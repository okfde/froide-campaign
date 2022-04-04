from django import forms
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from froide.foirequest.models import FoiRequest
from froide.helper.widgets import BootstrapRadioSelect

from .campaign import Campaign, InformationObject


class Questionaire(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    multiple_reports = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    class DataType(models.TextChoices):
        TEXT = "", _("Text")
        CHOICES = "choices", _("Choices")
        INTEGER = "integer", _("Integer")

    questionaire = models.ForeignKey(
        Questionaire, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=255)
    is_required = models.BooleanField(default=False)
    data_type = models.CharField(
        choices=DataType.choices, default=DataType.TEXT, blank=True, max_length=20
    )
    options = models.TextField(blank=True)
    help_text = models.CharField(max_length=255, blank=True)

    position = models.SmallIntegerField(_("Position"), blank=True, default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text

    def make_field(self):
        if self.data_type == self.DataType.CHOICES:
            return forms.ChoiceField(
                label=self.text,
                required=self.is_required,
                choices=[(x, x) for x in self.options.split(",")],
                help_text=self.help_text,
                widget=BootstrapRadioSelect,
            )
        elif self.data_type == self.DataType.INTEGER:
            return forms.IntegerField(
                label=self.text,
                required=self.is_required,
                help_text=self.help_text,
                widget=forms.NumberInput(attrs={"class": "form-control"}),
            )
        try:
            max_length = int(self.options)
        except ValueError:
            max_length = 255
        if max_length == 0:
            max_length = 5000
            widget = forms.Textarea(attrs={"class": "form-control"})
        else:
            widget = forms.TextInput(attrs={"class": "form-control"})
        return forms.CharField(
            label=self.text,
            max_length=max_length,
            required=self.is_required,
            help_text=self.help_text,
            widget=widget,
        )


class Report(models.Model):
    questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(null=True, blank=True, default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )
    informationsobject = models.ForeignKey(
        InformationObject, related_name="reports", on_delete=models.CASCADE
    )
    foirequest = models.ForeignKey(
        FoiRequest, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        get_latest_by = "timestamp"
        ordering = ("-timestamp",)

    def __str__(self):
        return "{} | {}".format(self.questionaire.title, self.informationsobject.title)


class Answer(models.Model):
    text = models.TextField(blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.report, self.text)
