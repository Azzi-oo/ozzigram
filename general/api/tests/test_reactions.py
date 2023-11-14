from rest_framework.test import APITestCase
from general.factories import UserFactory, PostFactory, ReactionFactory

from rest_framework import status
from general.models import Reaction, Message


class ReactionTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.post = PostFactory()
        self.url = "/api/reaction/"

    def test_create_reaction(self):
        data = {
            "post": self.post.id,
            "value": Reaction.Values.SMILE,
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reaction = Reaction.objects.last()
        self.assertEqual(reaction.author, self.user)
        self.assertEqual(reaction.post, self.post)
        self.assertEqual(reaction.value, data["value"])

    def test_pass_other_reaction(self):
        reaction = ReactionFactory(
            author=self.user,
            post=self.post,
            value=Reaction.Values.SMILE,
        )
        data = {
            "post": self.post.id,
            "value": Reaction.Values.SAD,
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reaction.refresh_from_db()
        self.assertEqual(reaction.value, data["value"])
    
    def test_pass_the_same_value(self):
        reaction = ReactionFactory(
            author=self.user,
            post=self.post,
            value=Reaction.Values.SMILE,
        )
        data = {
            "post": self.post.id,
            "value": Reaction.Values.SMILE,
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reaction.refresh_from_db()
        self.assertEqual(reaction.value, None)
    
    def test_pass_invalid_value(self):
        data = {
            "post": self.post.id,
            "value": "some invalid value",
        }
        response = self.client.post(
            path=self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Reaction.objects.count(), 0)
