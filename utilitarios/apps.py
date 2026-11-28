from django.apps import AppConfig


class UtilitariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilitarios'
    verbose_name = 'Utilitários'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_logged_out
        from .acesso import registrar_auditoria

        def ao_entrar(sender, request, user, **kwargs):
            registrar_auditoria(request, 'LOGIN', 'login', 'Entrar', 'Login realizado', usuario=user)

        def ao_sair(sender, request, user, **kwargs):
            if user is not None:
                registrar_auditoria(request, 'LOGOUT', 'logout', 'Sair', 'Logout realizado', usuario=user)

        user_logged_in.connect(ao_entrar, dispatch_uid='guto_auditoria_login')
        user_logged_out.connect(ao_sair, dispatch_uid='guto_auditoria_logout')
