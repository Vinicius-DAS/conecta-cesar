from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from project_cc.roles import Professor, Aluno


class CadastroTests(TestCase):
    def test_public_registration_ignores_user_type_professor(self):
        """Public self-registration must only ever create aluno accounts,
        even if user_type=professor is sent in the request — there's no
        approval step here, so letting visitors grant themselves professor
        access would be a privilege escalation."""
        self.client.post(reverse('cadastro'), {
            'username': 'sneaky_prof',
            'email': 'sneaky@test.com',
            'senha': 'Xk9#mP2vLq!7Rt',
            'user_type': 'professor',
        })

        user = User.objects.get(username='sneaky_prof')
        self.assertTrue(has_role(user, Aluno))
        self.assertFalse(has_role(user, Professor))
        self.assertFalse(hasattr(user, 'professor'))

    def test_weak_password_is_rejected(self):
        self.client.post(reverse('cadastro'), {
            'username': 'weakpass_user',
            'email': 'weak@test.com',
            'senha': '12345678',
        })
        self.assertFalse(User.objects.filter(username='weakpass_user').exists())
