#!/usr/bin/env python3
"""
Script para corrigir botões "Voltar" hardcoded
Substitui links hardcoded por JavaScript que usa o histórico real
"""

import os
import re
import glob

def fix_navigation_in_file(file_path):
    """Corrige um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrão para capturar botões voltar com href hardcoded
        # Exemplo: <a href="{% url 'algo' %}" class="...">...Voltar</a>
        pattern_href = r'<a\s+href="[^"]*"\s+class="([^"]*)"[^>]*>\s*(?:<i[^>]*></i>\s*)?(?:.*?)?Voltar\s*</a>'
        
        def replace_href(match):
            css_classes = match.group(1)
            # Mantém as classes CSS mas remove o href hardcoded
            return f'<a href="#" class="btn-voltar {css_classes}" onclick="event.preventDefault(); window.gutoNav?.goBack() || history.back();">\n                    <i class="fas fa-arrow-left mr-2"></i>Voltar\n                </a>'
        
        # Substitui os padrões
        content = re.sub(pattern_href, replace_href, content, flags=re.IGNORECASE | re.DOTALL)
        
        # Padrão mais específico para casos onde o ícone está separado
        pattern_with_icon = r'<a\s+href="[^"]*"\s+class="([^"]*)"[^>]*>\s*<i[^>]*></i>\s*Voltar\s*</a>'
        
        def replace_with_icon(match):
            css_classes = match.group(1)
            return f'<a href="#" class="btn-voltar {css_classes}" onclick="event.preventDefault(); window.gutoNav?.goBack() || history.back();">\n                    <i class="fas fa-arrow-left mr-2"></i>Voltar\n                </a>'
        
        content = re.sub(pattern_with_icon, replace_with_icon, content, flags=re.IGNORECASE | re.DOTALL)
        
        # Se o conteúdo mudou, salva o arquivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigido: {file_path}")
            return True
        else:
            print(f"📝 Sem alterações: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro em {file_path}: {e}")
        return False

def main():
    """Função principal"""
    # Diretório dos templates
    templates_dir = "/mnt/c/Users/Luan/Desktop/Documents/5 sem/Engenharia de Software II/Guto/templates"
    
    # Encontra todos os arquivos HTML
    html_files = glob.glob(os.path.join(templates_dir, "**", "*.html"), recursive=True)
    
    # Filtra apenas os que têm "Voltar" ou "voltar"
    files_with_voltar = []
    for file_path in html_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Voltar' in content or 'voltar' in content:
                    files_with_voltar.append(file_path)
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
    
    print(f"🔍 Encontrados {len(files_with_voltar)} arquivos com botões 'Voltar'")
    print("🔧 Corrigindo navegação...")
    print()
    
    fixed_count = 0
    for file_path in files_with_voltar:
        if fix_navigation_in_file(file_path):
            fixed_count += 1
    
    print()
    print(f"✅ Correção concluída!")
    print(f"📊 {fixed_count} arquivos corrigidos de {len(files_with_voltar)} analisados")

if __name__ == "__main__":
    main()