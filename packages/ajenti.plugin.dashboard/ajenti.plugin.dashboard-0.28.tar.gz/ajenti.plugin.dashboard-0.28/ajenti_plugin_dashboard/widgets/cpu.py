import multiprocessing
import psutil
from jadi import component

from aj.plugins.dashboard.api import Widget


@component(Widget)
class CPUWidget(Widget):
    id = 'cpu'
    name = _('CPU usage')
    template = '/dashboard:resources/partial/widgets/cpu.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        k = 0.01
        if config and config.get('divide', False):
            k /= multiprocessing.cpu_count()
        return [x * k for x in psutil.cpu_percent(interval=0, percpu=True)]
