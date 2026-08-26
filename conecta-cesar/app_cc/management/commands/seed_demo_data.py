import io
import random
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from PIL import Image
from rolepermissions.roles import assign_role

from app_cc.models import (
    Aluno,
    Atividade,
    AtividadeFeita,
    Aviso,
    Diario,
    Disciplina,
    Evento,
    Falta,
    File,
    Like,
    Nota,
    Post,
    Professor,
    ProfessorFile,
    Review,
    ToDoItem,
    ToDoList,
    Turma,
)
from app_cc.views import gerar_relatorio
from project_cc.roles import Aluno as AlunoRole, Professor as ProfessorRole

PROFESSORES = [
    ("ana.ferreira", "Ana Ferreira"),
    ("carlos.mendes", "Carlos Mendes"),
]

DISCIPLINAS = [
    ("Fundamentos de Software", "ana.ferreira"),
    ("Estrutura de Dados", "carlos.mendes"),
    ("Banco de Dados", "carlos.mendes"),
]

ALUNOS = [
    ("joao.silva", "João Silva", "Turma A"),
    ("maria.santos", "Maria Santos", "Turma A"),
    ("pedro.oliveira", "Pedro Oliveira", "Turma A"),
    ("julia.costa", "Julia Costa", "Turma B"),
    ("lucas.almeida", "Lucas Almeida", "Turma B"),
    ("beatriz.souza", "Beatriz Souza", "Turma B"),
]


def _png_file(name, size=(64, 64), color=(214, 80, 31)):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=name)


