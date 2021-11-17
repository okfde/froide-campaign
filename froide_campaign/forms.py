from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Report, Answer


class QuestionaireForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.questionaire = kwargs.pop("questionaire")

        super().__init__(*args, **kwargs)

        if self.questionaire.multiple_reports:
            self.fields["add_new"] = forms.TypedChoiceField(
                widget=forms.RadioSelect(attrs={"class": "list-unstyled"}),
                choices=(
                    (1, _("Yes, this is a new submission.")),
                    (0, _("No, update my last submission.")),
                ),
                coerce=lambda x: bool(int(x)),
                required=True,
                initial=1,
                label=_("Is this a new submission?"),
                error_messages={"required": _("You have to decide.")},
            )

        for question in self.questionaire.questions.all():
            self.fields[self._fieldname(question)] = question.make_field()

    def _fieldname(self, question):
        return "field_{}".format(question.id)

    def save(self, user, iobj, foirequest):
        add_new = self.cleaned_data.get("add_new", True)
        if add_new:
            report = Report.objects.create(
                questionaire=self.questionaire,
                informationsobject=iobj,
                user=user,
                foirequest=foirequest,
            )
        else:
            report, _created = Report.objects.update_or_create(
                questionaire=self.questionaire,
                informationsobject=iobj,
                defaults={
                    "user": user,
                    "foirequest": foirequest,
                },
            )
        for question in self.questionaire.questions.all():
            value = self.cleaned_data[self._fieldname(question)]
            if add_new:
                Answer.objects.create(report=report, question=question, text=str(value))
            else:
                Answer.objects.update_or_create(
                    report=report, question=question, defaults={"text": str(value)}
                )
        return report
