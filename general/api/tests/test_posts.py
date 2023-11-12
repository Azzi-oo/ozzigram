from rest_framework.test import APITestCase
from general.factories import UserFactory, PostFactory, ReactionFactory
from django.contrib.auth.hashers import check_password
from rest_framework import status
from general.models import Post, Reaction


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

    def test_post_list(self):
        PostFactory.create_batch(5)

        response = self.client.get(path=self.url, formst="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    def test_post_list_data_structure(self):
        post = PostFactory()
        response = self.client.get(path=self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        author = post.author
        expected_data = {
            "id": post.pk,
            "author": {
                "id": author.pk,
                "first_name": author.first_name,
                "last_name": author.last_name,
            },
            "title": post.title,
            "body": (
                post.body[:125] + "..."
                if len(post.body) > 128
                else post.body
            ),
            "created_at": post.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(expected_data, response.data["results"][0])

    def test_retrieve_structure(self):
        post = PostFactory()
        author = post.author
        reaction = ReactionFactory(
            author=self.user,
            post=post,
            value=Reaction.Values.HEART,
        )
        response = self.client.get(
            path=f"{self.url}{post.pk}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "id": post.pk,
            "author": {
                "id": author.pk,
                "first_name": author.first_name,
                "last_name": author.last_name,
            },
            "title": post.title,
            "body": post.body,
            "my_reaction": reaction.value,
            "created_at": post.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.assertDictEqual(expected_data, response.data)

    def test_retrieve_structure_without_own_reaction(self):
        post = PostFactory()

        response = self.client.get(
            path=f"{self.url}{post.pk}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["my_reaction"], "")

    def test_update_own_post(self):
        post = PostFactory(
            author=self.user,
            title="old_title",
            body="old_body",
        )

        new_data = {
            "title": "new title",
            "body": "new_body",
        }
        response = self.client.patch(
            path=f"{self.url}{post.pk}/",
            data=new_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["title"], new_data["title"])
        self.assertEqual(response.data["body"], new_data["body"])

        post.refresh_from_db()
        self.assertEqual(post.title, new_data["title"], new_data["title"])
        self.assertEqual(post.body, new_data["body"])

    def test_try_to_update_other_post(self):
        post = PostFactory(
            title="old_title",
            body="old_body",
        )
        new_data = {
            "title": "new_title",
            "body": "new_body",
        }
        response = self.client.patch(
            path=f"{self.url}{post.pk}/",
            data=new_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
