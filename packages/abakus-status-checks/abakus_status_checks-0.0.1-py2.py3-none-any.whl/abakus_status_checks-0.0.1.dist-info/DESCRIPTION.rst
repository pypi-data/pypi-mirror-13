Abakus Status Checks
====================

.. image:: https://ci.frigg.io/eirsyl/abakus-status-checks.svg
    :target: https://ci.frigg.io/eirsyl/abakus-status-checks/last/
    :alt: Build Status

.. image:: https://ci.frigg.io/eirsyl/abakus-status-checks/coverage.svg
    :target: https://ci.frigg.io/eirsyl/abakus-status-checks/last/
    :alt: Coverage Status

This package is used together with Sensu_. Checks is managed with Puppet and reported to our #devops
channel on Slack.

Supported checks:

- CPU percent
- Load


Create a new check
------------------

- Create a new file in the abakus_checks/checks directory
- Import abakus_checks.utils.check.StatusCheck and use this as a base for your check.
- Give the check a name, decription and options

::

    name = 'load'
    description = 'Trigger errors based on load threshold. Load is divided by core count.'
    options = [
        click.option('--warning', default='2,1.5,1', type=str),
        click.option('--critical', default='3,2,1.5', type=str),
    ]

- Implement the run method. Call self.ok, self.warning, self.critical with a message based on the
result.

- Register the check in abakus_checks/cli.py. Import the check in the check import block and
register the check.

::

    from .checks import load
    register_check(load.LoadCheck)

- You can use the tests.test_case.CLITestCase to test the check. This TestCase has a .invoke
method you can use to call the check.

::

    class LoadCheckTestCase(CLITestCase):

        @mock.patch('os.getloadavg', return_value=(0, 0, 0))
        def test_load_ok(self, mock_loadavg):
            result = self.invoke(['load', '--warning /'3.2.1/''])
            self.assertEquals(result.exit_code, 0)

.. _Sensu: https://sensuapp.org/


