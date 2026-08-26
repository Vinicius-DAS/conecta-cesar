from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from rolepermissions.roles import assign_role

from app_cc.models import (
    Aluno,
    Aviso,
    Diario,
    Disciplina,
    Evento,
    Falta,
    Nota,
    Professor,
    ProfessorFile,
    Turma,
)
from project_cc.roles import Aluno as AlunoRole
from project_cc.roles import Professor as ProfessorRole


class Command(BaseCommand):
    help = 'Cria dados de teste para Cypress: Professor, Turma, Disciplina e Aluno'

    def handle(self, *args, **kwargs):
        # This seeds professor1/aluno1/adm with the password "123", including
        # a superuser — never let it run anywhere DEBUG isn't explicitly on.
        if not settings.DEBUG:
            raise CommandError(
                "seed_cypress_data only runs with DEBUG=True — it creates "
                "throwaway accounts with the password '123', including a "
                "superuser. Refusing to run against what looks like a real "
                "deployment."
            )
        try:
            # Criação do usuário para o professor
            user_professor = User.objects.create_user(
                username='professor1', password='123', email='professor1@test.com'
            )

            # Criação do professor e associação ao usuário
            professor = Professor.objects.create(
                usuario=user_professor, ra='1234567890'
            )
            assign_role(user_professor, ProfessorRole)

            # Criação de uma turma
            turma = Turma.objects.create(nome='Turma 1')

            # Criação de uma disciplina e associação ao professor e à turma
            disciplina = Disciplina.objects.create(
                nome='Disciplina 1', professor=professor
            )
            disciplina.turmas.add(turma)

            # Criação de um aluno e associação à turma
            user_aluno = User.objects.create_user(
                username='aluno1', password='123', email='aluno1@test.com'
            )
            aluno = Aluno.objects.create(
                usuario=user_aluno, turma=turma, ra='0987654321'
            )
            assign_role(user_aluno, AlunoRole)

            # Criação de um diário
            Diario.objects.create(
                disciplina=disciplina, titulo="Título do Diário", texto="Descrição do Diário"
            )

            # Criação de uma nota para o aluno
            Nota.objects.create(
                aluno=aluno, disciplina=disciplina, valor=6.0
            )

            # Adição de 8 faltas para o aluno em diferentes dias
            base_date = date.today()
            for i in range(9):#Faltas o suficiente para o aluno entrar pro relatório de desempenho
                falta_date = base_date - timedelta(days=i)
                Falta.objects.create(
                    aluno=aluno, data=falta_date, justificada=False, disciplina=disciplina
                )

            User.objects.create_superuser(
                username='adm', password='123', email='adm@test.com'
            )

            Aviso.objects.create(
                titulo = "E2E aviso",
                corpo = "testes automatizados"
            )

            Evento.objects.create(
                titulo = "titulo",
                descricao = "evento e2e",
                horario = "12:30",
                disciplina = disciplina,
                professor = professor,
                data = date.today()
            )
            ProfessorFile.objects.create(
                 professor=professor,
                disciplina=disciplina,
                titulo='titulo',
                descricao = 'slide e2e',
            )

            self.stdout.write(self.style.SUCCESS('Dados de teste criados com sucesso: Professor, Turma, Disciplina, Aluno, Diário, Nota , Aviso, Evento, Faltas,  Slides e Superusuário'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Erro de integridade, os seguintes dados já existem no banco de dados: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar dados de teste: {str(e)}'))
