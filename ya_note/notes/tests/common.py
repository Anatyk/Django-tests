from django.urls import reverse


HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')


DETAIL_URL = lambda slug: reverse('notes:detail', args=(slug,))
EDIT_URL = lambda slug: reverse('notes:edit', args=(slug,))
DELETE_URL = lambda slug: reverse('notes:delete', args=(slug,))
LOGOUT_URL = reverse('users:logout')
