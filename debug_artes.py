#!/usr/bin/env python3

"""
Script de diagnóstico para problema de lançamento de notas em Artes 2° ano
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guto.settings')
django.setup()

from avaliacao.models import Turma, Disciplina, Avaliacao, NotaAvaliacao, Enturmacao
from alunos.models import Aluno

def diagnosticar_artes_segundo_ano():
    print("=== DIAGNÓSTICO: ARTES 2° ANO ===\n")
    
    # 1. Verificar Turma 5
    try:
        turma = Turma.objects.get(pk=5)
        print(f"✅ Turma encontrada: {turma.nome} (ID: {turma.pk})")
        print(f"   - Tipo: {turma.get_tipo_ensino_display()}")
        print(f"   - Ano/Série: {turma.get_ano_serie_display()}")
        print(f"   - Turno: {turma.get_turno_display()}")
    except Turma.DoesNotExist:
        print("❌ ERRO: Turma 5 não encontrada!")
        return
    
    # 2. Verificar Disciplina 3 (Artes)
    try:
        disciplina = Disciplina.objects.get(pk=3)
        print(f"✅ Disciplina encontrada: {disciplina.nome} (ID: {disciplina.pk})")
        print(f"   - Ativa: {disciplina.ativo}")
    except Disciplina.DoesNotExist:
        print("❌ ERRO: Disciplina 3 não encontrada!")
        return
    
    # 3. Verificar alunos enturmados
    alunos = Aluno.objects.filter(
        enturmacoes__turma=turma,
        enturmacoes__ativo=True
    )
    print(f"\n📚 Alunos enturmados na turma: {alunos.count()}")
    for i, aluno in enumerate(alunos[:5], 1):  # Mostrar apenas os primeiros 5
        print(f"   {i}. {aluno.nome} (Código: {aluno.codigo})")
    if alunos.count() > 5:
        print(f"   ... e mais {alunos.count() - 5} alunos")
    
    # 4. Verificar avaliações para esta turma e disciplina
    avaliacoes = Avaliacao.objects.filter(
        turma=turma,
        disciplina=disciplina
    )
    print(f"\n📋 Avaliações de {disciplina.nome} para {turma.nome}: {avaliacoes.count()}")
    
    if avaliacoes.count() == 0:
        print("❌ PROBLEMA IDENTIFICADO: Não há avaliações criadas para Artes na turma 5!")
        print("   Solução: Criar avaliações em /diario/disciplina/avaliacoes/turma/5/?disciplina=3")
        return
    
    for avaliacao in avaliacoes:
        notas_count = NotaAvaliacao.objects.filter(avaliacao=avaliacao).count()
        print(f"   - {avaliacao.nome} (Peso: {avaliacao.peso}) - {notas_count} notas lançadas")
    
    # 5. Verificar notas existentes
    notas_existentes = NotaAvaliacao.objects.filter(
        avaliacao__turma=turma,
        avaliacao__disciplina=disciplina
    )
    print(f"\n⭐ Total de notas lançadas: {notas_existentes.count()}")
    
    # 6. Verificar possíveis problemas
    print(f"\n🔍 DIAGNÓSTICO DETALHADO:")
    
    if avaliacoes.count() == 0:
        print("❌ Problema: Sem avaliações criadas")
    else:
        print(f"✅ Avaliações: {avaliacoes.count()} encontrada(s)")
    
    if alunos.count() == 0:
        print("❌ Problema: Sem alunos enturmados")
    else:
        print(f"✅ Alunos: {alunos.count()} enturmado(s)")
    
    # 7. Testar criação de nota (simulação)
    if avaliacoes.count() > 0 and alunos.count() > 0:
        primeira_avaliacao = avaliacoes.first()
        primeiro_aluno = alunos.first()
        
        print(f"\n🧪 TESTE DE CRIAÇÃO DE NOTA:")
        print(f"   Avaliação: {primeira_avaliacao.nome}")
        print(f"   Aluno: {primeiro_aluno.nome}")
        
        try:
            # Verificar se já existe uma nota
            nota_existente = NotaAvaliacao.objects.filter(
                avaliacao=primeira_avaliacao,
                aluno=primeiro_aluno
            ).first()
            
            if nota_existente:
                print(f"   ✅ Nota já existe: {nota_existente.nota}")
            else:
                print(f"   ✅ Pronto para criar nova nota")
                
        except Exception as e:
            print(f"   ❌ Erro no teste: {e}")
    
    print(f"\n{'='*50}")
    print("RESUMO:")
    if avaliacoes.count() == 0:
        print("🚨 CAUSA PROVÁVEL: Faltam avaliações para a disciplina Artes na turma 5")
        print("💡 SOLUÇÃO: Acesse /diario/disciplina/avaliacoes/turma/5/?disciplina=3 e crie avaliações")
    else:
        print("🤔 Avaliações existem. O problema pode ser JavaScript ou AJAX.")
        print("💡 Verifique o Console do navegador (F12) para erros JavaScript")

if __name__ == "__main__":
    diagnosticar_artes_segundo_ano()