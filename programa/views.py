from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def programa_home(request):
    """
    Página inicial do módulo Programa Pedagógico
    """
    context = {
        'title': 'Programa Pedagógico',
        'description': 'Sistema de gestão de programas pedagógicos'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def programa_list(request):
    """
    Lista de programas pedagógicos
    """
    context = {
        'title': 'Programas Pedagógicos',
        'programas': []
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def programa_create(request):
    """
    Criar novo programa pedagógico
    """
    context = {
        'title': 'Novo Programa Pedagógico'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def programa_detail(request, pk):
    """
    Detalhes do programa pedagógico
    """
    context = {
        'title': 'Detalhes do Programa',
        'pk': pk
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def programa_edit(request, pk):
    """
    Editar programa pedagógico
    """
    context = {
        'title': 'Editar Programa',
        'pk': pk
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def modulo_list(request):
    """
    Lista de módulos
    """
    context = {
        'title': 'Módulos do Programa'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def modulo_create(request):
    """
    Criar novo módulo
    """
    context = {
        'title': 'Novo Módulo'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def modulo_detail(request, pk):
    """
    Detalhes do módulo
    """
    context = {
        'title': 'Detalhes do Módulo',
        'pk': pk
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def participante_list(request, programa_pk):
    """
    Lista de participantes do programa
    """
    context = {
        'title': 'Participantes do Programa',
        'programa_pk': programa_pk
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def participante_create(request, programa_pk):
    """
    Inscrever participante no programa
    """
    context = {
        'title': 'Inscrever Participante',
        'programa_pk': programa_pk
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def aula_list(request):
    """
    Lista de aulas
    """
    context = {
        'title': 'Aulas dos Programas'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def aula_create(request):
    """
    Criar nova aula
    """
    context = {
        'title': 'Nova Aula'
    }
    return render(request, 'programa/programa_home.html', context)

@login_required
def frequencia_aula(request, pk):
    """
    Registrar frequência da aula
    """
    context = {
        'title': 'Frequência da Aula',
        'aula_pk': pk
    }
    return render(request, 'programa/programa_home.html', context)
