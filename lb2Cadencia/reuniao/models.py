#!/usr/bin/env python
#coding: utf8
from datetime import *
from bson import Code
from mongoengine import *
from django.db import models
from lb2Cadencia.settings import DBNAME
#Conexao com o mongodb
connect(DBNAME)

class Cadencia(EmbeddedDocument):
    acao = StringField(max_length=100, required=True, verbose_name='Ação')
    data_reuniao = DateTimeField(required=True, verbose_name='Data da Reunião' , default=datetime.now())
    valor_esperado = FloatField(required=True, min_value=0.0, verbose_name='Valor Esperado')
    contato = StringField(max_length=40 ,required=True, verbose_name='Contato Atual')
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

"""
Esse capudo serve para organizar a lista que recebo
do banco.
"""
def proj_graph(list):
        format = '%d/%m/%Y'
        data = []
        goals = []
        #split array
        for i in list:
            data.append(i[0].strftime(format))
            goals.append(i[1])
        return [data,goals]
"""
Organizacao da lista do dashbord geral
"""
def dashboard_geral(list):
    format = '%d/%m/%Y'
    data = []
    propostas = []
    projetos = []
    pipeline = []
    for i in list:
        key = i.key
        data.append(key.strftime(format))
        propostas.append(i.value['propostas'])
        projetos.append(i.value['projetos'])
        pipeline.append(i.value['pipeline'])
    return [data,propostas,projetos,pipeline]

class Projeto(Document):
    vendedor = StringField(max_length=30 , required=True , verbose_name='Vendedor')
    cliente = StringField(max_length=40 , required=True , verbose_name='Cliente')
    nome = StringField(max_length=80 , required=True , verbose_name='Nome')
    cadencias = ListField(EmbeddedDocumentField(Cadencia))
    ativo = BooleanField(default=True)
    meta = {'queryset_class': ProjetoQuerySet}

    @classmethod
    def mr_qt_propostas(document):
        map_f = Code(
            """
            function() {
                for (var idx = 0; idx < this.cadencias.length; idx++) {
                    var key = this.cadencias[idx].data_reuniao;
                    var value = {
                            nome : this.vendedor+this.cliente+this.nome,
                            goals : this.cadencias[idx].goals,
                            valor : this.cadencias[idx].valor_esperado};
                    emit(key, value);
                };
            }
        """
        )
        # reduce to a list of tag ids and counts
        reduce_f = Code ("""
        function(data_reuniao, objs) {
            reducedVal = { propostas: 0, projetos: 0, pipeline : 0};
            var resultArray = [];
            for (var idx = 0; idx < objs.length; idx++) {
                reducedVal.pipeline += objs[idx].valor;
                if (resultArray.indexOf(objs[idx].nome) == -1){
                    resultArray.push(objs[idx].nome);
                    reducedVal.projetos += 1;
                    if(objs[idx].goals.indexOf("Enviada a Proposta") != -1)
                        reducedVal.propostas += 1;
                        resultArray.push(objs[idx].nome);
                }
            }
            return reducedVal;
        };
        """)
        f = """
            function (key, reducedVal) {
                if (typeof reducedVal.propostas == 'undefined'){
                    if (reducedVal.goals.indexOf("Enviada a Proposta") != -1)
                        return {
                            propostas : 1,
                            projetos : 1,
                            pipeline : reducedVal.valor
                        };
                    else
                        return {
                            propostas : 0,
                            projetos : 1,
                            pipeline : reducedVal.valor
                        };
                }else{
                    return reducedVal;
                }
            };
          """
        results = document.objects.map_reduce(map_f,reduce_f,output="inline",finalize_f=f)
        return dashboard_geral(list(results))
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
    def goals_por_cad(document,vendedor,cliente,nome):
        code = """
            function() {
                var data_goals = [[]];
                var i = 0;
                var cad = [];
                var v = options.vendedor;
                var c = options.cliente;
                var n = options.nome;
            db.projeto.aggregate(
                {$unwind: '$cadencias'},
                {$match: {"vendedor" : v, "cliente" : c, "nome" : n}},
                {$sort: {'cadencias.data_reuniao': 1}},
                {$group: {_id: '$_id', 'cadencias': {$push: '$cadencias'}}},
                {$project: {'cadencias': '$cadencias'}}).forEach(function(doc){
                var cad = doc["cadencias"];
                cad.forEach(function(cadDoc){
                    data_goals[i] = [];
                    data_goals[i][0] = cadDoc["data_reuniao"]
                    data_goals[i][1] = cadDoc["goals"].length;
                    i = i + 1;
                });
            });
            return data_goals;
        }
        """
        options = {'vendedor' : vendedor, 'cliente' : cliente, 'nome': nome}
        return proj_graph(document.objects.exec_js(code,**options))
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

