from django.contrib import admin
from .models import Question, Prediction, Answer


QUESTION_TEXT_TRIM_LENGTH = 50


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'championship', 'order', 'text_short', 'question_type', 'active', 'required')
    list_editable = ('order', 'active', 'required')
    list_filter = ('active', 'question_type', 'championship')
    search_fields = ('text',)

    def text_short(self, obj):
        length = len(obj.text)
        text = obj.text[:QUESTION_TEXT_TRIM_LENGTH]
        if length > QUESTION_TEXT_TRIM_LENGTH:
            text += '...'
        return text

    text_short.short_description = "Soru"


admin.site.register(Question, QuestionAdmin)
admin.site.register(Prediction)
admin.site.register(Answer)
