from rest_framework.test import APITestCase
from general.factories import UserFactory, MessageFactory, ChatFactory

from rest_framework import status
from general.models import Chat


class ChatTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/chats/"

    def test_get_chat_list(self):
        user_1 = UserFactory()
        user_2 = UserFactory()
        user_3 = UserFactory()

        chat_1 = ChatFactory(user_1=self.user, user_2=user_1)
        chat_2 = ChatFactory(user_1=self.user, user_2=user_2)
        chat_3 = ChatFactory(user_1=user_3, user_2=self.user)

        mes_1 = MessageFactory(author=self.user, chat=chat_1)
        mes_3 = MessageFactory(author=self.user, chat=chat_3)
        mes_2 = MessageFactory(author=user_2, chat=chat_2)

        MessageFactory.create_batch(10)

        with self.assertNumQueries(2):
            response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_chat_ids = [
            chat["id"]
            for chat
            in response.data["results"]
        ]
        expected_chat_ids = [chat_2.pk, chat_3.pk, chat_1.pk]
        self.assertEqual(response_chat_ids, expected_chat_ids)

        chat_2_expected_data = {
            "id": chat_2.pk,
            "companion_name": f"{user_2.first_name} {user_2.last_name}",
            "last_message_content": mes_2.content,
            "last_message_datetime": mes_2.created_at.strftime("%Y-%m-%dT%H:%M:%S"), 
        }
        self.assertDictEqual(
            response.data["results"][0],
            chat_2_expected_data,
        )

        chat_3_expected_data = {
            "id": chat_3.pk,
            "companion_name": f"{user_3.first_name} {user_3.last_name}",
            "last_message_content": mes_3.content,
            "last_message_datetime": mes_3.created_at.strftime("%Y-%m-%dT%H:%M:%S"), 
        }
        self.assertDictEqual(
            response.data["results"][1],
            chat_3_expected_data,
        )
        chat_1_expected_data = {
            "id": chat_1.pk,
            "companion_name": f"{user_1.first_name} {user_1.last_name}",
            "last_message_content": mes_1.content,
            "last_message_datetime": mes_1.created_at.strftime("%Y-%m-%dT%H:%M:%S"), 
        }
        self.assertDictEqual(
            response.data["results"][2],
            chat_1_expected_data,
        )

    def test_create_chat(self):
        user = UserFactory()
        data = {"user_2": user.pk}

        response = self.client.post(
            self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        chat = Chat.objects.last()
        self.assertEqual(chat.user_1, self.user)
        self.assertEqual(chat.user_2, user)
