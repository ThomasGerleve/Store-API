from django.test import TestCase
from django.contrib.auth.models import User, Group
from store_api.models import Store
import json

USERDATA = {
    "username": "user",
    "password": "password",
}

STOREDATA = {
    "name": "Store 1",
    "address": "123 Main St",
    "opening_hours": "9am-5pm"
}

def assert_401(self, response):
    self.assertEqual(response.status_code, 401)
    self.assertIn("Authentication credentials were not provided.", response.json()["detail"])

class TestStoreAPI(TestCase):

    # Unauthorized tests

    def test_api_get_stores_unauthorized(self):
        response = self.client.get("/stores/")
        assert_401(self, response)

    def test_api_post_stores_unauthorized(self):
        response = self.client.post("/stores/", data=STOREDATA)
        assert_401(self, response)

    def test_api_get_store_unauthorized(self):
        response = self.client.get(f"/stores/1")
        assert_401(self, response)

    def test_api_put_store_unauthorized(self):
        response = self.client.put(f"/stores/1", data=STOREDATA)
        assert_401(self, response)

    def test_api_delete_store_unauthorized(self):
        response = self.client.delete(f"/stores/1")
        assert_401(self, response)

    def test_api_post_api_token_with_wrong_credentials(self):
        data = {
            "username": "wrong",
            "password": "wrong",
        }

        response = self.client.post("/api/token/", data=data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("No active account found with the given credentials", response.json()["detail"])

    def test_api_post_api_token_refresh_with_wrong_token(self):
        refresh_data = {
            "refresh": "wrong"
        }

        response = self.client.post("/api/token/refresh/", data=refresh_data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Token is invalid or expired", response.json()["detail"])

    # Authorized tests

    def test_api_post_api_token_with_correct_credentials(self):
        User.objects.create_user(username="user", password="password")

        response = self.client.post("/api/token/", data=USERDATA)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_api_post_api_token_refresh_with_correct_token(self):
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        refresh_token = token_response.json()["refresh"]
        refresh_data = {
            "refresh": refresh_token
        }

        response = self.client.post("/api/token/refresh/", data=refresh_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_api_get_stores_authorized_with_pagination_and_filtering(self):
        for i in range(12):
            Store.objects.create(
                name=f"Store {i+1}",
                address=f"Address {i+1}",
                opening_hours="9am-5pm"
            )
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]
        response = self.client.get("/stores/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(12, response.json()["count"])
        self.assertEqual("http://testserver/stores/?page=2", response.json()["next"])
        self.assertEqual(None, response.json()["previous"])

        next_page_response = self.client.get("/stores/?page=2", HTTP_AUTHORIZATION=f"Bearer {access_token}")
        wanted_next_page_results = [
            {
                "id": 11,
                "name": "Store 11",
                "address": "Address 11",
                "opening_hours": "9am-5pm"
            },
            {
                "id": 12,
                "name": "Store 12",
                "address": "Address 12",
                "opening_hours": "9am-5pm"
            }
        ]

        self.assertEqual(next_page_response.status_code, 200)
        self.assertEqual(None, next_page_response.json()["next"])
        self.assertEqual("http://testserver/stores/", next_page_response.json()["previous"])
        self.assertEqual(wanted_next_page_results, next_page_response.json()["results"])

        filtered_page_response = self.client.get("/stores/?search=2", HTTP_AUTHORIZATION=f"Bearer {access_token}")
        wanted_filtered_page_results = [
            {
                "id": 2,
                "name": "Store 2",
                "address": "Address 2",
                "opening_hours": "9am-5pm"
            },
            {
                "id": 12,
                "name": "Store 12",
                "address": "Address 12",
                "opening_hours": "9am-5pm"
            }
        ]

        self.assertEqual(filtered_page_response.status_code, 200)
        self.assertEqual(2, filtered_page_response.json()["count"])
        self.assertEqual(None, filtered_page_response.json()["next"])
        self.assertEqual(None, filtered_page_response.json()["previous"])
        self.assertEqual(wanted_filtered_page_results, filtered_page_response.json()["results"])

    def test_api_post_store_authorized_as_manager(self):
        manager_group = Group.objects.create(name="manager")
        user = User.objects.create_user(username="user", password="password")
        user.groups.set([manager_group])

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.post("/stores/", data=STOREDATA, HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(STOREDATA["name"], response.json()["name"])
        self.assertEqual(STOREDATA["address"], response.json()["address"])
        self.assertEqual(STOREDATA["opening_hours"], response.json()["opening_hours"])

    def test_api_post_store_authorized_not_as_manager(self):
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.post("/stores/", data=STOREDATA, HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 403)
        self.assertIn("You do not have permission to perform this action.", response.json()["detail"])

    def test_api_get_store_authorized(self):
        store = Store.objects.create(name="Store 1", address="123 Main St", opening_hours="9am-5pm")
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]
        response = self.client.get(f"/stores/{store.id}", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(store.name, response.json()["name"])
        self.assertEqual(store.address, response.json()["address"])
        self.assertEqual(store.opening_hours, response.json()["opening_hours"])

    def test_api_get_store_authorized_not_found(self):
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]
        response = self.client.get("/stores/1", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 404)
        self.assertIn("No Store matches the given query.", response.json()["detail"])

    def test_api_put_store_authorized_as_manager(self):
        store = Store.objects.create(name="Store 2", address="123 Main St", opening_hours="9am-5pm")
        manager_group = Group.objects.create(name="manager")
        user = User.objects.create_user(username="user", password="password")
        user.groups.set([manager_group])

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.put(f"/stores/{store.id}", data=json.dumps(STOREDATA), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(STOREDATA["name"], response.json()["name"])
        self.assertEqual(STOREDATA["address"], response.json()["address"])
        self.assertEqual(STOREDATA["opening_hours"], response.json()["opening_hours"])

    def test_api_put_store_authorized_not_as_manager(self):
        store = Store.objects.create(name="Store 2", address="123 Main St", opening_hours="9am-5pm")
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.put(f"/stores/{store.id}", data=json.dumps(STOREDATA), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 403)
        self.assertIn("You do not have permission to perform this action.", response.json()["detail"])

    def test_api_delete_store_authorized_as_manager(self):
        store = Store.objects.create(name="Store 1", address="123 Main St", opening_hours="9am-5pm")
        manager_group = Group.objects.create(name="manager")
        user = User.objects.create_user(username="user", password="password")
        user.groups.set([manager_group])

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.delete(f"/stores/{store.id}", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Store.objects.count(), 0)

    def test_api_delete_store_authorized_not_as_manager(self):
        store = Store.objects.create(name="Store 1", address="123 Main St", opening_hours="9am-5pm")
        User.objects.create_user(username="user", password="password")

        token_response = self.client.post("/api/token/", data=USERDATA)
        access_token = token_response.json()["access"]

        response = self.client.delete(f"/stores/{store.id}", HTTP_AUTHORIZATION=f"Bearer {access_token}")

        self.assertEqual(response.status_code, 403)
        self.assertIn("You do not have permission to perform this action.", response.json()["detail"])
