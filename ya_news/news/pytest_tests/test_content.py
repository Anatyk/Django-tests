from datetime import datetime, timedelta


import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model


from news.models import News, Comment
from news.forms import CommentForm


pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def author():
    return User.objects.create_user(username="author")


@pytest.fixture
def reader():
    return User.objects.create_user(username="reader")


@pytest.fixture
def news():
    return News.objects.create(title="Тестовая новость", text="Просто текст.")


@pytest.fixture
def multiple_news():
    today = datetime.today()
    news_objects = (
        News(
            title=f"Новость {i}",
            text="Просто текст.",
            date=today - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return News.objects.bulk_create(news_objects)


@pytest.fixture
def comment_set(news, author):
    now = timezone.now()
    comments = []
    for i in range(10):
        c = Comment.objects.create(news=news, author=author, text=f"Текст {i}")
        c.created = now + timedelta(days=i)
        c.save()
        comments.append(c)
    return comments


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
def home_url():
    return reverse("news:home")


@pytest.fixture
def news_detail_url(news):
    return reverse("news:detail", args=[news.id])


def test_news_count(client, multiple_news, home_url):
    response = client.get(home_url)
    object_list = response.context["object_list"]
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_order(client, news, author, comment_set, news_detail_url):
    response = client.get(news_detail_url)
    assert "news" in response.context
    news_obj = response.context["news"]
    timestamps = [c.created for c in news_obj.comment_set.all()]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, news_detail_url):
    response = client.get(news_detail_url)
    assert "form" not in response.context


def test_authorized_client_has_form(auth_client, news_detail_url):
    response = auth_client.get(news_detail_url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
