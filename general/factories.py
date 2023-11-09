import factory
from factory.django import DjangoModelFactory
from general.models import User, Post


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("email")
    email = factory.Faker("email")
    is_staff = True


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    title = factory.Faker("word")
    body = factory.Faker("text")
