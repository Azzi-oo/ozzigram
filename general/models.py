from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint, F, functions


class User(AbstractUser):
    friends = models.ManyToManyField(
        to='self',
        symmetrical=True,
        blank=True,
    )


class Post(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    title = models.CharField(max_length=64)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'({self.id}) {self.title}'


class Comment(models.Model):
    body = models.TextField()
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Reaction(models.Model):
    class Values(models.TextChoices):
        SMILE = 'smile', 'Улыбка'
        THUMB_UP = 'thumb_up', 'Больщой палец'
        LAUGH = 'laugh', 'Смех'
        SAD = 'sad', 'Грусть'
        HEART = 'heart', 'Сердце'

    value = models.CharField(max_length=8, choices=Values.choices, null=True)
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='reactions',
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='reactions',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'author',
                'post',
                name='author_post_unique',
            ),
        ]


class Chat(models.Model):
    user_1 = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='user_1',
    )
    user_2 = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='user_2',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                functions.Greatest(F('user_1'), F('user_2')),
                functions.Least(F('user_1'), F('user_2')),
                name='users_chat_unique',
            ),
        ]


class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    created_at = models.DateTimeField(auto_now_add=True)
