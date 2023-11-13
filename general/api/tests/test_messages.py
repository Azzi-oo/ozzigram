from rest_framework.test import APITestCase
from general.factories import UserFactory, MessageFactory, ChatFactory

from rest_framework import status
from general.models import Chat, Message


class MessageTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/messages/"

    def test_create_message(self):
        chat = ChatFactory(user_1=self.user)
        data = {
            "chat": chat.pk,
            "content": "Test message",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        message = Message.objects.last()
        self.assertEqual(message.author, self.user)
        self.assertEqual(message.chat, chat)
        self.assertEqual(message.content, data["content"])

    def test_try_to_create_message_for_other_chat(self):
        chat = ChatFactory()
        data = {
            "chat": chat.pk,
            "content": "Test message",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Message.objects.count(), 0)

    def test_delete_own_message(self):
        chat = ChatFactory(user_1=self.user)
        message =  MessageFactory(author=self.user, chat=chat)

        response = self.client.delete(
            self.url + f"{message.pk}/",
            format="json",
        )                 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.messages.count(), 0)

    def test_try_to_delete_companion_message(self):
        companion = UserFactory()
        chat = ChatFactory(user_1=self.user, user_2=companion)
        message = MessageFactory(author=companion, chat=chat)

        response = self.client.delete(
            self.url + f"{message.pk}/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(chat.messages.count(), 1)
        self.assertEqual(companion.messages.count(), 1)
