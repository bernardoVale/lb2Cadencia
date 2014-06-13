from mongoforms import MongoForm
from lb2Cadencia.reuniao.models import Cadencia, Projeto

__author__ = 'bernardovale'
from django import forms


class ProjetoForm(MongoForm):
    class Meta:
        document = Projeto
        fields = ('nome','vendedor','cliente')

class CadenciaMongoForm(MongoForm):
    class Meta:
        document = Cadencia
        fields = ('acao', 'contato', 'data_reuniao', 'valor_esperado' )

class FindProjetoForm(forms.Form):
    nome = forms.CharField(max_length=80,required=False)
    cliente = forms.CharField(max_length=40,required=False)
    vendedor = forms.CharField(max_length=30,required=True)


class CadenciaForm(forms.Form):
    acao = forms.CharField(max_length=100, required=True)
    contato = forms.CharField(max_length=40, required=True)
    data_reuniao = forms.DateTimeField(required=True)
    valor_esperado = forms.FloatField(required=True, min_value=1.0)
    goals = forms.CharField(required=True)
