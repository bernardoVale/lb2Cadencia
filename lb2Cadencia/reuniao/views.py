# !/usr/bin/env python
#coding: utf8
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from lb2Cadencia.reuniao.forms import FindProjetoForm, CadenciaForm
from models import Projeto, Cadencia
import datetime


def novacadencia(request):
    if request.method == 'POST':
        proj = Projeto.objects.get(pk=request.POST['proj_pk'])
        form = CadenciaForm(request.POST)
        if form.is_valid():
            cad = Cadencia(
                acao=request.POST['acao'],
                data_reuniao=request.POST['data_reuniao'],
                valor_esperado=request.POST['valor_esperado'],
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
def index(request):
    proj = Projeto
    today = datetime.date
    if request.method == 'POST':
        proj = Projeto(
            nome=request.POST['nome'],
            vendedor=request.POST['vendedor'],
            contato=request.POST['contato'],
            cliente=request.POST['cliente'])
        g = request.POST['goals'].split(',')
        cad = Cadencia(
            acao=request.POST['acao'],
            data_reuniao=request.POST['data_reuniao'],
            valor_esperado=request.POST['valor_esperado']
        )
        #Tratamento das hashtags para os goals
        cad.goals = g
        proj.cadencias = [cad]
        proj.save()
    return render_to_response('index.html', {'proj': proj},
                              context_instance=RequestContext(request))