class Command(BaseCommand):
    help = (
        "Popula o banco com dados realistas de demonstração: professores, "
        "turmas, disciplinas, alunos, avisos, eventos, notas, faltas, "
        "diários, atividades, arquivos, fórum e to-do lists. Pensado pra "
        "deixar o site pronto pra mostrar, não pros testes do Cypress "
        "(esses continuam em seed_cypress_data)."
    )

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo_data only runs with DEBUG=True — it's meant for "
                "a demo deployment's initial data, not a real production DB."
            )

        try:
            self._seed()
        except IntegrityError as e:
            raise CommandError(
                f"Dados já existem (rode 'manage.py flush' pra limpar o "
                f"banco antes, se quiser recomeçar do zero): {e}"
            )

    def _seed(self):
        turmas = {nome: Turma.objects.create(nome=nome) for nome in ("Turma A", "Turma B")}

        professores = {}
        for username, nome_completo in PROFESSORES:
            first, last = nome_completo.split(" ", 1)
            user = User.objects.create_user(
                username=username,
                password="demo123",
                email=f"{username}@conectacesar.school",
                first_name=first,
                last_name=last,
            )
            assign_role(user, ProfessorRole)
            professor = Professor.objects.create(
                usuario=user,
                email=user.email,
                foto_perfil=_png_file(f"{username}.png", color=(31, 111, 214)),
            )
            professores[username] = professor

        disciplinas = {}
        for nome, prof_username in DISCIPLINAS:
            disciplina = Disciplina.objects.create(nome=nome, professor=professores[prof_username])
            disciplina.turmas.add(*turmas.values())
            disciplinas[nome] = disciplina

        alunos = {}
        for username, nome_completo, turma_nome in ALUNOS:
            first, last = nome_completo.split(" ", 1)
            user = User.objects.create_user(
                username=username,
                password="demo123",
                email=f"{username}@cesar.school",
                first_name=first,
                last_name=last,
            )
            assign_role(user, AlunoRole)
            # Note: Aluno.disciplinas is a dead ManyToManyField — a method
            # of the same name defined later in the model shadows it, so
            # it never got a real DB table (see app_cc/models.py). Which
            # disciplinas an aluno has actually flows through their turma,
            # already linked to every disciplina above.
            aluno = Aluno.objects.create(
                usuario=user,
                turma=turmas[turma_nome],
                email=user.email,
                foto_perfil=_png_file(f"{username}.png", color=(80, 160, 90)),
            )
            alunos[username] = aluno

        # Notas — a mix of good and below-passing (< 7) grades, so the
        # "alunos com nota abaixo" report has something to actually show.
        aluno_list = list(alunos.values())
        for disciplina in disciplinas.values():
            for i, aluno in enumerate(aluno_list):
                valor = round(random.uniform(4.0, 6.9), 1) if i % 3 == 0 else round(random.uniform(7.0, 10.0), 1)
                Nota.objects.create(aluno=aluno, disciplina=disciplina, valor=valor)

        # Faltas — a couple of students cross the 8-faltas threshold that
        # triggers the "frequência abaixo" report; most stay well under it.
        today = date.today()
        for i, aluno in enumerate(aluno_list):
            disciplina = list(disciplinas.values())[i % len(disciplinas)]
            num_faltas = 9 if i % 3 == 0 else random.randint(0, 4)
            for d in range(num_faltas):
                Falta.objects.create(
                    aluno=aluno,
                    disciplina=disciplina,
                    data=today - timedelta(days=d * 2),
                    justificada=(d % 4 == 0),
                )

        # Diários — a couple of entries per disciplina.
        for disciplina in disciplinas.values():
            for titulo, texto in [
                ("Aula 1 — Introdução", "Apresentação da disciplina, ementa e critérios de avaliação."),
                ("Aula 2 — Conceitos fundamentais", "Discussão dos principais conceitos e exercícios em sala."),
            ]:
                Diario.objects.create(disciplina=disciplina, titulo=titulo, texto=texto)

        # Avisos — a handful, one with a real image.
        avisos_conteudo = [
            ("Início do semestre", "As aulas começam na próxima segunda-feira. Fiquem atentos ao calendário.", True),
            ("Prazo de matrícula", "O prazo final para ajuste de matrícula é sexta-feira às 18h.", False),
            ("Semana de provas", "A semana de avaliações está confirmada para o mês que vem.", False),
        ]
        for titulo, corpo, com_imagem in avisos_conteudo:
            Aviso.objects.create(
                titulo=titulo,
                corpo=corpo,
                imagem=_png_file("aviso.png", color=(240, 112, 58)) if com_imagem else None,
            )

        # Eventos no calendário — um por disciplina, em datas futuras.
        for i, disciplina in enumerate(disciplinas.values()):
            Evento.objects.create(
                titulo=f"Avaliação — {disciplina.nome}",
                descricao="Avaliação valendo 40% da nota da unidade.",
                data=today + timedelta(days=7 * (i + 1)),
                horario="14:00",
                disciplina=disciplina,
                professor=disciplina.professor,
            )

        # Atividades — duas por disciplina; a primeira já com submissões de
        # metade da turma (algumas concluídas, outras ainda pendentes).
        for disciplina in disciplinas.values():
            turma = disciplina.turmas.first()
            atividade1 = Atividade.objects.create(
                turma=turma,
                professor=disciplina.professor,
                disciplina=disciplina,
                titulo=f"Exercício — {disciplina.nome}",
                texto="Resolva os exercícios do capítulo 1 e envie sua resposta.",
            )
            Atividade.objects.create(
                turma=turma,
                professor=disciplina.professor,
                disciplina=disciplina,
                titulo=f"Projeto final — {disciplina.nome}",
                texto="Projeto em grupo a ser entregue ao final do semestre.",
            )
            for aluno in [a for a in alunos.values() if a.turma == turma][:2]:
                AtividadeFeita.objects.create(
                    aluno=aluno,
                    atividade=atividade1,
                    conclusao=True,
                    arquivo=ContentFile(b"resposta do exercicio", name="resposta.txt"),
                )

        # Horas extras — arquivos de exemplo pra alguns alunos.
        for aluno in aluno_list[:3]:
            File.objects.create(
                title="Certificado de curso",
                archive=_png_file("certificado.png", color=(200, 200, 60)),
                aluno=aluno,
                horas_extras=round(random.uniform(2, 10), 1),
            )

        # Materiais do professor — um por disciplina.
        for disciplina in disciplinas.values():
            ProfessorFile.objects.create(
                professor=disciplina.professor,
                disciplina=disciplina,
                titulo=f"Slides — {disciplina.nome}",
                descricao="Material de apoio da primeira aula.",
                archive=ContentFile(b"%PDF-1.4 conteudo de exemplo", name="slides.pdf"),
            )

        # Ocorrências (Review) — uma por aluno em três, pra a lista de
        # ocorrências não ficar vazia sem exagerar.
        for aluno in aluno_list[:3]:
            Review.objects.create(
                aluno=aluno,
                title="Participação em sala",
                content="Aluno demonstrou ótima participação nas discussões em aula.",
            )

        # Fórum — alguns posts com curtidas cruzadas.
        posts = []
        for aluno in aluno_list[:3]:
            post = Post.objects.create(
                autor=aluno.usuario,
                titulo=f"Dúvida sobre a disciplina — {aluno.usuario.first_name}",
                corpo="Alguém pode me ajudar a entender melhor esse tópico da última aula?",
            )
            posts.append(post)
        for post in posts:
            for aluno in aluno_list:
                if aluno.usuario != post.autor and random.random() > 0.4:
                    Like.objects.get_or_create(usuario=aluno.usuario, post=post)

        # To-do list de exemplo pro primeiro aluno.
        primeiro_aluno = aluno_list[0]
        todo = ToDoList.objects.create(user=primeiro_aluno.usuario, title="Tarefas da semana")
        for content, priority, completed in [
            ("Revisar slides da aula 1", "low", True),
            ("Entregar exercício de Estrutura de Dados", "high", False),
            ("Estudar para a avaliação", "medium", False),
        ]:
            ToDoItem.objects.create(
                todo_list=todo, content=content, priority=priority, completed=completed
            )

        # Relatórios — reaproveita a lógica que já existe em app_cc.views,
        # em vez de duplicar a regra de "nota/frequência abaixo do esperado".
        # Note: professor.disciplinas is *also* shadowed — not by the same
        # bug as Aluno's, though: here it's Disciplina.professor's FK
        # related_name="disciplinas" clashing with Professor's own
        # disciplinas() method, and the reverse FK manager wins. Called as
        # a manager (.all()), not a method, since that's what's live.
        for professor in professores.values():
            gerar_relatorio(list(professor.disciplinas.all()), professor)

        self.stdout.write(self.style.SUCCESS(
            "Dados de demonstração criados: 2 professores, 2 turmas, 3 "
            "disciplinas, 6 alunos, e avisos/eventos/notas/faltas/diários/"
            "atividades/arquivos/fórum/to-do em cada um. Login: qualquer "
            "usuário acima, senha 'demo123'."
        ))
