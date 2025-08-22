from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
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
    
    # Dados fictícios para demonstração (depois virão do banco de dados real)
    context = {
        'total_alunos': 1250,
        'total_funcionarios': 85,
        'avaliacoes_pendentes': 23,
        'transportes_ativos': 12,
        'escola_nome': 'Sistema GUTO',
        'data_atual': hoje,
        'dia_semana': dia_semana,
        
        # Dados para gráficos (simulados)
        'alunos_por_serie': [
            {'serie': '1º Ano', 'quantidade': 180},
            {'serie': '2º Ano', 'quantidade': 165},
            {'serie': '3º Ano', 'quantidade': 142},
            {'serie': '4º Ano', 'quantidade': 158},
            {'serie': '5º Ano', 'quantidade': 135},
        ],
        
        # Atividades recentes
        'atividades_recentes': [
            {
                'tipo': 'Avaliação',
                'descricao': 'Prova de Matemática - 5º Ano',
                'data': '2025-01-20',
                'status': 'Concluída',
                'icon': 'fas fa-clipboard-list',
                'color': 'green'
            },
            {
                'tipo': 'Aluno',
                'descricao': 'Novo aluno matriculado: João Silva',
                'data': '2025-01-19',
                'status': 'Ativo',
                'icon': 'fas fa-user-plus',
                'color': 'blue'
            },
            {
                'tipo': 'Transporte',
                'descricao': 'Rota 03 - Manutenção programada',
                'data': '2025-01-18',
                'status': 'Agendado',
                'icon': 'fas fa-bus',
                'color': 'yellow'
            },
        ]
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
