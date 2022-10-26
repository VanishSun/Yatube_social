import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from posts.models import Post, Group, Follow
from http import HTTPStatus


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Lev')
        cls.paginator_objects = []
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(1, 13):
            new_post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост ' + str(i),
                group=cls.group
            )
            cls.paginator_objects.append(new_post)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Lev')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostViewTests.user)
        cache.clear()

    def test_pages_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = self.post.id
        slug = self.group.slug
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': post_id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_create'
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template_for_author(self):
        """
        URL-адрес использует шаблон редактирования posts/create_post.html
        для автора.
        """
        post_id = self.post.id
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_index_page_show_correct_context(self):
        """Шаблон posts/index.html сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон posts/group_list.html сформирован с правильным контекстом."""
        slug = self.group.slug
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': slug})
        )
        first_object = response.context['page_obj'].object_list[0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(response.context['group'].slug, slug)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон posts/profile.html сформирован с правильным контекстом."""
        author = self.post.author
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': author})
        )
        first_object = response.context['page_obj'].object_list[0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(response.context['author'], author)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_post_id_page_show_correct_context(self):
        """
        Шаблон posts/post_detail.html сформирован с правильным контекстом.
        """
        post_id = self.post.id
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_create_post_page_show_correct_context(self):
        """Шаблон posts/create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """
        Шаблон posts/edit_post.html сформирован с правильным контекстом
        в случае редактирования поста автором.
        """
        post_id = self.post.id
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': post_id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cache(self):
        """Проверка работы кэша страницы index."""
        post = Post.objects.create(
            author=self.user,
            text='Пост для провери работы кэша',
            group=self.group
        )
        response_1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.get(pk=post.id).delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_3.content)

    def test_users_can_follow_and_unfollow(self):
        """Авторизованный клиент может подписаться и отписаться."""
        follower_quantity = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(PostViewTests.user,))
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(PostViewTests.user,)),
            HTTPStatus.FOUND
        )
        self.assertEqual(Follow.objects.count(), follower_quantity + 1)
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(PostViewTests.user,))
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(PostViewTests.user,)),
            HTTPStatus.FOUND
        )
        self.assertEqual(Follow.objects.count(), follower_quantity)

    def test_post_appears_at_feed(self):
        """Пост появляется в ленте у подписчика."""
        Follow.objects.get_or_create(
            user=self.user,
            author=PostViewTests.user
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertContains(response, self.post)
        Follow.objects.filter(
            user=self.user,
            author__username=PostViewTests.user.username
        ).delete()
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotContains(response, self.post)
