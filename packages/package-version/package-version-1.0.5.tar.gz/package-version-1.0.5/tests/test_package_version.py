import unittest
import subprocess
import semantic_version
from package_version import PackageVersion
from future import standard_library
standard_library.install_aliases()
from flexmock import flexmock


class VersionsTestCase(unittest.TestCase):

    def setUp(self):
        output = 'pip 1.5.3 from /virtualenv/lib/python3.5/site-packages (python 3.5)'
        flexmock(PackageVersion).should_receive('_run_shell_command').with_args('pip --version').and_return(output)
        self._mock_version_list(['1.1.3', '1.1.4', '1.2', '1.8', '1.8.6', '1.9a1', '1.9b1'])

    def test_old_pip_version_raise_exception(self):
        out = 'pip 1.0.0 from /virtualenv/lib/python3.5/site-packages (python 3.5)'
        flexmock(PackageVersion).should_receive('_run_shell_command').with_args('pip --version').and_return(out).once()

        pv = PackageVersion()
        self.assertRaises(RuntimeError, lambda: pv.get_all('Django'))

    def test_all_versions_returned_correctly(self):
        out = (
            "Collecting Django==invalid\n" +
            "  Could not find a version that satisfies the requirement Django==invalid (from versions: " +
            "1.1.3, 1.1.4, 1.2, 1.8, 1.8.6, 1.9a1, 1.9b1)\n" +
            "No matching distribution found for Django==invalid"
        )
        flexmock(PackageVersion).should_receive('_run_shell_command').with_args('pip install Django==invalid').and_return(out).once()

        pv = PackageVersion()
        versions = pv.get_all('Django')
        self.assertEqual(['1.1.3', '1.1.4', '1.2', '1.8', '1.8.6', '1.9a1', '1.9b1'], versions)

    def test_latest_version_returned_as_expected(self):
        self._mock_version_list(['1.1.3', '1.1.4', '1.2', '1.8', '1.8.6', '1.9a1', '1.9b1'])
        pv = PackageVersion()
        latest = pv.get_latest('Django')
        self.assertEqual(str(semantic_version.Version.coerce('1.9b1', partial=True)), latest)
        self._mock_version_list([], 'Flask')
        latest = pv.get_latest('Flask')
        self.assertEqual('0.0.0-na', latest)

    def test_generate_new_patch_version_returns_expected_value(self):
        self._mock_version_list(['1.1.3', '1.1.4', '1.2', '1.8', '1.8.6', '1.9a1', '1.9b1'])
        pv = PackageVersion()
        next_version = pv.generate_next_stable('Django')
        self.assertEqual('1.9', next_version)
        self._mock_version_list(['1'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('1.0.1', next_version)
        self._mock_version_list(['1.0'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('1.0.1', next_version)
        self._mock_version_list(['0'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('0.0.1', next_version)
        self._mock_version_list([], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('0.0.1', next_version)
        self._mock_version_list(['1.9-a2'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('1.9', next_version)
        self._mock_version_list(['1.9'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('1.9.1', next_version)
        self._mock_version_list(['1-a2'], 'Flask')
        next_version = pv.generate_next_stable('Flask')
        self.assertEqual('1', next_version)

    def _mock_version_list(self, version_list, package_name='Django'):
        version_string = ", ".join(version_list)
        output = (
            'Collecting '+package_name+'==invalid'+"\n" +
            '  Could not find a version that satisfies the requirement '+package_name+'==invalid (from versions: ' +
            version_string+')' + "\n" +
            'No matching distribution found for '+package_name+'==invalid'
        )

        flexmock(PackageVersion).should_receive('_run_shell_command').with_args(
            'pip install '+package_name+'==invalid').and_return(output)
