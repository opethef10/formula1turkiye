from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from f1t.apps.fantasy.models import Championship


class Question(models.Model):
    QUESTION_TYPES = [
        ('integer', 'Sayısal Değer'),
        ('multiple_choice', 'Çoklu Seçim'),
        ('single_choice', 'Tek Seçim (Radio Button)'),
        ('text', 'Metin'),
        ('driver_multiselect', 'Pilot Çoklu Seçim'),
        ('driver_singleselect', 'Tek Pilot Seçimi (Radio Button)'),
        ('race_singleselect', 'Yarış Seçimi (Radio Button)'),
        ('race_select', 'Yarış Seçimi (Checkbox)'),
        ('constructor_singleselect', 'Tek Takım Seçimi (Radio Button)'),
        ('constructor_multiselect', 'Takım Çoklu Seçim (Checkbox)'),
        ('boolean', 'Evet/Hayır'),
        ('driver_matrix', 'Pilot Sıralama Matrisi'),
    ]

    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(verbose_name="Sıralama")
    text = models.TextField(verbose_name="Soru Metni")
    help_text = models.TextField(blank=True, verbose_name="Yardım Metni")
    question_type = models.CharField(
        max_length=32,
        choices=QUESTION_TYPES,
        default='text',
        verbose_name="Soru Tipi"
    )
    positions = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Matrix Positions",
        help_text="Number of positions in the ranking matrix (only for driver matrix questions)"
    )
    choices = models.TextField(
        blank=True,
        help_text="Virgülle ayrılmış seçenekler (sadece çoklu seçimler için)",
        verbose_name="Seçenekler"
    )
    active = models.BooleanField(default=True, verbose_name="Aktif")
    validation_min = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Minimum Değer"
    )
    validation_max = models.IntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1000)],
        verbose_name="Maksimum Değer"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"

    def __str__(self):
        return f"{self.order}. {self.text[:50]}"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'championship'],
                name='unique_user_championship'
            )
        ]


class Answer(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.JSONField()

    class Meta:
        unique_together = ['prediction', 'question']
