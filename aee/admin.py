from django.apps import apps
from django.contrib import admin

# Disponibiliza todos os cadastros do módulo na administração do Django (/admin)
for model in apps.get_app_config('aee').get_models():
    if not admin.site.is_registered(model):
        admin.site.register(model)
