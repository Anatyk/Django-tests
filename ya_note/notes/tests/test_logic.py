from http import HTTPStatus
from django.urls import reverse
from pytils.translit import slugify

from .test_setup_base import NotesBaseTestCase
from notes.models import Note
from notes.forms import WARNING


class TestLogicNotes(NotesBaseTestCase):

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        initial_count = Note.objects.count()

        response = self.author_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.exclude(id=self.note.id).get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        initial_count = Note.objects.count()

        response = self.anon_client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        data = self.form_data.copy()
        data['slug'] = self.note.slug
        initial_count = Note.objects.count()

        response = self.author_client.post(url, data=data)

        form = response.context.get('form')
        self.assertIsNotNone(
            form, "Ожидалась форма в контексте при ошибке валидации"
        )
        slug_errors = form.errors.get('slug', [])
        errors_str = " ".join(map(str, slug_errors))
        self.assertIn(self.note.slug + WARNING, errors_str)

        self.assertEqual(Note.objects.count(), initial_count)

    def test_empty_slug_auto_generation(self):
        url = reverse('notes:add')
        data = self.form_data.copy()
        data.pop('slug', None)
        initial_count = Note.objects.count()

        response = self.author_client.post(url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.exclude(id=self.note.id).get()
        expected_slug = slugify(data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        initial_note = Note.objects.get(id=self.note.id)
        response = self.not_author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(initial_note.title, note_from_db.title)
        self.assertEqual(initial_note.text, note_from_db.text)
        self.assertEqual(initial_note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=self.slug_for_args)
        initial_count = Note.objects.count()

        response = self.author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('notes:success'))

        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=self.slug_for_args)
        initial_count = Note.objects.count()

        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
