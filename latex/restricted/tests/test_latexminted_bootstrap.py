# -*- coding: utf-8 -*-
# ruff: noqa: E402

import pathlib
import sys
import tempfile
import unittest
import zipfile
from email.message import EmailMessage
from unittest.mock import Mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from latexminted_bootstrap import (
    _satisfies_specifier,
    _version_key,
    local_installation_is_compatible,
)


class VersionComparisonTests(unittest.TestCase):
    def test_release_versions(self):
        self.assertGreater(_version_key('0.7.2'), _version_key('0.7.1'))
        self.assertEqual(_version_key('0.7.1'), _version_key('0.7.1.0'))

    def test_prerelease_order(self):
        self.assertLess(_version_key('1.0rc1'), _version_key('1.0'))
        self.assertLess(_version_key('1.0.dev1'), _version_key('1.0a1'))

    def test_specifiers(self):
        self.assertTrue(_satisfies_specifier('2.0', '>=1.5, <3.0'))
        self.assertFalse(_satisfies_specifier('1.4', '>=1.5'))
        self.assertFalse(_satisfies_specifier('1.0', '~=1.0'))


class LocalInstallationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.wheel_path = pathlib.Path(self.tempdir.name) / 'latexminted-0.7.1-py3-none-any.whl'
        metadata = EmailMessage()
        metadata['Name'] = 'latexminted'
        metadata['Version'] = '0.7.1'
        with zipfile.ZipFile(self.wheel_path, 'w') as wheel:
            wheel.writestr('latexminted-0.7.1.dist-info/METADATA', metadata.as_string())

    def finder(self, distributions):
        def find(name):
            if name not in distributions:
                raise LookupError(name)
            return distributions[name]
        return find

    def distribution(self, version, requires=None):
        return Mock(version=version, requires=requires)

    def test_compatible_local_installation(self):
        distributions = {
            'latexminted': self.distribution('0.7.2', [
                'latex2pydata >= 0.5.0', 'latexrestricted >= 0.6.2', 'Pygments >= 2.17.0',
            ]),
            'latex2pydata': self.distribution('0.5.0'),
            'latexrestricted': self.distribution('0.6.2'),
            'Pygments': self.distribution('2.17.0'),
        }
        self.assertTrue(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_equal_latexminted_version_is_accepted(self):
        distributions = {
            'latexminted': self.distribution('0.7.1', [
                'latex2pydata >= 0.5.0', 'latexrestricted >= 0.6.2', 'Pygments >= 2.17.0',
            ]),
            'latex2pydata': self.distribution('0.5.0'),
            'latexrestricted': self.distribution('0.6.2'),
            'Pygments': self.distribution('2.17.0'),
        }
        self.assertTrue(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_missing_latexminted_falls_back(self):
        self.assertFalse(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder({})
        ))

    def test_malformed_wheel_metadata_falls_back(self):
        malformed_wheel = pathlib.Path(self.tempdir.name) / 'latexminted-malformed.whl'
        with zipfile.ZipFile(malformed_wheel, 'w') as wheel:
            wheel.writestr('latexminted.dist-info/METADATA', 'not valid metadata')
        self.assertFalse(local_installation_is_compatible(
            [malformed_wheel], distribution_finder=self.finder({})
        ))

    def test_older_latexminted_falls_back(self):
        distributions = {'latexminted': self.distribution('0.7.0', [])}
        self.assertFalse(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_missing_direct_dependency_falls_back(self):
        distributions = {
            'latexminted': self.distribution('0.7.1', ['latex2pydata >= 0.5.0']),
        }
        self.assertFalse(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_incompatible_direct_dependency_falls_back(self):
        distributions = {
            'latexminted': self.distribution('0.7.1', ['latex2pydata >= 0.5.0']),
            'latex2pydata': self.distribution('0.4.9'),
        }
        self.assertFalse(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_unreadable_metadata_falls_back(self):
        def broken_finder(name):
            raise RuntimeError('metadata unavailable')
        self.assertFalse(local_installation_is_compatible(
            [self.wheel_path], distribution_finder=broken_finder
        ))


if __name__ == '__main__':
    unittest.main()
