from rest_framework.test import APITestCase
from general.factories import UserFactory, MessageFactory, ChatFactory

from rest_framework import status
from general.models import Chat, Message


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

    def test_try_to_create_chat_when_exists(self):
        user = UserFactory()
        chat = ChatFactory(user_1=self.user, user_2=user)
        data = {"user_2": user.pk}

        response = self.client.post(
            self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        chats = Chat.objects.all()
        self.assertEqual(chats.count(), 1)

    def test_try_to_create_chat_when_exists_reversed(self):
        user = UserFactory()
        chat = ChatFactory(user_1=user, user_2=self.user)
        data = {"user_2": user.pk}

        response = self.client.post(
            self.url,
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        chats = Chat.objects.all()
        self.assertEqual(chats.count(), 1)

        chat = Chat.objects.last()
        self.assertEqual(chat.user_1, user)
        self.assertEqual(chat.user_2, self.user)

    def test_delete_chat(self):
        chat_1 = ChatFactory(user_1=self.user)
        chat_2 = ChatFactory(user_2=self.user)

        MessageFactory(author=self.user, chat=chat_1)
        MessageFactory(author=self.user, chat=chat_2)

        response = self.client.delete(f"{self.url}{chat_1.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(f"{self.url}{chat_2.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Chat.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 0)
    
    def test_try_to_delete_other_chat(self):
        chat = ChatFactory()

        response = self.client.delete(f"{self.url}{chat.pk}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Chat.objects.all().count(), 1)

    def test_get_messages(self):
        user = UserFactory()
        chat = ChatFactory(user_1=self.user, user_2=user)

        message_1 = MessageFactory(author=self.user, chat=chat)
        message_2 = MessageFactory(author=user, chat=chat)
        message_3 = MessageFactory(author=self.user, chat=chat)

        url = f"{self.url}{chat.pk}/messages/"

        with self.assertNumQueries(2):
            response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # сообщения приходят в порядке от новых к старым.
        # поэтому сначала проверяем message_3.
        message_3_expected_data = {
            "id": message_3.pk,
            "content": message_3.content,
            "message_author": "Вы",
            "created_at": message_3.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[0],
            message_3_expected_data,
        )

        message_2_expected_data = {
            "id": message_2.pk,
            "content": message_2.content,
            "message_author": user.first_name,
            "created_at": message_2.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[1],
            message_2_expected_data,
        )

        message_1_expected_data = {
            "id": message_1.pk,
            "content": message_1.content,
            "message_author": "Вы",
            "created_at": message_1.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[2],
            message_1_expected_data,
        )

    def test_get_messages_not_ychastnik(self):
        user = UserFactory()

        chat = ChatFactory(user_1=user, user_2=UserFactory())

        message_1 = MessageFactory(author=user, chat=chat)
        message_2 = MessageFactory(author=chat.user_2, chat=chat)
        message_3 = MessageFactory(author=user, chat=chat)
                                
        url = f"{self.url}{chat.pk}/messages/"

        with self.assertNumQueries(2):
            response = self.client.get(url, format="json")

        message_3_expected_data = {
            "id": message_3.pk,
            "content": message_3.content,
            "message_author": "Вы",
            "created_at": message_3.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[0],
            message_3_expected_data,
        )

        message_1_expected_data = {
            "id": message_1.pk,
            "content": message_1.content,
            "message_author": "Вы",
            "created_at": message_1.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[2],
            message_1_expected_data,
        )

        message_2_expected_data = {
            "id": message_2.pk,
            "content": message_2.content,
            "message_author": user.first_name,
            "created_at": message_2.created_at.strftime(("%Y-%m-%dT%H:%M:%S")),
        }
        self.assertDictEqual(
            response.data[1],
            message_2_expected_data,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(len(response.data), 0)
