from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError


class SeedCypressDataCommandTests(TestCase):
    @override_settings(DEBUG=False)
    def test_seed_command_refuses_to_run_without_debug(self):
        """seed_cypress_data creates a superuser and other accounts with
        the password "123" — it must never run outside local dev."""
        with self.assertRaises(CommandError):
            call_command('seed_cypress_data')

    @override_settings(DEBUG=False)
    def test_delete_command_refuses_to_run_without_debug(self):
        with self.assertRaises(CommandError):
            call_command('delete_cypress_data')
