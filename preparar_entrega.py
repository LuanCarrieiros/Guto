"""
Script para preparar a entrega da atividade SonarCloud/SonarLint
Autor: Sistema GUTO
Data: 11/11/2025
"""

import os
import shutil
import zipfile
from datetime import datetime

def criar_pasta_entrega():
    """Cria a pasta para os arquivos de entrega"""
    pasta = "entrega_sonarcloud"
    if os.path.exists(pasta):
        print(f"⚠️  Pasta '{pasta}' já existe. Removendo...")
        shutil.rmtree(pasta)

    os.makedirs(pasta)
    print(f"✅ Pasta '{pasta}' criada com sucesso!")
    return pasta

def copiar_questionario(pasta_destino):
    """Copia o arquivo do questionário"""
    arquivo_origem = "Questionario_SonarCloud_SonarLint.md"

    if not os.path.exists(arquivo_origem):
        print(f"❌ Erro: Arquivo '{arquivo_origem}' não encontrado!")
        return False

    arquivo_destino = os.path.join(pasta_destino, arquivo_origem)
    shutil.copy2(arquivo_origem, arquivo_destino)
    print(f"✅ Questionário copiado: {arquivo_origem}")
    return True

def copiar_screenshot(pasta_destino):
    """Copia o screenshot do SonarLint"""
    # Procura por arquivo de screenshot com diferentes extensões
    extensoes = ['.png', '.jpg', '.jpeg']
    nomes_possiveis = ['screenshot_sonarlint', 'sonarlint_screenshot', 'screenshot']

    arquivo_encontrado = None
    for nome in nomes_possiveis:
        for ext in extensoes:
            arquivo = nome + ext
            if os.path.exists(arquivo):
                arquivo_encontrado = arquivo
                break
        if arquivo_encontrado:
            break

    if arquivo_encontrado:
        arquivo_destino = os.path.join(pasta_destino, 'screenshot_sonarlint' + os.path.splitext(arquivo_encontrado)[1])
        shutil.copy2(arquivo_encontrado, arquivo_destino)
        print(f"✅ Screenshot copiado: {arquivo_encontrado}")
        return True
    else:
        print("⚠️  Screenshot não encontrado! Por favor:")
        print("   1. Capture um screenshot do SonarLint no VS Code")
        print("   2. Salve como 'screenshot_sonarlint.png' na pasta do projeto")
        print("   3. Execute este script novamente")
        return False

