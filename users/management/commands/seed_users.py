from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Seed akun awal untuk testing'

    def handle(self, *args, **kwargs):
        accounts = [
            {'email': 'ketua.ksb@gmail.com',   'password': 'Ketua1234!',   'role': 'CHAIRMAN'},
            {'email': 'manager.ksb@gmail.com',  'password': 'Manager1234!', 'role': 'MANAGER'},
            {'email': 'petugas.ksb@gmail.com',  'password': 'Petugas1234!',   'role': 'STAFF'},
        ]

        for acc in accounts:
            if not User.objects.filter(email=acc['email']).exists():
                User.objects.create_user(
                    email=acc['email'],
                    password=acc['password'],
                    role=acc['role'],
                )
                self.stdout.write(f"✓ Dibuat: {acc['email']}")
            else:
                self.stdout.write(f"- Skip (sudah ada): {acc['email']}")

        self.stdout.write('Selesai!')
