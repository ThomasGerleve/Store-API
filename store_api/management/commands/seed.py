from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from store_api.models import Store

class Command(BaseCommand):
    help = "Seeds the database for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding the database")
        run_seed()
        self.stdout.write("Seeding complete")

def clear_database():
    Store.objects.all().delete()
    User.objects.all().delete()
    Group.objects.all().delete()

def create_users():
    User.objects.create_superuser(username="admin", password="admin")
    User.objects.create_user(username="store", password="store")
    manager = User.objects.create_user(username="manager", password="manager")
    group = Group.objects.create(name="manager")
    manager.groups.set([group])

def create_stores():
    for i in range(12):
        Store.objects.create(
            name=f"Store {i+1}",
            address=f"Badstraße {i+1}, 12345 Monopolis",
            opening_hours="Mo-Fr 6:00 - 18:00, Sa 6:00 - 14:00, So 8:00 - 12:00"
        )
    Store.objects.create(name="Super Store", address="Boah Weg 25, 54321 Wowstadt", opening_hours="Mo-Fr 6:00 - 21:00, Sa 7:00 - 19:00")
    Store.objects.create(name="Amazing Store", address="Grandiosallee 10, 54321 Wowstadt", opening_hours="Mo-Mi 6:00 - 21:00, Do,Fr 6:00 - 18:00, Sa 8:00 - 12:00")
    Store.objects.create(name="Top Store", address="Megastraße 4, 54321 Wowstadt", opening_hours="Mo,Di 6:00 - 12:00, 13:00 - 18:00, Mi-Fr 8:00 - 14:00")

def run_seed():
    clear_database()
    create_users()
    create_stores()
