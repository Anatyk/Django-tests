from django.urls import reverse
from notes.forms import NoteForm

from .test_setup_base import NotesBaseTestCase


class TestContentViews(NotesBaseTestCase):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.not_author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_form_presence_on_create_and_edit_pages(self):
        urls = [
            ('create', reverse('notes:add')),
            ('edit', reverse('notes:edit', args=self.slug_for_args)),
        ]
        for name, url in urls:
            with self.subTest(page=name):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
