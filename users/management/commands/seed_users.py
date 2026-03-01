from decimal import Decimal

from django.core.management.base import BaseCommand

from members.models import MemberProfile, MemberStatus
from savings.models import SavingStatus, SavingTransaction, SavingType
from users.models import User, UserRole


class Command(BaseCommand):
    help = 'Seed default users for local development'

    def handle(self, *args, **options):
        users_to_seed = [
            ('ketua', 'ketua.ksb@gmail.com', 'Ketua1234!', UserRole.CHAIRMAN),
            ('manager', 'manager.ksb@gmail.com', 'Manager1234!', UserRole.MANAGER),
            ('petugas', 'petugas.ksb@gmail.com', 'Petugas1234!', UserRole.STAFF),
            ('memberactive', 'member.active@gmail.com', 'Member1234!', UserRole.MEMBER),
            ('memberverified', 'member.verified@gmail.com', 'Member1234!', UserRole.MEMBER),
        ]

        for username, email, password, role in users_to_seed:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={'username': username, 'role': role, 'is_active': True},
            )
            user.username = username
            user.role = role
            user.is_active = True
            user.set_password(password)
            user.save()

            if role == UserRole.MEMBER:
                profile, _ = MemberProfile.objects.get_or_create(user=user)
                pokok_transaction, _ = SavingTransaction.objects.get_or_create(
                    user=user,
                    saving_type=SavingType.POKOK,
                    defaults={'amount': Decimal('150000.00')},
                )

                if email == 'member.active@gmail.com':
                    profile.status = MemberStatus.ACTIVE
                    profile.has_paid_pokok = True
                    profile.member_id = profile.member_id or '#MBR-00001'
                    pokok_transaction.status = SavingStatus.SUCCESS
                else:
                    profile.status = MemberStatus.VERIFIED
                    profile.has_paid_pokok = False
                    pokok_transaction.status = SavingStatus.PENDING

                pokok_transaction.amount = Decimal('150000.00')
                pokok_transaction.save()
                profile.save()

        self.stdout.write(self.style.SUCCESS('Seed users selesai.'))
