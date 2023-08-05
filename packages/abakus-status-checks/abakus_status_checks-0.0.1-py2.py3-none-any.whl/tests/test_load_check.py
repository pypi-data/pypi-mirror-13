import mock

from .test_case import CLITestCase


class LoadCheckTestCase(CLITestCase):

    @mock.patch('os.getloadavg', return_value=(0, 0, 0))
    def test_load_ok(self, mock_loadavg):
        result = self.invoke(['load'])
        self.assertEquals(result.exit_code, 0)

    @mock.patch('psutil.cpu_count', return_value=1)
    @mock.patch('os.getloadavg', return_value=(2.5, 0, 0))
    def test_load_warning(self, mock_loadavg, mock_cpu_cores):
        result = self.invoke(['load'])
        self.assertEquals(result.exit_code, 1)

    @mock.patch('psutil.cpu_count', return_value=1)
    @mock.patch('os.getloadavg', return_value=(3.5, 0, 0))
    def test_load_critical(self, mock_loadavg, mock_cpu_cores):
        result = self.invoke(['load'])
        self.assertEquals(result.exit_code, 2)
