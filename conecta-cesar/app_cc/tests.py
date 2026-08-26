import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rolepermissions.roles import assign_role

from app_cc.models import Aluno, Atividade, AtividadeFeita, Disciplina, Professor, Turma
from app_cc.views import uploaded_file_content_is_valid
from project_cc.roles import Aluno as AlunoRole


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


def _make_aluno(username):
    user = User.objects.create_user(username=username, password='pw123456!')
    assign_role(user, AlunoRole)
    return Aluno.objects.create(usuario=user, email=f'{username}@test.com')


def _make_png_bytes():
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, format='PNG')
    return buffer.getvalue()


class AlunoAtividadeIntegrityTests(TestCase):
    """Regression test for a bug where completing an activity looked up
    an existing AtividadeFeita by atividade alone, so a second student's
    submission could silently steal/overwrite the first student's row."""

    def setUp(self):
        professor_user = User.objects.create_user(username='prof', password='pw123456!')
        professor = Professor.objects.create(usuario=professor_user)
        turma = Turma.objects.create(nome='Turma Teste')
        disciplina = Disciplina.objects.create(nome='Disciplina Teste', professor=professor)
        self.atividade = Atividade.objects.create(turma=turma, professor=professor, disciplina=disciplina)
        self.aluno1 = _make_aluno('aluno_a')
        self.aluno2 = _make_aluno('aluno_b')

    def _submit(self, aluno):
        self.client.force_login(aluno.usuario)
        arquivo = SimpleUploadedFile('resposta.txt', b'conteudo', content_type='text/plain')
        return self.client.post(
            reverse('aluno_atividade', args=[self.atividade.id]),
            {'arquivo': arquivo},
        )

    def test_two_students_get_independent_records(self):
        self._submit(self.aluno1)
        self._submit(self.aluno2)

        feita1 = AtividadeFeita.objects.get(atividade=self.atividade, aluno=self.aluno1)
        feita2 = AtividadeFeita.objects.get(atividade=self.atividade, aluno=self.aluno2)

        self.assertTrue(feita1.conclusao)
        self.assertTrue(feita2.conclusao)
        self.assertNotEqual(feita1.id, feita2.id)
        # The bug would reassign aluno1's row to aluno2 instead of creating
        # a second one — confirm aluno1's row is still theirs.
        self.assertEqual(
            AtividadeFeita.objects.filter(atividade=self.atividade).count(), 2
        )


class UploadedFileContentValidationTests(TestCase):
    def test_real_image_passes(self):
        f = SimpleUploadedFile('foto.png', _make_png_bytes(), content_type='image/png')
        self.assertTrue(uploaded_file_content_is_valid(f, '.png'))

    def test_non_image_with_image_extension_is_rejected(self):
        f = SimpleUploadedFile('foto.png', b'not actually a png', content_type='image/png')
        self.assertFalse(uploaded_file_content_is_valid(f, '.png'))

    def test_real_pdf_signature_passes(self):
        f = SimpleUploadedFile('doc.pdf', b'%PDF-1.4 rest of file', content_type='application/pdf')
        self.assertTrue(uploaded_file_content_is_valid(f, '.pdf'))

    def test_fake_pdf_is_rejected(self):
        f = SimpleUploadedFile('doc.pdf', b'not a real pdf', content_type='application/pdf')
        self.assertFalse(uploaded_file_content_is_valid(f, '.pdf'))
