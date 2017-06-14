from unittest import TestCase
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from services_lib.click import CiTools, build_soocii_cli


class CiToolsTestCases(TestCase):
    def test_command_call_methods(self):
        """Test if soocii_cli call CiTools' methods"""
        runner = CliRunner()

        tools = CiTools('test')

        test_methods = ['docker_login', 'build', 'build_and_push', 'deploy_to_integ']
        for m in test_methods:
            setattr(tools, m, MagicMock(name=m))

        cli = build_soocii_cli(tools)
        runner.invoke(cli, [m.replace('_', '-') for m in test_methods])

        for m in test_methods:
            getattr(tools, m).assert_called_with()


class FunctionsTestCases(TestCase):
    def test_build_soocii_cli_instance_type_check(self):
        with pytest.raises(ValueError):
            non_ci_tools_instance = list()
            build_soocii_cli(non_ci_tools_instance)
