from http import HTTPStatus
import pytest


from django.urls import reverse


@pytest.mark.django_db
def test_pages_availability(client, news):
    urls = (
        ('news:home', None),
        ('news:detail', (news.id,)),
        ('users:login', None),
        ('users:signup', None),
    )
    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("author", HTTPStatus.OK),
        ("reader", HTTPStatus.NOT_FOUND),
    ],
)
def test_availability_for_comment_edit_and_delete(
    request, client, comment, user_fixture, expected_status
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)

    for name in ("news:edit", "news:delete"):
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, comment):
    login_url = reverse("users:login")
    for name in ("news:edit", "news:delete"):
        url = reverse(name, args=(comment.id,))
        redirect_url = f"{login_url}?next={url}"
        response = client.get(url)

        assert response.status_code == HTTPStatus.FOUND

        assert response.url == redirect_url
