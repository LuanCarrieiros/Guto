from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def transporte_home(request):
    """
    Página inicial do módulo Transporte Escolar
    """
    context = {
        'title': 'Transporte Escolar',
        'description': 'Sistema de gestão de transporte escolar'
    }
    return render(request, 'transporte/transporte_home.html', context)

@login_required
def motorista_list(request):
    """
    Lista de motoristas
    """
    context = {
        'title': 'Motoristas',
        'motoristas': []  # Placeholder
    }
    return render(request, 'transporte/motorista_list.html', context)

@login_required
def motorista_create(request):
    """
    Criar novo motorista
    """
    context = {
        'title': 'Novo Motorista'
    }
    return render(request, 'transporte/motorista_form.html', context)

@login_required
def motorista_detail(request, pk):
    """
    Detalhes do motorista
    """
    context = {
        'title': 'Detalhes do Motorista',
        'pk': pk
    }
    return render(request, 'transporte/motorista_detail.html', context)

@login_required
def veiculo_list(request):
    """
    Lista de veículos
    """
    context = {
        'title': 'Veículos',
        'veiculos': []  # Placeholder
    }
    return render(request, 'transporte/veiculo_list.html', context)

@login_required
def veiculo_create(request):
    """
    Criar novo veículo
    """
    context = {
        'title': 'Novo Veículo'
    }
    return render(request, 'transporte/veiculo_form.html', context)

@login_required
def veiculo_detail(request, pk):
    """
    Detalhes do veículo
    """
    context = {
        'title': 'Detalhes do Veículo',
        'pk': pk
    }
    return render(request, 'transporte/veiculo_detail.html', context)

@login_required
def rota_list(request):
    """
    Lista de rotas
    """
    context = {
        'title': 'Rotas',
        'rotas': []  # Placeholder
    }
    return render(request, 'transporte/rota_list.html', context)

@login_required
def rota_create(request):
    """
    Criar nova rota
    """
    context = {
        'title': 'Nova Rota'
    }
    return render(request, 'transporte/rota_form.html', context)

@login_required
def rota_detail(request, pk):
    """
    Detalhes da rota
    """
    context = {
        'title': 'Detalhes da Rota',
        'pk': pk
    }
    return render(request, 'transporte/rota_detail.html', context)
