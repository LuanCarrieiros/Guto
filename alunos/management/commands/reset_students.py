from django.core.management.base import BaseCommand
from alunos.models import Aluno

class Command(BaseCommand):
    help = 'Remove todos os alunos e recria os 20 alunos fictícios'
    
    def handle(self, *args, **options):
        # Contar alunos existentes
        total_existentes = Aluno.objects.count()
        
        if total_existentes > 0:
            self.stdout.write(
                self.style.WARNING(f'🚨 Encontrados {total_existentes} alunos no banco.')
            )
            self.stdout.write('Deletando todos os alunos existentes...')
            Aluno.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Alunos existentes deletados!'))
        
        # Importar e executar o comando de criação
        from django.core.management import call_command
        call_command('populate_students')