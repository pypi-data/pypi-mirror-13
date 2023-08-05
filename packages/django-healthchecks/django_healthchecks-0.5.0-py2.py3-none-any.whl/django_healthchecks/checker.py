from importlib import import_module

from django.conf import settings
from six import iteritems

try:
    from django.utils.module_loading import import_string
except ImportError:
    def import_string(value):
        module_name, func_name = value.rsplit('.', 1)
        module = import_module(module_name)
        return getattr(module, func_name)


def create_report():
    """Run all checks and return a tuple containing results and boolea to
    indicate to indicate if all things are healthy.

    """
    report = {}
    has_error = False

    checks = _get_registered_health_checks()
    for service, func_string in iteritems(checks):
        check_func = import_string(func_string)
        report[service] = check_func() or False

        if not report[service]:
            has_error = True
    return report, not has_error


def create_service_result(service):
    func_string = _get_registered_health_checks().get(service)
    if not func_string:
        return

    check_func = import_string(func_string)
    return check_func() or False


def _get_registered_health_checks():
    return getattr(settings, 'HEALTH_CHECKS', {})
