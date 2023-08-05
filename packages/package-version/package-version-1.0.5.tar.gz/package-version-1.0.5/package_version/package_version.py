import subprocess
import semantic_version
import re


class PackageVersion:

    def get_all(self, package_name):
        self._check_pip_version()
        try:
            out = self._run_shell_command('pip install ' + package_name + '==invalid')
        except subprocess.CalledProcessError as e:
            if e.returncode != 1:
                raise
            out = e.output

        m = re.search('from versions: ([^\)]*)\)', str(out))
        if m is None:
            return []
        versions_string = m.group(1)
        version_list = versions_string.split(', ')
        return version_list

    def get_latest(self, package_name):
        version_list = self.get_all(package_name)
        latest_version = semantic_version.Version('0.0.0-na')
        for v in version_list:
            if not v:
                continue
            sv = semantic_version.Version.coerce(v, partial=True)
            if sv > latest_version:
                latest_version = sv
        return str(latest_version)

    def generate_next_stable(self, package_name):
        v = self.get_latest(package_name)
        version = semantic_version.Version.coerce(v, partial=True)

        major = 0 if version.major is None else version.major
        minor = version.minor
        if minor is None:
            minor = 0
            if version.prerelease is None:
                if major == 0:
                    return "%d.%d" % (major, minor)  # version 0 -> 0.1
                return "%d.%d.1" % (major, minor)  # version 1 -> 1.0.1
            return "%d" % major  # version 1a2 -> 1

        if version.patch is None and minor > 0:
            if version.prerelease is None:
                return "%d.%d.%d" % (major, minor, 1)  # version 1.0 -> 1.0.1
            return "%d.%d" % (major, minor)  # version 1.0a2 -> 1.0

        patch = 1 if version.patch is None else version.patch+1
        return "%d.%d.%d" % (major, minor, patch)  # version 1.0.1 -> 1.0.2

    def _check_pip_version(self):
        out = self._run_shell_command('pip --version')
        m = re.search('pip\s+([^\s]+)', str(out))
        version_text = m.group(1)
        version = semantic_version.Version(version_text)
        if semantic_version.Version('1.0.0') >= version:
            raise RuntimeError('Only pip versions larger than 1.0.0 is supported')

    def _run_shell_command(self, command):
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        output = process.communicate()[0]

        if process.returncode:
            raise subprocess.CalledProcessError(process.returncode, command, output)

        return output