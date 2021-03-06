from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Добавьте текст поста',
            'group': 'Добавьте группу',
            'image': 'Добавьте изображение',

        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Добавьте комментарий',
        }
