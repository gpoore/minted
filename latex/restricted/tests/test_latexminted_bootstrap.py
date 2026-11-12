# -*- coding: utf-8 -*-
import ast
import contextlib
import email.parser
import io
import importlib.metadata
import pathlib
import re
import sys
import tempfile
import unittest
import zipfile
from email.message import EmailMessage
from unittest.mock import Mock


# Load only the standard-library bootstrap definitions from the launcher.
# Importing latexminted.py itself would execute the launcher and application.
_launcher_path = pathlib.Path(__file__).resolve().parents[1] / 'latexminted.py'
_launcher_tree = ast.parse(_launcher_path.read_text(encoding='utf-8'))
_bootstrap_names = {
    '_version_key',
    '_wheel_distribution_version',
    'local_pygments_is_compatible',
}
_bootstrap_nodes = [
    node for node in _launcher_tree.body
    if (
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in _bootstrap_names
    ) or (
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == '_VERSION_RE'
            for target in node.targets
        )
    )
]
_bootstrap_namespace = {
    'email': email,
    'importlib': importlib,
    're': re,
    'sys': sys,
    'zipfile': zipfile,
}
exec(compile(
    ast.Module(body=_bootstrap_nodes, type_ignores=[]),
    str(_launcher_path),
    'exec',
), _bootstrap_namespace)

_version_key = _bootstrap_namespace['_version_key']
local_pygments_is_compatible = _bootstrap_namespace['local_pygments_is_compatible']


class VersionComparisonTests(unittest.TestCase):
    def test_release_versions(self):
        self.assertGreater(_version_key('2.18.0'), _version_key('2.17.0'))
        self.assertEqual(_version_key('2.17.0'), _version_key('2.17'))

    def test_prerelease_order(self):
        self.assertLess(_version_key('2.18.0rc1'), _version_key('2.18.0'))
        self.assertLess(_version_key('2.18.0.dev1'), _version_key('2.18.0a1'))


class LocalPygmentsTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.wheel_path = pathlib.Path(self.tempdir.name) / 'Pygments-2.17.0-py3-none-any.whl'
        metadata = EmailMessage()
        metadata['Name'] = 'Pygments'
        metadata['Version'] = '2.17.0'
        with zipfile.ZipFile(self.wheel_path, 'w') as wheel:
            wheel.writestr('pygments-2.17.0.dist-info/METADATA', metadata.as_string())

    def finder(self, distributions):
        def find(name):
            if name not in distributions:
                raise LookupError(name)
            return distributions[name]
        return find

    def distribution(self, version):
        return Mock(version=version)

    def test_equal_local_version_is_accepted(self):
        distributions = {'Pygments': self.distribution('2.17.0')}
        self.assertTrue(local_pygments_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_newer_local_version_is_accepted(self):
        distributions = {'Pygments': self.distribution('2.18.0')}
        self.assertTrue(local_pygments_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_older_local_version_falls_back(self):
        distributions = {'Pygments': self.distribution('2.16.9')}
        self.assertFalse(local_pygments_is_compatible(
            [self.wheel_path], distribution_finder=self.finder(distributions)
        ))

    def test_missing_local_pygments_falls_back(self):
        self.assertFalse(local_pygments_is_compatible(
            [self.wheel_path], distribution_finder=self.finder({})
        ))

    def test_missing_bundled_pygments_wheel_falls_back(self):
        self.assertFalse(local_pygments_is_compatible(
            [], distribution_finder=self.finder({'Pygments': self.distribution('2.18.0')})
        ))

    def test_unreadable_metadata_falls_back(self):
        def broken_finder(name):
            raise RuntimeError('metadata unavailable')
        self.assertFalse(local_pygments_is_compatible(
            [self.wheel_path], distribution_finder=broken_finder
        ))

    def test_malformed_bundled_metadata_falls_back(self):
        malformed_wheel = pathlib.Path(self.tempdir.name) / 'Pygments-malformed.whl'
        with zipfile.ZipFile(malformed_wheel, 'w') as wheel:
            wheel.writestr('pygments.dist-info/METADATA', 'not valid metadata')
        distributions = {'Pygments': self.distribution('2.18.0')}
        self.assertFalse(local_pygments_is_compatible(
            [malformed_wheel], distribution_finder=self.finder(distributions)
        ))

    def test_debug_reports_selected_source(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            selected = local_pygments_is_compatible(
                [self.wheel_path],
                debug=True,
                distribution_finder=self.finder({'Pygments': self.distribution('2.18.0')}),
            )
        self.assertTrue(selected)
        self.assertIn('using local Pygments', stderr.getvalue())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            selected = local_pygments_is_compatible(
                [self.wheel_path],
                debug=True,
                distribution_finder=self.finder({'Pygments': self.distribution('2.16.9')}),
            )
        self.assertFalse(selected)
        self.assertIn('using bundled Pygments', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
