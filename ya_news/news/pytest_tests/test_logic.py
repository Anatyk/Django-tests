from http import HTTPStatus
import pytest

from django.urls import reverse
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse("news:detail", args=(news.id,))
    initial_count = Comment.objects.count()
    client.post(url, data=form_data)
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, news, author, form_data):
    url = reverse("news:detail", args=(news.id,))
    initial_count = Comment.objects.count()
    response = auth_client.post(url, data=form_data)

    expected_redirect = f"{url}#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect

    assert Comment.objects.count() == initial_count + 1
    comment = Comment.objects.get(news=news, author=author)
    assert comment.text == form_data["text"]


@pytest.mark.django_db
@pytest.mark.parametrize("bad_word", BAD_WORDS)
def test_user_cant_use_bad_words(auth_client, news, bad_word):
    url = reverse("news:detail", args=(news.id,))
    data = {"text": f"Текст с плохим словом: {bad_word}"}
    initial_count = Comment.objects.count()

    response = auth_client.post(url, data=data)
    form = response.context.get("form")
    assert form is not None

    errors = form.errors.get("text", [])
    errors_str = " ".join(map(str, errors))
    assert WARNING in errors_str

    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_author_can_delete_comment(auth_client, comment):
    url = reverse("news:delete", args=(comment.id,))
    initial_count = Comment.objects.count()
    response = auth_client.delete(url)

    expected_redirect = f"{reverse('news:detail', args=(comment.news.id,))}#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect

    assert Comment.objects.count() == initial_count - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    url = reverse("news:delete", args=(comment.id,))
    initial_count = Comment.objects.count()
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_author_can_edit_comment(auth_client, comment):
    url = reverse("news:edit", args=(comment.id,))
    data = {"text": "Обновлённый комментарий"}

    response = auth_client.post(url, data=data)

    expected_redirect = f"{reverse('news:detail', args=(comment.news.id,))}#comments"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect

    comment.refresh_from_db()
    assert comment.text == data["text"]


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    url = reverse("news:edit", args=(comment.id,))
    data = {"text": "Попытка редактирования"}
    initial_text = comment.text

    response = reader_client.post(url, data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == initial_text
