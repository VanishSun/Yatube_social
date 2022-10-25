from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Post, Group
from django.urls import reverse

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Lev')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.user)

    def test_urls_exist_status_for_guest_user(self):
        """Проверка доступности страницы address для гостя."""
        urls_list = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ): HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexpected/': HTTPStatus.NOT_FOUND,
        }
        for address, status_code in urls_list.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_exist_status_for_guest_user(self):
        """
        Проверка доступности страницы address для
        зарегистрированного пользователя, но не автора.
        """
        urls_list = {
            '/create/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/unexpected/': HTTPStatus.NOT_FOUND,
            '/posts/1/comment/': HTTPStatus.FOUND,
        }
        for address, status_code in urls_list.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_post_edit_url_exists_for_author(self):
        """Страница /posts/<post_id>/edit/ доступна автору."""
        response = self.author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_exists_for_authorized_user(self):
        """Странице address соответствует шаблон для гостя."""
        urls_list = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/Lev/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in urls_list.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_template_exists_for_author(self):
        """Странице address соответствует шаблон для автора."""
        urls_list = {
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in urls_list.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_nonexistent_page(self):
        """Проверка шаблона 404 для несуществующих страниц."""
        url = '/unexpected_page/'
        roles = (
            self.guest_client,
            self.authorized_client,
        )
        for role in roles:
            with self.subTest(url=url):
                response = role.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, 'core/404.html')
