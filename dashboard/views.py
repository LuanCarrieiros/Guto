from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db import models
from django.contrib.auth.models import User
from .models import AtividadeRecente
from alunos.models import Aluno
from funcionarios.models import Funcionario
from avaliacao.models import Turma, Enturmacao, Avaliacao
import datetime
import locale

@login_required
def home(request):
    """
    View principal do dashboard - mostra resumo geral do sistema
    """
    # Configurar localização para português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar padrão se não conseguir configurar
    
    # Data atual com dia da semana
    hoje = datetime.date.today()
    dias_semana = {
        0: 'Segunda-feira',
        1: 'Terça-feira', 
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    dia_semana = dias_semana[hoje.weekday()]
    
    # Dados reais do banco de dados
    total_alunos = Aluno.objects.count()
    total_funcionarios = Funcionario.objects.count()
    
    # Avaliações pendentes (não lançadas)
    avaliacoes_pendentes = Avaliacao.objects.filter(notas_lancadas=False).count()
    
    # Buscar atividades recentes reais
    atividades_recentes = AtividadeRecente.objects.select_related('usuario')[:10]
    
    # Dados reais de alunos por série/turma
    turmas_com_alunos = Turma.objects.annotate(
        total_alunos=Count('enturmacoes', filter=Q(enturmacoes__ativo=True))
    ).filter(total_alunos__gt=0).order_by('nome')
    
    # Preparar dados para o gráfico
    alunos_por_serie = []
    total_max = 0
    
    for turma in turmas_com_alunos:
        alunos_por_serie.append({
            'serie': turma.nome,
            'quantidade': turma.total_alunos
        })
        if turma.total_alunos > total_max:
            total_max = turma.total_alunos
    
    # Calcular percentuais para as barras (baseado no máximo)
    if total_max > 0:
        for item in alunos_por_serie:
            item['percentual'] = (item['quantidade'] / total_max) * 100
    
    context = {
        'total_alunos': total_alunos,
        'total_funcionarios': total_funcionarios,
        'avaliacoes_pendentes': avaliacoes_pendentes,
        'transportes_ativos': 0,  # Será implementado quando o módulo transporte for criado
        'escola_nome': 'Sistema GUTO',
        'data_atual': hoje,
        'dia_semana': dia_semana,
        
        # Dados reais para gráficos
        'alunos_por_serie': alunos_por_serie,
        'total_turmas': turmas_com_alunos.count(),
        
        # Atividades recentes reais
        'atividades_recentes': atividades_recentes,
    }
    
    return render(request, 'dashboard/home.html', context)

def estatisticas(request):
    """
    View para página de estatísticas detalhadas
    """
    context = {
        'page_title': 'Estatísticas',
    }
    return render(request, 'dashboard/estatisticas.html', context)

def configuracoes(request):
    """
    View para configurações do sistema
    """
    context = {
        'page_title': 'Configurações',
    }
    return render(request, 'dashboard/configuracoes.html', context)


def em_desenvolvimento(request):
    """
    View para páginas em desenvolvimento
    """
    # Obter parâmetros da URL
    funcionalidade = request.GET.get('funcionalidade', '')
    progresso = request.GET.get('progresso', '75')
    
    context = {
        'funcionalidade': funcionalidade,
        'progresso': progresso,
    }
    
    return render(request, 'em_desenvolvimento.html', context)
