from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Проверка создания поста',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args={self.user}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        for form_field in form_data.keys():
            if form_field == 'image':
                self.assertEqual(
                    Post.objects.latest('created').image, 'posts/small.gif'
                )
            else:
                self.assertTrue(
                    (Post._meta.get_field(form_field)
                     .value_from_object(Post.objects
                     .latest('created'))) == form_data[form_field]
                )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        other_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3c'
        )
        uploaded = SimpleUploadedFile(
            name='other.gif',
            content=other_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args={self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args={self.post.pk}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        for form_field in form_data.keys():
            if form_field == 'image':
                self.assertEqual(
                    Post.objects.latest('created').image, 'posts/other.gif'
                )
            else:
                self.assertTrue(
                    (Post._meta.get_field(form_field)
                     .value_from_object(Post.objects
                     .latest('created'))) == form_data[form_field]
                )

    def test_cant_create_post_with_forbidden_words(self):
        """Проверяет что нельзя создать пост
        со словами из запрещенного списка.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Блин',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form',
            'text',
            'Слово блин запрещено',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_anonymous_cant_create_post(self):
        """Неавторизованный пользователь не может
        создать запись в Post.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост неавторизованного пользователя',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_anonymous_cant_comment(self):
        """Неавторизованный пользователь не может
        комментировать.
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Коммент от анонима',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args={self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/comment/'
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_comment_add(self):
        """Добавление комментария."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                args={self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args={self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        for form_field in form_data.keys():
            self.assertTrue(
                (Comment._meta.get_field(form_field)
                 .value_from_object(Comment.objects
                 .latest('created'))) == form_data[form_field]
            )

    def test_cant_add_comment_with_forbidden_words(self):
        """Проверяет что нельзя добавить комментарий
        со словами из запрещенного списка.
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Блин',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args={self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), comments_count + 1)
        self.assertFormError(
            response,
            'form',
            'text',
            'Слово блин запрещено',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
