import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


from news.models import News, Comment


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


User = get_user_model()


COMMENT_FORM_DATA = {"text": "Текст комментария"}


@pytest.fixture
def form_data():
    # возвращаем копию, чтобы тесты не мутировали одну и ту же структуру
    return COMMENT_FORM_DATA.copy()


@pytest.fixture
def author():
    return User.objects.create_user(username="author")


@pytest.fixture
def reader():
    return User.objects.create_user(username="reader")


@pytest.fixture
def news():
    return News.objects.create(title="Заголовок", text="Текст")


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text="Текст комментария"
    )


COMMENT_FORM_DATA = {"text": "Текст комментария"}


@pytest.fixture
def auth_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news_list_url():
    return reverse("news:list")


@pytest.fixture
def news_detail_url(news):
    return reverse("news:detail", args=[news.pk])


@pytest.fixture
def comment_create_url(news):
    return reverse("news:comment_create", args=[news.pk])
