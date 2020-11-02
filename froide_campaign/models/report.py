from django.db import models

from .campaign import Campaign, InformationObject


class Questionaire(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    campaign = models.ForeignKey(Campaign,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.CharField(max_length=255)
    is_required = models.BooleanField(default=False)
    options = models.CharField(max_length=255, blank=True)
    help_text = models.CharField(max_length=255, blank=True)
    questionaire = models.ForeignKey(Questionaire,
                                     on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Report(models.Model):
    questionaire = models.ForeignKey(Questionaire,
                                     on_delete=models.CASCADE)
    informationsobject = models.ForeignKey(InformationObject,
                                           on_delete=models.CASCADE)

    def __str__(self):
        return '{} | {}'.format(self.questionaire.title,
                                self.informationsobject.title)


class Answer(models.Model):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
