from rest_framework.test import APITestCase
from general.factories import UserFactory, PostFactory, CommentFactory
from django.contrib.auth.hashers import check_password
from rest_framework import status
from general.models import Post, Reaction, Comment


class CommentTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.post = PostFactory()
        self.url = "/api/comments/"

    def test_create_comment(self):
        data = {
            "post": self.post.pk,
            "body": "comment body",
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.last()
        self.assertEqual(data["post"], comment.post.id)
        self.assertEqual(data["body"], comment.body)
        self.assertEqual(self.user, comment.author)
        self.assertIsNotNone(comment.created_at)
    
    def test_pass_incorrect_post_id(self):
        data = {
            "post": self.post.pk + 1,
            "body": "comment body",
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_own_comment(self):
        comment = CommentFactory(author=self.user)
        response = self.client.delete(
            f"{self.url}{comment.pk}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_other_comment(self):
        comment = CommentFactory()
        response = self.client.delete(
            f"{self.url}{comment.pk}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(
            response.data["detail"],
            "Вы не являетесь автором этого комментария.",
        )