# !/usr/bin/env python
#coding: utf8
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from lb2Cadencia.reuniao.forms import FindProjetoForm, CadenciaForm, ProjetoForm, CadenciaMongoForm
from models import Projeto, Cadencia
import locale
from datetime import *
from datetime import datetime
import datetime


def home(request):
    vendedor = "Bernardo Vale"
    locale.setlocale( locale.LC_ALL, 'pt_BR' )
    #Quantidade de Propostas ativas
    qpa =  len(Projeto.objects(ativo=True))
    # Valor das propostas ativa
    vpa = locale.currency(Projeto.sum_projetos_ativos())
    pipe = locale.currency(Projeto.pipeline())
    qt_propostas = str(Projeto.qt_propostas())[0:-2] #corta ,0
    goals = Projeto.goals_por_cad("Bernardo Vale","Sementes Sefrinho","Box LB2")
    print goals
    return render_to_response('home.html',{'qpa':qpa,'vpa':vpa
                            ,'pipe':pipe,'qt_propostas':qt_propostas},
                              context_instance=RequestContext(request))
def base(request):
    return render_to_response('base.html',
                              context_instance=RequestContext(request))
def novacadencia(request):
    if request.method == 'POST':
        proj = Projeto.objects.get(pk=request.POST['proj_pk'])
        form = CadenciaForm(request.POST)
        if form.is_valid():
            cad = Cadencia(
                acao=request.POST['acao'],
                data_reuniao=request.POST['data_reuniao'],
                valor_esperado=request.POST['valor_esperado'],
                contato = request.POST['contato'],
                goals = request.POST['goals'].split(','))
            proj.update(add_to_set__cadencias=cad)
            proj.save()
            #Refresh no objeto apos salvar
            proj = Projeto.objects.get(pk=proj.pk)

        return render_to_response('novacadencia.html',{'form':form , 'proj' : proj},
                                  context_instance=RequestContext(request))
    return render_to_response('novacadencia.html',
                              context_instance=RequestContext(request))
def cadencia(request):
    if request.method == 'POST':
        # Clicou em nova cadencia na tabela de baixo
        if request.POST['action'] == 'save':
            proj = Projeto.objects.get(pk=request.POST['p_id'])
            return render(request, 'novacadencia.html', {
                'proj': proj,})
        # Clicou em encerrar projeto - Alterar o campo ativo
        elif request.POST['action'] == 'delete':
            proj = Projeto.objects.get(pk=request.POST['p_id'])
            proj.ativo = False
            proj.save()
            return render_to_response('cadencia.html',
                              context_instance=RequestContext(request))
        # Projeto desativado, clicou em restaurar
        elif request.POST['action'] == 'restore':
            proj = Projeto.objects.get(pk=request.POST['p_id'])
            proj.ativo = True
            proj.save()
            return render_to_response('cadencia.html',
                              context_instance=RequestContext(request))

        #Vamos checar se o formulario é valido
        form = FindProjetoForm(request.POST)
        if form.is_valid(): # All validation rules pass
            campo_ven  = request.POST['vendedor']
            campo_cli  = request.POST['cliente']
            campo_nome = request.POST['nome']
            campo_status = request.POST['status']
            print campo_status

            # O Vendedor sempre deve ser especificado
            # Podemos pesquisar com cliente ou com o nome do projeto
            # Ou com os 3
            if campo_cli != '' and campo_nome != '':
                proj = Projeto.objects.get_projeto(campo_ven, campo_nome, campo_cli, campo_status)
            elif campo_nome != '':
                proj = Projeto.objects.get_by_ven_proj(campo_ven, campo_nome)
            elif campo_cli != '':
                proj = Projeto.objects.get_by_ven_cli(campo_ven, campo_cli)
            else:
                proj = Projeto.objects.get_by_vendedor(campo_ven, campo_status)
            return render_to_response('cadencia.html',{'proj':proj},
                              context_instance=RequestContext(request))
        else:
            return render_to_response('cadencia.html',{'form':form},
                              context_instance=RequestContext(request))
    return render_to_response('cadencia.html',
                              context_instance=RequestContext(request))


#Refatorar!
def projeto(request):
    proj = Projeto
    today = datetime.date
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        form_cadencia = CadenciaMongoForm(request.POST)
        if form.is_valid() and form_cadencia.is_valid():
            proj = Projeto(
                nome=request.POST['nome'],
                vendedor=request.POST['vendedor'],
                cliente=request.POST['cliente'])
            g = request.POST['goals'].split(',')
            #todo remover esse trecho de cast da data que
            #nao funciona no apache
            data_reuniao = request.POST['data_reuniao']
            format = '%m/%d/%Y'
            d = datetime.datetime.strptime(data_reuniao,format)
            cad = Cadencia(
                acao=request.POST['acao'],
                data_reuniao=d,
                contato=request.POST['contato'],
                valor_esperado=request.POST['valor_esperado']
            )
            #Tratamento das hashtags para os goals
            cad.goals = g
            proj.cadencias = [cad]
            proj.save()
        return render_to_response('projeto.html', {'proj': proj,'form': form, 'form_cadencia':form_cadencia},
                              context_instance=RequestContext(request))
    return render_to_response('projeto.html', {'proj': proj},
                              context_instance=RequestContext(request))
