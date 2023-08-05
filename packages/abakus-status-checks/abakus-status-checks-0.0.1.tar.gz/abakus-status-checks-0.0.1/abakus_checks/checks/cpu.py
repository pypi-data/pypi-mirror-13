import click
import psutil

from abakus_checks.utils.check import StatusCheck


class CPUCheck(StatusCheck):

    name = 'cpu'
    description = 'Trigger errors based on cpu threshold.'
    options = [
        click.option('--warning', default=70, type=int),
        click.option('--critical', default=90, type=int),
        click.option('--per-cpu', default=False, is_flag=True)
    ]

    def run(self):
        per_cpu = self.arguments['per_cpu']
        warning_threshold = self.arguments['warning']
        critical_threshold = self.arguments['critical']
        cpu_percent = psutil.cpu_percent(interval=1, percpu=per_cpu)

        def check_percent(percent):
            if percent >= critical_threshold:
                self.critical('%s is greater than %s' % (percent, critical_threshold))
            elif percent >= warning_threshold:
                self.warning('%s is greater than %s' % (percent, warning_threshold))

        if per_cpu:
            for percent in cpu_percent:
                check_percent(percent)
        else:
            check_percent(cpu_percent)

        self.ok('cpu usage is okay!')
