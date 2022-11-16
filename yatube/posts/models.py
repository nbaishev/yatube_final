from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(
        verbose_name='Имя',
        max_length=200,
        help_text='Введите название группы',
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        unique=True,
        help_text='Введите слаг группы',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание группы',
    )

    class Meta:
        """Метаданные модели группы."""
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('title',)

    def __str__(self) -> str:
        """Вернуть название группы."""
        return self.title


class Post(CreatedModel):
    """Модель поста."""

    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        related_name='posts',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        """Метаданные модели группы."""
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-created',)

    def __str__(self):
        """Вернуть содержимое поста."""
        return self.text[:settings.NUMBER_OF_CHARACTERS_IN_TEXT_OF_POST]


class Comment(CreatedModel):
    """Модель комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        help_text='Прокомментируйте запись',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Комментатор',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите комментарий',
    )

    class Meta:
        """Метаданные модели комментария."""
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        """Вернуть текст комментария."""
        return self.text[:settings.NUMBER_OF_CHARACTERS_IN_TEXT_OF_POST]


class Follow(CreatedModel):
    """Модель подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        """Метаданные модели комментария."""
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created',)
        UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow'
        )
