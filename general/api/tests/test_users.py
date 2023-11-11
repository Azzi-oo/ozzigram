from rest_framework.test import APITestCase
from general.factories import UserFactory
from rest_framework import status
import json


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
