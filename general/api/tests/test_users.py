from rest_framework.test import APITestCase
from general.factories import UserFactory
from django.contrib.auth.hashers import check_password
from rest_framework import status
import json
from general.models import User


class UserTestCase(APITestCase):
    def setUp(self):
        print("Запуск метода сетАп")
        self.user = UserFactory()
        print(f"username: {self.user.username}\n")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/users/"

    def test_user_list(self):
        UserFactory.create_batch(20)
        response = self.client.get(path=self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 21)

    def test_user_list_response_structure(self):
        response = self.client.get(path=self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        expected_data = {
            "id": self.user.pk,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "is_friend": False,
        }
        self.assertDictEqual(response.data["results"][0], expected_data)

    def test_user_list_is_friend_field(self):
        users = UserFactory.create_batch(5)

        self.user.friends.add(users[-1])
        self.user.save()

        with self.assertNumQueries(3):
            response = self.client.get(path=self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)

        self.assertTrue(response.data["results"][0]["is_friend"])

        for user_data in response.data["results"][1::]:
            self.assertFalse(user_data["is_friend"])

    def test_correct_registration(self):
        self.client.logout()

        data = {
            "username": "test_user_1",
            "password": "12345",
            "email": "test_user_1@gmail.com",
            "first_name": "Aza",
            "last_name": "Yanb",
        }
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_user = User.objects.last()
        self.assertTrue(check_password(data["password"], created_user.password))
        data.pop("password")

        user_data = {
            "username": created_user.username,
            "email": created_user.email,
            "first_name": created_user.first_name,
            "last_name": created_user.last_name,
        }
        self.assertDictEqual(data, user_data)

    def test_try_to_pass_existing_username(self):
        self.client.logout()

        data = {
            "username": self.user.username,
            "password": "12345",
            "email": "test_user_1@gmail.com",
            "first_name": "Aza",
            "last_name": "Yanb",
        }

        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 1)

    def test_user_add_friend(self):
        friend = UserFactory()
        url = f"{self.url}{friend.pk}/add_friend/"

        response = self.client.post(path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(friend in self.user.friends.all())

    