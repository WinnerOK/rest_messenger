from django.test import Client, TestCase
from rest_framework import status

from messenger.models.person import Person
from messenger.serializers.personSerializers import PersonSerializer

client = Client()


class PersonTest(TestCase):
    def setUp(self):
        self.person = Person.objects.create(id="965c9bf5-be59-40e7-980a-d4008faba9d0", name='Petya')

    def test_create(self):
        name = "Vanya"
        resp = client.post("/api/users/", data={"name": name})
        data = resp.data
        self.assertEqual(data["name"], name)

        person = Person.objects.filter(id__exact=data["id"]).first()
        self.assertEqual(person.name, name)

    def test_get(self):
        resp = client.get(f"/api/users/{self.person.id}/")
        serializer = PersonSerializer(self.person)

        self.assertEqual(serializer.data, resp.data)

    def test_not_exist(self):
        resp = client.get(f"/api/users/822aed34-06af-4aad-86ba-ac201a489736/")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data, {"detail": "Not found."})
