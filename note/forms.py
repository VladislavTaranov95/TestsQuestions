from django import forms
from .models import Test, Question, NotedItem
from django.utils.translation import gettext_lazy as _


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', ]

    options = (
        ('10', _('None')),
        ('20', _('Minutes')),
        ('30', _('Days'))
    )
    delay = forms.ChoiceField(label=_('Delay'), widget=forms.Select, choices=options)
    count = forms.CharField(label=_('Wait'), widget=forms.NumberInput, required=False)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', ]


class NoteForm(forms.ModelForm):
    class Meta:
        model = NotedItem
        fields = ['note', ]
        widgets = {
            'note': forms.Textarea(attrs={'cols': 40,
                                          'rows': 8,
                                          'style': 'resize:none;'}),
            }


class AnswerForm(forms.Form):
    Answer = forms.CharField(label=_('Answer'))
