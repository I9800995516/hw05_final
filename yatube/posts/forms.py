from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
            'image': ('Картинка'),
        }
        help_texts = {
            'text': ('Введите текст поста'),
            'group': ('Выберите группу'),
            'image': ('Выберите картинку поста'),
        }
        error_messages = {
            'text': {
                'max_length': ("Текст слишком длинный"),
            },
            'group': {
                'max_length': ("Название группы слишком длинное"),
            },
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст комментария',
        }
