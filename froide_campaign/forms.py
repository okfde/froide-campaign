from django import forms

from .models import Report, Answer


class QuestionaireForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.questionaire = kwargs.pop("questionaire")

        super().__init__(*args, **kwargs)

        for question in self.questionaire.questions.all():
            self.fields[self._fieldname(question)] = question.make_field()

    def _fieldname(self, question):
        return "field_{}".format(question.id)

    def save(self, user, iobj, foirequest):
        report, created = Report.objects.get_or_create(
            questionaire=self.questionaire,
            informationsobject=iobj,
            defaults={
                "user": user,
                "foirequest": foirequest,
            },
        )
        for question in self.questionaire.questions.all():
            value = self.cleaned_data[self._fieldname(question)]
            Answer.objects.get_or_create(
                report=report, question=question, defaults={"text": str(value)}
            )
        return report
