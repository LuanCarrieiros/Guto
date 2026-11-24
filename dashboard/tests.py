from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from guto_system.testing import criar_admin


class AutenticacaoTest(TestCase):
    def test_login_redireciona_e_logout_por_post(self):
        User.objects.create_user('maria', password='senha-forte-123')
        resp = self.client.post(reverse('login'), {'username': 'maria', 'password': 'senha-forte-123'})
        self.assertRedirects(resp, reverse('dashboard:home'))
        # Sem "Lembrar-me", a sessão expira ao fechar o navegador
        self.assertTrue(self.client.session.get_expire_at_browser_close())

        resp = self.client.post(reverse('logout'))
        self.assertRedirects(resp, reverse('login'))
        self.assertEqual(self.client.get(reverse('dashboard:home')).status_code, 302)

    def test_lembrar_me_mantem_sessao(self):
        User.objects.create_user('joao', password='senha-forte-123')
        self.client.post(reverse('login'), {'username': 'joao', 'password': 'senha-forte-123', 'remember_me': 'on'})
        self.assertFalse(self.client.session.get_expire_at_browser_close())


class MenuTest(TestCase):
    def test_menu_lateral_aponta_para_modulos_reais(self):
        self.client.force_login(criar_admin())
        resp = self.client.get(reverse('dashboard:home'))
        for nome in ('censo:censo_home', 'transporte:transporte_home', 'aee:aee_home',
                     'escola:escola_home', 'programa:programa_home', 'utilitarios:dashboard'):
            self.assertContains(resp, f'href="{reverse(nome)}"')
