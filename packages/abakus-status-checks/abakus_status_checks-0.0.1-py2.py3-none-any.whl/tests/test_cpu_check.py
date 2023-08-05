import mock

from .test_case import CLITestCase


class CPUCheckTestCase(CLITestCase):

    @mock.patch('psutil.cpu_percent', return_value=10)
    def test_cli_ok(self, mock_cpu_percent):

        result = self.invoke(['cpu'])
        self.assertEquals(result.exit_code, 0)

    @mock.patch('psutil.cpu_percent', return_value=75)
    def test_cli_warning(self, mock_cpu_percent):

        result = self.invoke(['cpu'])
        self.assertEquals(result.exit_code, 1)

    @mock.patch('psutil.cpu_percent', return_value=95)
    def test_cli_critical(self, mock_cpu_percent):

        result = self.invoke(['cpu'])
        self.assertEquals(result.exit_code, 2)

    @mock.patch('psutil.cpu_percent', return_value=[10, 50, 75])
    def test_cli_per_cpu_warning(self, mock_cpu_percent):

        result = self.invoke(['cpu', '--per-cpu'])
        self.assertEquals(result.exit_code, 1)
