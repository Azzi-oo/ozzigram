from rest_framework.test import APITestCase
from general.factories import UserFactory, PostFactory
from django.contrib.auth.hashers import check_password
from rest_framework import status
from general.models import Post


class PostTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/posts/"

    def test_create_post(self):
        data = {
            "title": "some posts title",
            "body": "some text",
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = Post.objects.last()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.title, data["title"])
        self.assertEqual(post.body, data["body"])
        self.assertIsNotNone(post.created_at)

    def test_unauthorized_post_request(self):
        self.client.logout()

        data = {
            "title": "some post title",
            "body": "some text",
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.all().count(), 0)
