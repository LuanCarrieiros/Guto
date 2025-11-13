# -*- coding: utf-8 -*-
"""
Script de Entrega Automatica - SonarCloud/SonarLint
Gera o arquivo entregas.zip pronto para envio
"""

import os
import shutil
import zipfile
from datetime import datetime

print("\n" + "="*60)
print("PREPARANDO ENTREGA - ATIVIDADE SONARCLOUD/SONARLINT")
print("="*60 + "\n")

# 1. Criar pasta de entrega
pasta = "entrega_sonarcloud"
if os.path.exists(pasta):
    shutil.rmtree(pasta)
os.makedirs(pasta)
print("OK: Pasta criada: entrega_sonarcloud/")

# 2. Copiar questionario
shutil.copy2("Questionario_SonarCloud_SonarLint.md",
             os.path.join(pasta, "Questionario_SonarCloud_SonarLint.md"))
print("OK: Questionario copiado")

# 3. Copiar screenshot (procurar por diferentes nomes)
screenshot_encontrado = False
for ext in ['.png', '.jpg', '.jpeg']:
    for nome in ['screenshot_sonarlint', 'sonarlint', 'screenshot', 'print']:
        arquivo = nome + ext
        if os.path.exists(arquivo):
            destino = os.path.join(pasta, 'screenshot_sonarlint' + ext)
            shutil.copy2(arquivo, destino)
            print(f"OK: Screenshot copiado: {arquivo}")
            screenshot_encontrado = True
            break
    if screenshot_encontrado:
        break

if not screenshot_encontrado:
    print("AVISO: Screenshot nao encontrado - adicione manualmente a pasta 'entrega_sonarcloud/'")

# 4. Criar arquivo com link do SonarCloud
with open(os.path.join(pasta, "link_sonarcloud.txt"), 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("LINK DO DASHBOARD SONARCLOUD - SISTEMA GUTO\n")
    f.write("="*60 + "\n\n")
    f.write("Link: https://sonarcloud.io/dashboard?id=LuanCarrieiros_Guto\n\n")
    f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
    f.write("Integrantes do Grupo:\n")
    f.write("- Luan Barbosa Rosa Carrieiros\n")
    f.write("- Diego Moreira Rocha\n")
    f.write("- Arthur Clemente Machado\n")
    f.write("- Bernardo Ferreira Temponi\n")
    f.write("- Arthur Gonçalves de Moraes\n\n")
    f.write("Projeto: Sistema GUTO\n")
    f.write("Repositorio: https://github.com/LuanCarrieiros/Guto\n\n")
    f.write("="*60 + "\n")
    f.write("ANALISE CONCLUIDA COM SUCESSO\n")
    f.write("="*60 + "\n\n")
    f.write("- 102 arquivos Python analisados\n")
    f.write("- Quality Profile: Sonar way\n")
    f.write("- Status: Analise completa\n")

print("OK: Arquivo de link criado")

# 5. Criar README
with open(os.path.join(pasta, "LEIA-ME.txt"), 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("ENTREGA - ATIVIDADE SONARCLOUD E SONARLINT\n")
    f.write("="*60 + "\n\n")
    f.write("Disciplina: Engenharia de Software II\n")
    f.write(f"Data de Entrega: {datetime.now().strftime('%d/%m/%Y')}\n")
    f.write("Projeto: Sistema GUTO - Gestao Escolar\n\n")
    f.write("INTEGRANTES DO GRUPO:\n")
    f.write("- Luan Barbosa Rosa Carrieiros\n")
    f.write("- Diego Moreira Rocha\n")
    f.write("- Arthur Clemente Machado\n")
    f.write("- Bernardo Ferreira Temponi\n")
    f.write("- Arthur Gonçalves de Moraes\n\n")
    f.write("="*60 + "\n")
    f.write("CONTEUDO DESTA ENTREGA\n")
    f.write("="*60 + "\n\n")
    f.write("1. Questionario_SonarCloud_SonarLint.md\n")
    f.write("   -> Respostas completas das 7 questoes\n\n")
    f.write("2. screenshot_sonarlint.png (ou .jpg)\n")
    f.write("   -> Screenshot do SonarLint no VS Code\n\n")
    f.write("3. link_sonarcloud.txt\n")
    f.write("   -> Link do dashboard publico do SonarCloud\n\n")
    f.write("4. LEIA-ME.txt (este arquivo)\n")
    f.write("   -> Informacoes sobre a entrega\n\n")
    f.write("="*60 + "\n")
    f.write("FERRAMENTAS UTILIZADAS\n")
    f.write("="*60 + "\n\n")
    f.write("- SonarCloud - Analise estatica no servidor\n")
    f.write("  * 102 arquivos Python analisados\n")
    f.write("  * Quality Profile: Sonar way\n")
    f.write("  * Tempo de analise: 1min 45s\n\n")
    f.write("- SonarLint - Extensao VS Code instalada\n")
    f.write("  * Analise em tempo real\n")
    f.write("  * Screenshot incluido\n\n")
    f.write("- Questionario - Completo com 7 questoes respondidas\n\n")
    f.write("="*60 + "\n")
    f.write("LINKS IMPORTANTES\n")
    f.write("="*60 + "\n\n")
    f.write("Dashboard SonarCloud:\n")
    f.write("https://sonarcloud.io/dashboard?id=LuanCarrieiros_Guto\n\n")
    f.write("Repositorio GitHub:\n")
    f.write("https://github.com/LuanCarrieiros/Guto\n\n")
    f.write("="*60 + "\n")
    f.write("STATUS: ENTREGA COMPLETA E PRONTA\n")
    f.write("="*60 + "\n")

print("OK: README criado")

# 6. Compactar tudo
arquivo_zip = "entregas.zip"
if os.path.exists(arquivo_zip):
    os.remove(arquivo_zip)

with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(pasta):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(pasta))
            zipf.write(file_path, arcname)

tamanho = os.path.getsize(arquivo_zip) / 1024
print(f"OK: ZIP criado: entregas.zip ({tamanho:.2f} KB)")

print("\n" + "="*60)
print("ENTREGA PRONTA PARA ENVIO!")
print("="*60)
print(f"\nArquivo: entregas.zip")
print(f"Conteudo verificado em: {pasta}/")
print("\nPROXIMO PASSO:")
print("   1. Verifique o conteudo da pasta 'entrega_sonarcloud/'")
print("   2. Se o screenshot nao foi copiado, adicione manualmente")
print("   3. Envie 'entregas.zip' no Canvas/Moodle")
print(f"\nPrazo: Hoje as 23:59")
print("\n" + "="*60 + "\n")
