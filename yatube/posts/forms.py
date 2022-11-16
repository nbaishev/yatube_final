from django import forms
from django.conf import settings

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания поста."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите сюда свой текст'
        )
        self.fields['group'].empty_label = (
            'Выберите группу, если желаете 🙂'
        )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа поста'
        }
        help_texts = {
            'text': 'Введите сюда содержимое поста',
            'group': 'Выберите группу, если хотите'
        }

    def clean_text(self):
        post_text = self.cleaned_data['text']
        for word in settings.FORBIDDEN_WORDS:
            if word in post_text.lower():
                raise forms.ValidationError(f'Слово {word} запрещено')
        return post_text


class CommentForm(forms.ModelForm):
    """Форма для комментрия."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Введите сюда комментарий'
        )

    class Meta:
        model = Comment
        fields = ('text', )
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Введите сюда комментарий',
        }

    def clean_text(self):
        comment_text = self.cleaned_data['text']
        for word in settings.FORBIDDEN_WORDS:
            if word in comment_text.lower():
                raise forms.ValidationError(f'Слово {word} запрещено')
        return comment_text
