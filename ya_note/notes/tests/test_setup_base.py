from typing import Tuple


from django.contrib.auth import get_user_model
from django.test import TestCase, Client


from notes.models import Note


User = get_user_model()


class NotesBaseTestCase(TestCase):
    SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=cls.SLUG,
            author=cls.author,
        )

        cls.slug_for_args: Tuple[str] = (cls.SLUG,)

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

        self.anon_client = Client()
