from qgispluginreleaser.entry_point import create_zipfile
from qgispluginreleaser.entry_point import prerequisites_ok
from unittest import TestCase

import mock
import pkg_resources


class InstallationTestCase(TestCase):

    def test_entry_point_available(self):
        entry_points = list(pkg_resources.iter_entry_points(
            group='zest.releaser.releaser.after_checkout'))
        self.assertTrue('qgispluginreleaser.entry_point' in str(entry_points))

    def test_prerequisites_ok(self):
        # Should return false for us.
        self.assertFalse(prerequisites_ok())

    def test_stops_if_prerequisites_wrong(self):
        # Should return false for us.
        self.assertFalse(create_zipfile({}))


def return_ok():
    return True


class EntryPointTestCase(TestCase):

    def setUp(self):
        self.patcher = mock.patch(
            'qgispluginreleaser.entry_point.prerequisites_ok',
            return_ok)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_makefile_call(self):
        with mock.patch('subprocess.call') as mocked:
            create_zipfile({})
            self.assertTrue(mocked.called)

    def test_ziprename(self):

        def mock_glob(something):
            return ['something.zip']

        with mock.patch('subprocess.call'):
            with mock.patch('glob.glob', mock_glob):
                with mock.patch('shutil.copy') as mocked:
                    create_zipfile({'version': '1.0',
                         'workingdir': '/tmp'})
                    mocked.assert_called_with(
                        'something.zip',
                        '/tmp/something.1.0.zip')
