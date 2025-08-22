from django.contrib import admin
from .models import Aluno, DocumentacaoAluno, Responsavel, TransporteAluno, Matricula

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'data_nascimento', 'sexo', 'tipo_arquivo', 'data_cadastro']
    list_filter = ['sexo', 'tipo_arquivo', 'aluno_gemeo', 'data_cadastro']
    search_fields = ['nome', 'codigo']
    readonly_fields = ['codigo', 'data_cadastro', 'data_atualizacao']
    
    fieldsets = (
        ('Dados Básicos', {
            'fields': ('codigo', 'nome', 'nome_social', 'data_nascimento', 'sexo')
        }),
        ('Filiação', {
            'fields': ('nome_mae', 'mae_nao_declarada', 'nome_pai', 'pai_nao_declarado')
        }),
        ('Flags Especiais', {
            'fields': ('aluno_gemeo', 'falta_historico_escolar', 'aluno_exclusivo_aee')
        }),
        ('Controle', {
            'fields': ('tipo_arquivo', 'lembrete', 'foto')
        }),
        ('Auditoria', {
            'fields': ('usuario_cadastro', 'data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        })
    )

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'ano_administrativo', 'tipo_ensino', 'serie_ano', 'status', 'data_matricula']
    list_filter = ['ano_administrativo', 'tipo_ensino', 'tipo_matricula', 'status', 'turno_preferencial']
    search_fields = ['aluno__nome', 'aluno__codigo']
    readonly_fields = ['data_cadastro', 'data_atualizacao']

@admin.register(DocumentacaoAluno)
class DocumentacaoAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'rg', 'cpf', 'certidao_nascimento']
    search_fields = ['aluno__nome', 'rg', 'cpf']

@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'parentesco', 'aluno', 'telefone', 'email']
    search_fields = ['nome', 'aluno__nome']
    list_filter = ['parentesco']

@admin.register(TransporteAluno)
class TransporteAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'utiliza_transporte', 'nome_motorista', 'placa_veiculo', 'rota']
    list_filter = ['utiliza_transporte']
    search_fields = ['aluno__nome', 'nome_motorista', 'placa_veiculo']
