from django.contrib import admin
from .models import Andar, Curso, Sala, SemestrePeriodo

# Register your models here.

@admin.register(SemestrePeriodo)
class SemestrePeriodoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data_inicio', 'data_fim', 'ativo', 'esta_ativo')
    list_filter = ('ano', 'periodo', 'ativo')
    search_fields = ('ano',)
    date_hierarchy = 'data_inicio'
    ordering = ['-ano', '-periodo']

@admin.register(Andar)
class AndarAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome')
    search_fields = ('numero', 'nome')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'semestre', 'turma', 'alunos', 'semestre_periodo')
    list_filter = ('semestre', 'turma', 'semestre_periodo')
    search_fields = ('nome',)

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'curso', 'andar', 'lugares', 'tem_lugares_livres')
    list_filter = ('andar', 'curso', 'curso__semestre_periodo')
    search_fields = ('nome', 'curso__nome')