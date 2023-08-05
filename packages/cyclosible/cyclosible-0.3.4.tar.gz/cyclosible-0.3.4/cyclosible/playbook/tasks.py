from django.contrib.auth.models import User
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone
from stevedore import enabled, driver
from ..Cyclosible.celery import app
from .models import Playbook
from .plugins.storage.base import check_plugin_enabled
from .callbacks_ansiblev1 import PlaybookCallbacks, PlaybookRunnerCallbacks, display
from .models import PlaybookRunHistory
from ansible import errors
from ansible import callbacks
from ansible import utils
from ansible.inventory import Inventory
from ansible.color import ANSIBLE_COLOR, stringc
import json
import ansible.playbook
import ansible.utils.template

logger = get_task_logger(__name__)


def colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    if num != 0 and ANSIBLE_COLOR and color is not None:
        return "%s%s%-15s" % (stringc(lead, color), stringc("=", color), stringc(str(num), color))
    else:
        return "%s=%-4s" % (lead, str(num))


def hostcolor(host, stats, color=True):
    if ANSIBLE_COLOR and color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return "%-37s" % stringc(host, 'red')
        elif stats['changed'] != 0:
            return "%-37s" % stringc(host, 'yellow')
        else:
            return "%-37s" % stringc(host, 'green')
    return "%-26s" % host


@app.task(bind=True, name="Run a playbook")
def run_playbook(self, playbook_name, user_name, only_tags=None, skip_tags=None, extra_vars=None, subset=None):
    """ This function will launch a playbook. To handle logging, it will
    use stevedore which will load all extensions registered under the
    entrypoint cyclosible.plugins.storage. For example, it will let Cyclosible
    save his log on a file, on S3, or something else.
    :param playbook_name:
    :param user_name:
    :param only_tags:
    :param skip_tags:
    :param extra_vars:
    :return:
    """
    history = PlaybookRunHistory.objects.create(
        playbook=Playbook.objects.get(name=playbook_name),
        date_launched=timezone.now(),
        status='RUNNING',
        task_id=self.request.id,
        launched_by=User.objects.get(username=user_name)
    )

    vault_password = None
    if settings.VAULT_ENABLED:
        try:
            self.mgr_vault = driver.DriverManager(
                namespace='cyclosible.plugins.vault',
                name=settings.VAULT_ENABLED,
                invoke_on_load=True,
            )
            vault_password = self.mgr_vault.driver.get_password()
        except RuntimeError as e:
            logger.error(e)

        logger.debug('LOADED VAULT: {plugins} | Status: {status}'.format(
            plugins=settings.VAULT_ENABLED,
            status='OK' if vault_password else 'KO'
        ))

    inventory = Inventory(vault_password=vault_password)

    # Here, we override the default ansible callbacks to pass our customs parameters
    stats = callbacks.AggregateStats()
    playbook_cb = PlaybookCallbacks(
        verbose=utils.VERBOSITY,
        task_id=self.request.id
    )
    runner_cb = PlaybookRunnerCallbacks(
        stats=stats,
        verbose=utils.VERBOSITY,
        task_id=self.request.id
    )

    pb = ansible.playbook.PlayBook(
        playbook=''.join([settings.PLAYBOOK_PATH, playbook_name, '.yml']),
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        inventory=inventory,
        stats=stats,
        extra_vars=extra_vars,
        only_tags=only_tags,
        skip_tags=skip_tags,
        vault_password=vault_password,
        subset=subset
    )

    try:
        pb.run()
        hosts = sorted(pb.stats.processed.keys())
        logger.info(hosts)
        playbook_cb.on_stats(pb.stats)
        history.status = 'SUCCESS'
        for h in hosts:
            t = pb.stats.summarize(h)

            display("%s : %s %s %s %s" % (
                hostcolor(h, t),
                colorize('ok', t['ok'], 'green'),
                colorize('changed', t['changed'], 'yellow'),
                colorize('unreachable', t['unreachable'], 'red'),
                colorize('failed', t['failures'], 'red')),
                task_id=self.request.id
            )
    except errors.AnsibleError as e:
        history.status = 'FAILED'
        display(u"ERROR: %s" % e, task_id=self.request.id)
        logger.error(u"ERROR: %s" % e)

    try:
        self.mgr_storage = enabled.EnabledExtensionManager(
            namespace='cyclosible.plugins.storage',
            check_func=check_plugin_enabled,
            invoke_on_load=True,
            invoke_kwds={'task_id': self.request.id},
            verify_requirements=True
        )

        logger.debug('LOADED STORAGE: {plugins}'.format(plugins=', '.join(self.mgr_storage.names())))
    except RuntimeError as e:
        logger.error(e)

    try:
        list_urls = []
        self.mgr_storage.map(lambda ext: (ext.name, ext.obj.write_log()))
        urls = self.mgr_storage.map(lambda ext: (ext.name, ext.obj.get_url_log()))
        for url in urls:
            try:
                if url[1]:
                    list_urls.append({url[0]: url[1]})
            except IndexError:
                logger.debug('Index does not exist in the url returned')
        history.log_url = json.dumps(list_urls)
    except RuntimeError:
        logger.debug('No plugins available')
    history.date_finished = timezone.now()
    history.save()
    if history.status == 'FAILED':
        return 1
