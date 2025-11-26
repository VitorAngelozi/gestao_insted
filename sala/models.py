from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

SEMESTRE = [
    ("1", "1°"),
    ("2", "2°"),
    ("3", "3°"),
    ("4", "4°"),
    ("5", "5°"),
    ("6", "6°"),
    ("7", "7°"),
    ("8", "8°"),
    ("9", "9°"),
    ("10", "10°"),
    ("11", "11°"),
    ("12", "12°"),
]
TURMA = [
    ("1", "1"),
    ("2", "2"),
]

PERIODO_CHOICES = [
    ("1", "1"),
    ("2", "2"),
]

METODOLOGIA_CHOICES = [
    ("ativa", "Metodologia Ativa"),
    ("tradicional", "Metodologia Tradicional"),
]


class SemestrePeriodo(models.Model):
    ano = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    periodo = models.CharField(max_length=1, choices=PERIODO_CHOICES)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(
        default=True, help_text="Indica se este período está ativo"
    )

    class Meta:
        unique_together = ["ano", "periodo"]
        ordering = ["-ano", "-periodo"]
        verbose_name = "Semestre Período"
        verbose_name_plural = "Semestres Períodos"

    def __str__(self):
        return f"{self.ano}.{self.periodo}"

    def esta_ativo(self):
        """Verifica se o período está dentro das datas"""
        from django.utils import timezone

        hoje = timezone.now().date()
        return self.data_inicio <= hoje <= self.data_fim


class Andar(models.Model):
    numero = models.IntegerField(unique=True)
    nome = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.nome:
            return f"{self.numero}° Andar - {self.nome}"
        return f"{self.numero}° Andar"

    class Meta:
        ordering = ["numero"]


class Curso(models.Model):
    nome = models.CharField(max_length=100)
    semestre = models.CharField(max_length=2, choices=SEMESTRE)
    turma = models.CharField(max_length=1, choices=TURMA)
    alunos = models.IntegerField(default=0)
    semestre_periodo = models.ForeignKey(
        SemestrePeriodo,
        on_delete=models.CASCADE,
        related_name="cursos",
        null=True,
        blank=True,
    )

    def __str__(self):
        semestre_str = f" - {self.semestre_periodo}" if self.semestre_periodo else ""
        return f"{self.nome} - {self.get_semestre_display()} - Turma {self.turma}{semestre_str}"


class Sala(models.Model):
    nome = models.CharField(max_length=100)
    lugares = models.IntegerField(default=0)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    andar = models.ForeignKey(
        Andar, on_delete=models.CASCADE, related_name="salas", null=True, blank=True
    )
    metodologia = models.CharField(
        max_length=15,
        choices=METODOLOGIA_CHOICES,
        default="tradicional",
        verbose_name="Metodologia de Ensino",
    )

    def lugares_disponiveis(self):
        """Retorna a quantidade de lugares disponíveis"""
        return max(0, self.lugares - self.curso.alunos)

    def tem_lugares_livres(self):
        """Retorna True se há lugares disponíveis"""
        return self.lugares > self.curso.alunos

    def __str__(self):
        return f"{self.nome} - {self.curso.nome}"

    class Meta:
        ordering = ["andar__numero", "nome"]
