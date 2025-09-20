from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from .models import DiarioEletronico, RegistroChamada, RegistroNota, DiarioOnline, ConteudoAula
from turma.models import Turma, Disciplina, DivisaoPeriodoLetivo, Enturmacao, Avaliacao
from alunos.models import Aluno


@login_required
def diario_dashboard(request):
    """Dashboard do diário eletrônico - versão bonita"""
    turmas = Turma.objects.all()
    total_turmas = turmas.count()
    diarios_ativos = total_turmas  # Para agora, consideramos todas as turmas como tendo diários ativos

    context = {
        'turmas': turmas,
        'total_turmas': total_turmas,
        'diarios_ativos': diarios_ativos,
    }
    return render(request, 'diario/diario_eletronico_dashboard.html', context)


@login_required
def diario_home(request):
    """Página inicial do diário eletrônico"""
    turmas = Turma.objects.all()

    context = {
        'turmas': turmas,
    }
    return render(request, 'diario/diario_home.html', context)


@login_required
def diario_turma(request, turma_id):
    """Página do diário de uma turma específica"""
    turma = get_object_or_404(Turma, pk=turma_id)
    disciplinas = turma.disciplinas.all()

    context = {
        'turma': turma,
        'disciplinas': disciplinas,
    }
    return render(request, 'diario/diario_turma.html', context)
