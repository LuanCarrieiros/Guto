from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.db import models
from .models import (
    Conceito, Turma, Disciplina, LancamentoNota, AtestadoMedico,
    MediaGlobalConceito, RecuperacaoEspecial, ParecerDescritivo,
    AvaliacaoDescritiva, PendenciaAvaliacao, DiarioOnline, ConteudoAula
)


@login_required
def avaliacao_home(request):
    """
    Dashboard principal do módulo Avaliação
    """
    # Estatísticas gerais
    total_turmas = Turma.objects.count()
    total_disciplinas = Disciplina.objects.count()
    total_lancamentos = LancamentoNota.objects.count()
    pendencias = PendenciaAvaliacao.objects.filter(resolvida=False).count()
    
    # Turmas recentes
    turmas_recentes = Turma.objects.order_by('-id')[:5]
    
    # Lançamentos recentes
    lancamentos_recentes = LancamentoNota.objects.order_by('-data_lancamento')[:5]
    
    context = {
        'total_turmas': total_turmas,
        'total_disciplinas': total_disciplinas,
        'total_lancamentos': total_lancamentos,
        'pendencias': pendencias,
        'turmas_recentes': turmas_recentes,
        'lancamentos_recentes': lancamentos_recentes,
    }
    
    return render(request, 'avaliacao/home.html', context)


@login_required
def turmas_list(request):
    """
    Lista todas as turmas para avaliação
    """
    turmas = Turma.objects.all().order_by('ano', 'nome')
    
    # Filtros
    ano = request.GET.get('ano', '')
    periodo_letivo = request.GET.get('periodo_letivo', '')
    
    if ano:
        turmas = turmas.filter(ano=ano)
    if periodo_letivo:
        turmas = turmas.filter(periodo_letivo=periodo_letivo)
    
    context = {
        'turmas': turmas,
        'ano': ano,
        'periodo_letivo': periodo_letivo,
    }
    
    return render(request, 'avaliacao/turmas_list.html', context)


@login_required
def disciplinas_list(request):
    """
    Lista todas as disciplinas
    """
    disciplinas = Disciplina.objects.all().order_by('nome')
    
    context = {
        'disciplinas': disciplinas,
    }
    
    return render(request, 'avaliacao/disciplinas_list.html', context)


@login_required
def notas_list(request):
    """
    Lista lançamentos de notas
    """
    lancamentos = LancamentoNota.objects.all().order_by('-data_lancamento')
    
    # Filtros
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    
    if turma_id:
        lancamentos = lancamentos.filter(turma_id=turma_id)
    if disciplina_id:
        lancamentos = lancamentos.filter(disciplina_id=disciplina_id)
    
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    
    context = {
        'lancamentos': lancamentos,
        'turmas': turmas,
        'disciplinas': disciplinas,
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
    }
    
    return render(request, 'avaliacao/notas_list.html', context)


@login_required
def lancar_notas(request):
    """
    Formulário para lançar notas
    """
    turmas = Turma.objects.all()
    disciplinas = Disciplina.objects.all()
    conceitos = Conceito.objects.filter(ativo=True)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        aluno_id = request.POST.get('aluno')
        conceito_id = request.POST.get('conceito')
        observacoes = request.POST.get('observacoes', '')
        
        if turma_id and disciplina_id and aluno_id and conceito_id:
            from alunos.models import Aluno
            turma = get_object_or_404(Turma, id=turma_id)
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
            aluno = get_object_or_404(Aluno, id=aluno_id)
            conceito = get_object_or_404(Conceito, id=conceito_id)
            
            LancamentoNota.objects.create(
                turma=turma,
                disciplina=disciplina,
                aluno=aluno,
                conceito=conceito,
                observacoes=observacoes,
                usuario_lancamento=request.user
            )
            messages.success(request, 'Nota lançada com sucesso!')
            return redirect('avaliacao:notas_list')
    
    context = {
        'turmas': turmas,
        'disciplinas': disciplinas,
        'conceitos': conceitos,
    }
    
    return render(request, 'avaliacao/lancar_notas.html', context)


@login_required
def conceitos_list(request):
    """
    Lista todos os conceitos
    """
    conceitos = Conceito.objects.all().order_by('valor')
    
    context = {
        'conceitos': conceitos,
    }
    
    return render(request, 'avaliacao/conceitos_list.html', context)


@login_required
def relatorios(request):
    """
    Página de relatórios de avaliação
    """
    # Estatísticas para relatórios
    stats = {
        'total_alunos_avaliados': LancamentoNota.objects.values('aluno').distinct().count(),
        'media_geral': LancamentoNota.objects.aggregate(
            avg_valor=Avg('conceito__valor')
        )['avg_valor'] or 0,
        'total_recuperacoes': RecuperacaoEspecial.objects.count(),
        'total_atestados': AtestadoMedico.objects.count(),
    }
    
    context = {
        'stats': stats,
    }
    
    return render(request, 'avaliacao/relatorios.html', context)


@login_required
def diario_online(request):
    """
    Diário online para registro de conteúdos e frequência
    """
    turmas = Turma.objects.all()
    
    # Conteúdos recentes
    conteudos_recentes = ConteudoAula.objects.order_by('-data_aula')[:10]
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma')
        disciplina_id = request.POST.get('disciplina')
        data_aula = request.POST.get('data_aula')
        conteudo = request.POST.get('conteudo')
        
        if turma_id and disciplina_id and data_aula and conteudo:
            turma = get_object_or_404(Turma, id=turma_id)
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
            
            ConteudoAula.objects.create(
                turma=turma,
                disciplina=disciplina,
                data_aula=data_aula,
                conteudo=conteudo,
                usuario_registro=request.user
            )
            messages.success(request, 'Conteúdo registrado com sucesso!')
            return redirect('avaliacao:diario_online')
    
    context = {
        'turmas': turmas,
        'conteudos_recentes': conteudos_recentes,
    }
    
    return render(request, 'avaliacao/diario_online.html', context)