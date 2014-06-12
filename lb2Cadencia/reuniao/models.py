#!/usr/bin/env python
#coding: utf8
from datetime import *
from mongoengine import *
from django.db import models
from lb2Cadencia.settings import DBNAME
#Conexao com o mongodb
connect(DBNAME)

class Cadencia(EmbeddedDocument):
    acao = StringField(max_length=100, required=True, verbose_name='Ação')
    data_reuniao = DateTimeField(required=True, verbose_name='Data da Reunião' , default=datetime.now())
    valor_esperado = FloatField(required=True, min_value=0.0, verbose_name='Valor Esperado')
    contato = StringField(max_length=40 , verbose_name='Contato Atual')
    goals = ListField(StringField(max_length=50), verbose_name='Goals')


class ProjetoQuerySet(QuerySet):

    def parseAtivo(self,s):
        if s == 'True':
            return True
        else:
            return False

    # Query vendedor
    def get_by_vendedor(self,v,s):
        return self.filter(vendedor__icontains=v,ativo=self.parseAtivo(s))
    # Query: vendedor && projeto
    def get_by_ven_proj(self,v,p):
        return self.filter(vendedor__icontains=v,nome__icontains=p)
    # Query vendedor && cliente
    def get_by_ven_cli(self,v,c):
        return self.filter(vendedor__icontains=v,cliente__icontains=c)
    # Quert vendedor && cliente && projeto
    def get_projeto(self,v,p,c,s):
       return self.filter(vendedor__icontains=v,nome__icontains=p,cliente__icontains=c,ativo=s)

class Projeto(Document):
    vendedor = StringField(max_length=30 , required=True , verbose_name='Vendedor')
    cliente = StringField(max_length=40 , required=True , verbose_name='Cliente')
    nome = StringField(max_length=80 , required=True , verbose_name='Nome')
    cadencias = ListField(EmbeddedDocumentField(Cadencia))
    ativo = BooleanField(required=True,default=True)
    meta = {'queryset_class': ProjetoQuerySet}

    @classmethod
    # Soma de propostas de projeto ativos.
    def pipeline(document):
        code = """
        function() {
          var total = 0.0;
          var val = 0.0
          db.projeto.find({ativo:true},{cadencias:{$slice: -1}}).forEach(function(doc) {
            doc["cadencias"].forEach(function(subdoc){
              val = subdoc["valor_esperado"];
            });
            total = total + val;
          });
          return total;
        }
        """
        return document.objects.exec_js(code)

    @classmethod
    # Quantidade de propostas ativas.
    def qt_propostas(document):
        code = """
        function() {
         var count = 0;
          db.projeto.find({ativo:true},{cadencias:{$slice: -1}}).forEach(function(doc) {
            doc["cadencias"].forEach(function(subdoc){
              var goals = subdoc["goals"];
              for (var goal; goal = goals.pop();){
                if (goal == "Enviada a Proposta"){
                  count = count + 1;
                }
              }
            });
          });
          return count;
        }
        """
        return document.objects.exec_js(code)

    @classmethod
    # Soma de propostas de projeto ativos.
    def sum_projetos_ativos(document):
        code = """
        function() {
          var total = 0.0;
          var val = 0.0
          db.projeto.find({ativo:true},{cadencias:{$slice: -1}}).forEach(function(doc) {
            doc["cadencias"].forEach(function(subdoc){
              var goals = subdoc["goals"];
              val = 0.0;
              for (var goal; goal = goals.pop();){
                if (goal == "Enviada a Proposta"){
            	  val = subdoc["valor_esperado"];
            	}
              }
            });
            total = total + val;
          });
          return total;
        }
        """
        return document.objects.exec_js(code)

    # @classmethod
    # def refresh(self):
    #     proj =  Projeto.objects.get(
    #         vendedor = self.vendedor,
    #         cliente = self.cliente,
    #         nome = self.nome
    #     )
    #     return proj
    #def __unicode__(self):
    #    return self.vendedor, self.cliente, self.nome

