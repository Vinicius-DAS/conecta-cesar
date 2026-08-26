from django.contrib import admin

from app_cc.models import (
    Aluno,
    Atividade,
    AtividadeFeita,
    Aviso,
    Diario,
    Disciplina,
    Evento,
    Falta,
    FaltaRelatorio,
    File,
    Like,
    Nota,
    NotaRelatorio,
    Post,
    Professor,
    ProfessorFile,
    Relatorio,
    Review,
    ToDoItem,
    ToDoList,
    Turma,
)

# Register your models here.
admin.site.register(Professor)
admin.site.register(Nota)
admin.site.register(Disciplina)
admin.site.register(Diario)
admin.site.register(Turma)
admin.site.register(Aluno)
admin.site.register(Falta)
admin.site.register(Evento)
admin.site.register(Aviso)
admin.site.register(Review)
admin.site.register(Post)
admin.site.register(Relatorio)
admin.site.register(FaltaRelatorio)
admin.site.register(NotaRelatorio)
admin.site.register(ProfessorFile)
admin.site.register(Atividade)
admin.site.register(AtividadeFeita)
admin.site.register(File)
admin.site.register(ToDoList)
admin.site.register(ToDoItem)
admin.site.register(Like)
