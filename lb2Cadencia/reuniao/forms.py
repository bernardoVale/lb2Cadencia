__author__ = 'bernardovale'
from django import forms


class FindProjetoForm(forms.Form):
    nome = forms.CharField(max_length=80,required=False)
    cliente = forms.CharField(max_length=40,required=False)
    vendedor = forms.CharField(max_length=30,required=True)