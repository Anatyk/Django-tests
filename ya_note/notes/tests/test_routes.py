from http import HTTPStatus
from typing import List, Dict

from django.urls import reverse

from .test_setup_base import NotesBaseTestCase
from . import common


class TestRoutes(NotesBaseTestCase):
    def setUp(self):
        if not hasattr(self, 'author_client'):
            from django.test import Client
            self.author_client = Client()
            self.author_client.force_login(self.author)

        if not hasattr(self, 'not_author_client'):
            from django.test import Client
            self.not_author_client = Client()
            self.not_author_client.force_login(self.not_author)

        if not hasattr(self, 'anon_client'):
            from django.test import Client
            self.anon_client = Client()

    def test_status_codes_for_various_pages(self):
        home = getattr(common, 'HOME_URL', reverse('notes:home'))
        login = getattr(common, 'LOGIN_URL', reverse('users:login'))
        signup = getattr(common, 'SIGNUP_URL', reverse('users:signup'))
        list_url = getattr(common, 'LIST_URL', reverse('notes:list'))
        add = getattr(common, 'ADD_URL', reverse('notes:add'))
        success = getattr(common, 'SUCCESS_URL', reverse('notes:success'))
        logout = getattr(common, 'LOGOUT_URL', reverse('users:logout'))

        try:
            slug = self.slug_for_args[0]
        except Exception:
            slug = getattr(self, 'SLUG', None) or self.note.slug

        detail = getattr(common, 'DETAIL_URL', None)
        edit = getattr(common, 'EDIT_URL', None)
        delete = getattr(common, 'DELETE_URL', None)

        if callable(detail):
            detail = detail(slug)
        else:
            detail = detail or reverse('notes:detail', args=(slug,))

        if callable(edit):
            edit = edit(slug)
        else:
            edit = edit or reverse('notes:edit', args=(slug,))

        if callable(delete):
            delete = delete(slug)
        else:
            delete = delete or reverse('notes:delete', args=(slug,))

        cases: List[Dict] = [
            {'url': home, 'client_name': 'anon', 'client': self.anon_client,
             'expected': HTTPStatus.OK},
            {'url': login, 'client_name': 'anon', 'client': self.anon_client,
             'expected': HTTPStatus.OK},
            {'url': signup, 'client_name': 'anon', 'client': self.anon_client,
             'expected': HTTPStatus.OK},
            {'url': list_url, 'client_name': 'author',
             'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': add, 'client_name': 'author', 'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': success, 'client_name': 'author',
             'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': detail, 'client_name': 'author',
             'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': detail, 'client_name': 'not_author',
             'client': self.not_author_client,
             'expected': HTTPStatus.NOT_FOUND},
            {'url': edit, 'client_name': 'author',
             'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': edit, 'client_name': 'not_author',
             'client': self.not_author_client,
             'expected': HTTPStatus.NOT_FOUND},
            {'url': delete, 'client_name': 'author',
             'client': self.author_client,
             'expected': HTTPStatus.OK},
            {'url': delete, 'client_name': 'not_author',
             'client': self.not_author_client,
             'expected': HTTPStatus.NOT_FOUND},
            {'url': logout, 'client_name': 'anon', 'client': self.anon_client,
             'expected': HTTPStatus.METHOD_NOT_ALLOWED},
        ]

        for case in cases:
            with self.subTest(
                url=case['url'],
                client=case['client_name'],
                expected=case['expected']
            ):
                resp = case['client'].get(case['url'])
                self.assertEqual(resp.status_code, case['expected'])

    def test_redirects_for_anonymous_users(self):
        login_url = getattr(common, 'LOGIN_URL', reverse('users:login'))

        names_and_urls = [
            getattr(common, 'DETAIL_URL', None),
            getattr(common, 'EDIT_URL', None),
            getattr(common, 'DELETE_URL', None),
            getattr(common, 'ADD_URL', None),
            getattr(common, 'SUCCESS_URL', None),
            getattr(common, 'LIST_URL', None),
        ]

        resolved_urls: List[str] = []
        try:
            slug = self.slug_for_args[0]
        except Exception:
            slug = getattr(self, 'SLUG', None) or self.note.slug

        for u in names_and_urls:
            if u is None:
                continue
            resolved = u(slug) if callable(u) else u
            resolved_urls.append(resolved)

        for url in resolved_urls:
            expected = f'{login_url}?next={url}'
            with self.subTest(
                url=url,
                client='anon',
                expected_redirect=expected
            ):
                resp = self.anon_client.get(url)
                self.assertEqual(resp.status_code, HTTPStatus.FOUND)
                self.assertRedirects(resp, expected)
