import os

import click
import psutil

from abakus_checks.utils.check import StatusCheck


class LoadCheck(StatusCheck):

    name = 'load'
    description = 'Trigger errors based on load threshold. Load is divided by core count.'
    options = [
        click.option('--warning', default='2,1.5,1', type=str),
        click.option('--critical', default='3,2,1.5', type=str),
    ]

    def run(self):
        load = list(os.getloadavg())
        cores = psutil.cpu_count()

        warning_thresholds = self.arguments['warning'].split(',')
        critical_thresholds = self.arguments['critical'].split(',')

        assert len(warning_thresholds) == 3, 'The warning threshold needs to me a string of ' \
                                             'three floats separated by ,.'
        assert len(critical_thresholds) == 3, 'The critical threshold needs to me a string of ' \
                                              'three floats separated by ,.'

        warning_thresholds = list(map(float, warning_thresholds))
        critical_thresholds = list(map(float, critical_thresholds))
        load = list(map(lambda x: float(x)/cores, load))

        if load[0] >= critical_thresholds[0] or load[1] >= critical_thresholds[1] or load[2] >= \
                critical_thresholds[2]:
            self.critical('%s load is higher than the critical threshold ' % str(load))
        elif load[0] >= warning_thresholds[0] or load[1] >= warning_thresholds[1] or load[2] >= \
                warning_thresholds[2]:
            self.warning('%s load is higher than the warning threshold ' % str(load))

        self.ok('Load is okay!')
