from django import forms

from KB_SNP.models import *


class KbSnpResearchForm(forms.ModelForm):

    class Meta(object):
        model = Research
        fields = '__all__'
