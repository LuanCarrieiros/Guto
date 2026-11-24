import csv
from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from alunos.models import Aluno, Matricula
from funcionarios.models import Funcionario


def anos_disponiveis():
    """Anos com matrículas cadastradas, incluindo sempre o ano corrente."""
    anos = set(Matricula.objects.values_list('ano_administrativo', flat=True))
    anos.add(date.today().year)
    return sorted(anos, reverse=True)

@login_required
def censo_home(request):
    """
    Página inicial do módulo Censo
    """
    # Estatísticas básicas
    total_alunos = Aluno.objects.count()
    total_funcionarios = Funcionario.objects.count()
    total_matriculas = Matricula.objects.filter(status='ATIVA').count()
    
    context = {
        'title': 'Censo Escolar',
        'total_alunos': total_alunos,
        'total_funcionarios': total_funcionarios,
        'total_matriculas': total_matriculas,
        'ano_atual': datetime.now().year,
    }
    return render(request, 'censo/censo_home.html', context)

@login_required
def censo_escolar(request):
    """
    Dados do censo escolar atual
    """
    ano_atual = datetime.now().year
    return censo_escolar_ano(request, ano_atual)

@login_required
def censo_escolar_ano(request, ano):
    """
    Dados do censo escolar por ano
    """
    # Dados de matrículas por ano
    matriculas = Matricula.objects.filter(ano_administrativo=ano)
    
    # Estatísticas por tipo de ensino
    matriculas_por_tipo = {}
    for matricula in matriculas:
        tipo = matricula.get_tipo_ensino_display()
        if tipo not in matriculas_por_tipo:
            matriculas_por_tipo[tipo] = 0
        matriculas_por_tipo[tipo] += 1
    
    context = {
        'title': f'Censo Escolar {ano}',
        'ano': ano,
        'total_matriculas': matriculas.count(),
        'matriculas_por_tipo': matriculas_por_tipo,
        'matriculas_ativas': matriculas.filter(status='ATIVA').count(),
        'matriculas_encerradas': matriculas.filter(status='ENCERRADA').count(),
        'anos_disponiveis': anos_disponiveis(),
    }
    return render(request, 'censo/censo_escolar.html', context)

@login_required
def relatorios(request):
    """
    Página de relatórios do censo
    """
    context = {
        'title': 'Relatórios do Censo'
    }
    return render(request, 'censo/relatorios.html', context)

@login_required
def relatorio_matriculas(request):
    """
    Relatório de matrículas com filtros por ano, status e tipo de ensino
    """
    ano = request.GET.get('ano', str(date.today().year))
    status = request.GET.get('status', '')
    tipo_ensino = request.GET.get('tipo_ensino', '')

    matriculas = Matricula.objects.select_related('aluno').order_by('aluno__nome')
    if ano:
        matriculas = matriculas.filter(ano_administrativo=ano)
    if status:
        matriculas = matriculas.filter(status=status)
    if tipo_ensino:
        matriculas = matriculas.filter(tipo_ensino=tipo_ensino)

    context = {
        'title': f'Relatório de Matrículas {ano}' if ano else 'Relatório de Matrículas',
        'ano': ano,
        'matriculas': matriculas,
        'anos_disponiveis': anos_disponiveis(),
        'status_choices': Matricula.STATUS_CHOICES,
        'tipo_ensino_choices': Matricula.TIPO_ENSINO_CHOICES,
    }
    return render(request, 'censo/relatorio_matriculas.html', context)

@login_required
def relatorio_funcionarios(request):
    """
    Relatório de funcionários
    """
    tipo_arquivo = request.GET.get('tipo_arquivo', '')
    nome = request.GET.get('nome', '').strip()
    funcionarios = Funcionario.objects.order_by('nome')
    if tipo_arquivo:
        funcionarios = funcionarios.filter(tipo_arquivo=tipo_arquivo)
    if nome:
        funcionarios = funcionarios.filter(nome__icontains=nome)

    context = {
        'title': 'Relatório de Funcionários',
        'funcionarios': funcionarios,
    }
    return render(request, 'censo/relatorio_funcionarios.html', context)

@login_required
def relatorio_estatisticas(request):
    """
    Relatório de estatísticas gerais
    """
    # Estatísticas por sexo
    alunos_masculino = Aluno.objects.filter(sexo='M').count()
    alunos_feminino = Aluno.objects.filter(sexo='F').count()
    
    # Estatísticas de idade (faixas)
    hoje = date.today()
    
    idades = []
    for aluno in Aluno.objects.all():
        idade = hoje.year - aluno.data_nascimento.year
        if (hoje.month, hoje.day) < (aluno.data_nascimento.month, aluno.data_nascimento.day):
            idade -= 1
        idades.append(idade)
    
    # Faixas etárias
    faixas_etarias = {
        '0-5 anos': len([i for i in idades if 0 <= i <= 5]),
        '6-10 anos': len([i for i in idades if 6 <= i <= 10]),
        '11-14 anos': len([i for i in idades if 11 <= i <= 14]),
        '15-17 anos': len([i for i in idades if 15 <= i <= 17]),
        '18+ anos': len([i for i in idades if i >= 18]),
    }
    
    context = {
        'title': 'Estatísticas Gerais',
        'alunos_masculino': alunos_masculino,
        'alunos_feminino': alunos_feminino,
        'faixas_etarias': faixas_etarias,
        'total_alunos': len(idades),
    }
    return render(request, 'censo/relatorio_estatisticas.html', context)

@login_required
def exportar_dados(request, tipo):
    """
    Exportar dados em diferentes formatos
    """
    if tipo == 'matriculas':
        matriculas = Matricula.objects.all()
        if request.GET.get('ano'):
            matriculas = matriculas.filter(ano_administrativo=request.GET['ano'])
        data = list(matriculas.values(
            'aluno__nome',
            'ano_administrativo',
            'tipo_ensino',
            'serie_ano',
            'status'
        ))
    elif tipo == 'funcionarios':
        data = list(Funcionario.objects.select_related('documentacao').values(
            'nome',
            'documentacao__cpf',
            'data_nascimento',
            'tipo_arquivo'
        ).order_by('nome'))
    else:
        return JsonResponse({'erro': 'Tipo de exportação não reconhecido'}, status=400)
    
    if request.GET.get('formato') == 'csv' and isinstance(data, list):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="censo_{tipo}.csv"'
        response.write('\ufeff')  # BOM para o Excel reconhecer UTF-8
        escritor = csv.writer(response, delimiter=';')
        if data:
            escritor.writerow(data[0].keys())
            for linha in data:
                escritor.writerow(linha.values())
        return response

    response = JsonResponse({
        'tipo': tipo,
        'total': len(data) if isinstance(data, list) else 0,
        'dados': data
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    if isinstance(data, list):
        response['Content-Disposition'] = f'attachment; filename="censo_{tipo}.json"'
    return response