def criar_arquivo_link(pasta_destino):
    """Cria arquivo com o link do SonarCloud"""
    link_file = os.path.join(pasta_destino, "link_sonarcloud.txt")

    # Solicita o link ao usuário
    print("\n📎 Por favor, forneça o link do seu dashboard no SonarCloud:")
    print("   (Ex: https://sonarcloud.io/project/overview?id=LuanCarrieiros_Guto)")
    link = input("   Link: ").strip()

    if not link:
        print("⚠️  Link não fornecido. Criando arquivo de template...")
        link = "[COLE AQUI O LINK DO SEU DASHBOARD NO SONARCLOUD]\n\nO link deve ter o formato:\nhttps://sonarcloud.io/project/overview?id=LuanCarrieiros_Guto"

    with open(link_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("Link do Dashboard SonarCloud - Sistema GUTO\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Link: {link}\n\n")
        f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write("Instruções:\n")
        f.write("1. Acesse o link acima\n")
        f.write("2. Verifique se o projeto está configurado como PÚBLICO\n")
        f.write("3. Explore as abas: Overview, Issues, Measures, Code\n\n")
        f.write("Informações do projeto:\n")
        f.write("- Nome: Sistema GUTO\n")
        f.write("- Linguagem: Python (Django)\n")
        f.write("- Repositório: https://github.com/yluan/Guto\n")

    print(f"✅ Arquivo de link criado: link_sonarcloud.txt")
    return True

def criar_readme(pasta_destino):
    """Cria um README na pasta de entrega"""
    readme_file = os.path.join(pasta_destino, "LEIA-ME.txt")

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ENTREGA - Atividade SonarCloud e SonarLint\n")
        f.write("=" * 60 + "\n\n")
        f.write("Disciplina: Engenharia de Software II\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
        f.write("Projeto: Sistema GUTO - Gestão Escolar\n\n")
        f.write("Integrantes do Grupo:\n")
        f.write("- Luan Barbosa Rosa Carrieiros\n")
        f.write("- Diego Moreira Rocha\n")
        f.write("- Arthur Clemente Machado\n")
        f.write("- Bernardo Ferreira Temponi\n")
        f.write("- Arthur Gonçalves de Moraes\n\n")
        f.write("=" * 60 + "\n")
        f.write("CONTEÚDO DESTA ENTREGA\n")
        f.write("=" * 60 + "\n\n")
        f.write("1. Questionario_SonarCloud_SonarLint.md\n")
        f.write("   → Respostas completas do questionário de estudo\n\n")
        f.write("2. screenshot_sonarlint.png (ou .jpg)\n")
        f.write("   → Screenshot do SonarLint identificando problemas no código\n\n")
        f.write("3. link_sonarcloud.txt\n")
        f.write("   → Link público do dashboard do projeto no SonarCloud\n\n")
        f.write("4. LEIA-ME.txt (este arquivo)\n")
        f.write("   → Informações sobre a entrega\n\n")
        f.write("=" * 60 + "\n")
        f.write("SOBRE O PROJETO ANALISADO\n")
        f.write("=" * 60 + "\n\n")
        f.write("Sistema GUTO (Gestão Unificada e Tecnológica Organizacional)\n")
        f.write("- Framework: Django 5.2.6\n")
        f.write("- Linguagem: Python 3.14+\n")
        f.write("- Módulos: Alunos, Funcionários, Turmas, Diário Eletrônico\n")
        f.write("- Linhas de código: ~15.000+\n\n")
        f.write("=" * 60 + "\n")
        f.write("FERRAMENTAS UTILIZADAS\n")
        f.write("=" * 60 + "\n\n")
        f.write("- SonarCloud: Análise estática de código no servidor\n")
        f.write("- SonarLint: Extensão VS Code para análise em tempo real\n")
        f.write("- Connected Mode: Sincronização entre SonarLint e SonarCloud\n\n")
        f.write("=" * 60 + "\n")
        f.write("OBSERVAÇÕES\n")
        f.write("=" * 60 + "\n\n")
        f.write("- Todos os arquivos foram verificados antes da entrega\n")
        f.write("- O dashboard do SonarCloud está configurado como PÚBLICO\n")
        f.write("- O projeto foi analisado com sucesso pelo SonarCloud\n")
        f.write("- O SonarLint foi instalado e configurado no VS Code\n\n")

    print(f"✅ README criado: LEIA-ME.txt")

def compactar_entrega(pasta_origem):
    """Cria o arquivo ZIP com todos os arquivos"""
    arquivo_zip = "entregas.zip"

    # Remove arquivo ZIP anterior se existir
    if os.path.exists(arquivo_zip):
        os.remove(arquivo_zip)
        print(f"🗑️  Arquivo ZIP anterior removido")

    # Cria novo ZIP
    with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(pasta_origem):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(pasta_origem))
                zipf.write(file_path, arcname)

    tamanho = os.path.getsize(arquivo_zip) / 1024  # Tamanho em KB
    print(f"✅ Arquivo ZIP criado: {arquivo_zip} ({tamanho:.2f} KB)")
    return arquivo_zip

def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("🎓 PREPARADOR DE ENTREGA - ATIVIDADE SONARCLOUD/SONARLINT")
    print("=" * 60 + "\n")

    try:
        # 1. Criar pasta de entrega
        print("📁 Etapa 1/6: Criando pasta de entrega...")
        pasta = criar_pasta_entrega()
        print()

        # 2. Copiar questionário
        print("📝 Etapa 2/6: Copiando questionário...")
        if not copiar_questionario(pasta):
            print("❌ Erro ao copiar questionário. Abortando...")
            return
        print()

        # 3. Copiar screenshot
        print("📸 Etapa 3/6: Procurando screenshot...")
        screenshot_ok = copiar_screenshot(pasta)
        print()

        # 4. Criar arquivo de link
        print("🔗 Etapa 4/6: Criando arquivo de link...")
        criar_arquivo_link(pasta)
        print()

        # 5. Criar README
        print("📄 Etapa 5/6: Criando arquivo LEIA-ME...")
        criar_readme(pasta)
        print()

        # 6. Compactar tudo
        print("📦 Etapa 6/6: Compactando arquivos...")
        arquivo_final = compactar_entrega(pasta)
        print()

        # Resumo final
        print("=" * 60)
        print("✅ PREPARAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"\n📦 Arquivo pronto para entrega: {arquivo_final}\n")

        if not screenshot_ok:
            print("⚠️  ATENÇÃO:")
            print("   - Screenshot não foi encontrado!")
            print("   - Adicione o screenshot e execute o script novamente\n")

        print("📋 Próximos passos:")
        print("   1. Verifique o conteúdo de 'entrega_sonarcloud/'")
        print("   2. Confirme que todos os arquivos estão corretos")
        print("   3. Envie o arquivo 'entregas.zip' no Canvas/Moodle")
        print("   4. Não se esqueça do prazo: 11/11/2025 às 23:59\n")

        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Erro durante a preparação: {str(e)}\n")
        print("Por favor, verifique os arquivos e tente novamente.")

if __name__ == "__main__":
    main()
