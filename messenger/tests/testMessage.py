from datetime import timedelta
from typing import List, Dict, Any

from django.test import TestCase, Client
from django.utils import timezone, dateparse
from rest_framework import status
from rest_framework.serializers import Serializer

from messenger.models import Message
from messenger.models.person import Person
from messenger.serializers.messageSerializers import MessageSerializer

client = Client()


class MessageTest(TestCase):
    @staticmethod
    def stringify_messages(response_messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        response_data = []
        for msg in response_messages:
            stringified_msg = {}
            for k, v in msg.items():
                stringified_msg[k] = str(v)
            response_data.append(stringified_msg)
        return response_data

    def assert_messages_equal(self, db_messages: List[Message], response_data: List[Dict[str, Any]],
                              serializer: Serializer = MessageSerializer) -> None:
        serialized = serializer(db_messages, many=True)  # noqa
        self.assertEqual(len(response_data), len(db_messages))
        response_data = MessageTest.stringify_messages(response_data)
        serialized_data = MessageTest.stringify_messages(serialized.data)
        self.assertEqual(serialized_data, response_data)

    def setUp(self):
        self.sender = Person.objects.create(id="965c9bf5-be59-40e7-980a-d4008faba9d0", name='Petya')
        self.receiver = Person.objects.create(id="d7970bd9-2be2-4f8b-8d9f-c2bd31fba483", name='Vanya')
        self.interceptor = Person.objects.create(id="093474d3-bcb5-4587-b4db-8e63c8a68565", name='Sanya')
        self.message_text = "Some text"
        self.new_message_text = "Some other text"
        self.message = Message.objects.create(sender=self.sender, receiver=self.receiver, text=self.message_text)

    def test_send_message(self):
        resp = client.post("/api/messages/", data={
            "text": self.message_text,
            "sender": self.sender.id,
            "receiver": self.receiver.id,
        })
        data = resp.data
        msg = Message.objects.filter(id__exact=data["id"]).first()
        serializer = MessageSerializer(msg)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data, data)
        self.assertTrue(
            timezone.now() - dateparse.parse_datetime(data["created_at"]) < timedelta(seconds=1)
        )

    def test_self_received_message(self):
        resp = client.post("/api/messages/received/", data={
            "user": self.receiver.id,
        })

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assert_messages_equal([self.message], resp.data)

    def test_others_received_message(self):
        resp = client.post("/api/messages/received/", data={
            "user": self.interceptor.id,
        })

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_self_sent_message(self):
        resp = client.post("/api/messages/sent/", data={
            "user": self.sender.id,
        })

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assert_messages_equal([self.message], resp.data)

    def test_others_sent_message(self):
        resp = client.post("/api/messages/sent/", data={
            "user": self.interceptor.id,
        })

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_patch_self_message(self):
        resp = client.patch(f"/api/messages/{self.message.id}/", data={
            "text": self.new_message_text,
            "sender": self.sender.id,
        }, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        msg = Message.objects.filter(id__exact=self.message.id).first()
        self.assert_messages_equal([msg], [resp.data])
        self.assertEqual(msg.text, self.new_message_text)
        self.assertTrue(
            timezone.now() - dateparse.parse_datetime(resp.data["updated_at"]) < timedelta(seconds=1)
        )

    def test_patch_other_message(self):
        resp = client.patch(f"/api/messages/{self.message.id}/", data={
            "text": self.new_message_text,
            "sender": self.interceptor.id,
        }, content_type="application/json")

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data, {"detail": "Updating someone else's message is prohibited"})

    def test_delete_self_message(self):
        resp = client.post(f"/api/messages/destroy/{self.message.id}/", data={
            "user": self.sender.id
        }, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Message.objects.filter(id__exact=self.message.id)), 0)

    def test_delete_other_message(self):
        resp = client.post(f"/api/messages/destroy/{self.message.id}/", data={
            "user": self.interceptor.id
        }, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data, {"detail": "Deleting other's messages is prohibited"})

    def test_delete_nonexisting_message(self):
        resp = client.post(f"/api/messages/destroy/{self.interceptor.id}/", data={
            "user": self.sender.id
        }, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data, {"detail": "Message with given uuid doesn't exist"})

    def test_delete_message_as_nonexisting_user(self):
        resp = client.post(f"/api/messages/destroy/{self.message.id}/", data={
            "user": self.message.id
        }, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp.data, {"detail": "User with given uuid doesn't exist"})
