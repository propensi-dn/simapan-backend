"""
Tests for PBI-9 and PBI-12.

Run with:
    python manage.py test verifications
"""
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from members.models import MemberProfile, MemberStatus
from savings.models import SavingStatus, SavingTransaction, SavingType
from users.models import User, UserRole
from verifications.models import VerificationLog
from verifications.services import process_deposit_verification, process_pokok_verification


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(email, role=UserRole.MEMBER, **kw):
    u = User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='Test1234!',
        role=role,
        **kw,
    )
    return u


def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}


def make_saving(user, saving_type=SavingType.POKOK, amount=150000, status=SavingStatus.PENDING):
    s = SavingTransaction.objects.create(
        user=user,
        saving_type=saving_type,
        amount=Decimal(str(amount)),
        transfer_proof='transfer_proofs/dummy.jpg',
        member_bank_name='BCA',
        member_account_number='1234567890',
        status=status,
    )
    return s


# ===========================================================================
# PBI-9 Service Tests
# ===========================================================================

class PBI9ServiceTest(APITestCase):

    def setUp(self):
        self.staff = make_user('staff@ksb.com', role=UserRole.STAFF)
        self.member_user = make_user('member@ksb.com', role=UserRole.MEMBER)
        self.profile = self.member_user.member_profile
        self.profile.status = MemberStatus.VERIFIED
        self.profile.save()

    def _make_pokok(self, status=SavingStatus.PENDING):
        return make_saving(self.member_user, SavingType.POKOK, 150000, status)

    # --- APPROVE ---

    def test_approve_pokok_changes_member_to_active(self):
        saving = self._make_pokok()
        result = process_pokok_verification(
            saving=saving, staff=self.staff, action='approve'
        )
        self.assertEqual(result['action'], 'approved')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, MemberStatus.ACTIVE)

    def test_approve_pokok_generates_member_id(self):
        saving = self._make_pokok()
        result = process_pokok_verification(
            saving=saving, staff=self.staff, action='approve'
        )
        self.assertIsNotNone(result['member_id'])
        self.assertTrue(result['member_id'].startswith('#MBR-'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.member_id, result['member_id'])

    def test_approve_pokok_saving_status_becomes_success(self):
        saving = self._make_pokok()
        process_pokok_verification(saving=saving, staff=self.staff, action='approve')
        saving.refresh_from_db()
        self.assertEqual(saving.status, SavingStatus.SUCCESS)

    def test_approve_creates_verification_log(self):
        saving = self._make_pokok()
        process_pokok_verification(saving=saving, staff=self.staff, action='approve')
        log = VerificationLog.objects.filter(saving_transaction=saving).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, 'APPROVE')
        self.assertEqual(log.staff, self.staff)

    def test_member_id_increments_sequentially(self):
        # First member
        saving1 = self._make_pokok()
        r1 = process_pokok_verification(saving=saving1, staff=self.staff, action='approve')
        # Second member
        member_user2 = make_user('m2@ksb.com', role=UserRole.MEMBER)
        member_user2.member_profile.status = MemberStatus.VERIFIED
        member_user2.member_profile.save()
        saving2 = make_saving(member_user2, SavingType.POKOK)
        r2 = process_pokok_verification(saving=saving2, staff=self.staff, action='approve')
        n1 = int(r1['member_id'].replace('#MBR-', ''))
        n2 = int(r2['member_id'].replace('#MBR-', ''))
        self.assertEqual(n2, n1 + 1)

    # --- REJECT ---

    def test_reject_pokok_saving_status_becomes_rejected(self):
        saving = self._make_pokok()
        process_pokok_verification(
            saving=saving, staff=self.staff, action='reject',
            rejection_reason='Bukti transfer tidak jelas'
        )
        saving.refresh_from_db()
        self.assertEqual(saving.status, SavingStatus.REJECTED)

    def test_reject_stores_rejection_reason(self):
        saving = self._make_pokok()
        reason = 'Nominal tidak sesuai'
        process_pokok_verification(
            saving=saving, staff=self.staff, action='reject', rejection_reason=reason
        )
        saving.refresh_from_db()
        self.assertEqual(saving.rejection_reason, reason)

    def test_reject_resets_has_paid_pokok(self):
        saving = self._make_pokok()
        self.profile.has_paid_pokok = True
        self.profile.save()
        process_pokok_verification(
            saving=saving, staff=self.staff, action='reject',
            rejection_reason='Bukti tidak valid'
        )
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.has_paid_pokok)

    def test_reject_member_status_stays_verified(self):
        saving = self._make_pokok()
        process_pokok_verification(
            saving=saving, staff=self.staff, action='reject',
            rejection_reason='Foto buram'
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.status, MemberStatus.VERIFIED)

    # --- GUARD CASES ---

    def test_cannot_approve_already_confirmed_saving(self):
        saving = self._make_pokok(status=SavingStatus.SUCCESS)
        with self.assertRaises(ValueError):
            process_pokok_verification(saving=saving, staff=self.staff, action='approve')

    def test_cannot_approve_if_member_not_verified(self):
        self.profile.status = MemberStatus.ACTIVE
        self.profile.save()
        saving = self._make_pokok()
        with self.assertRaises(ValueError):
            process_pokok_verification(saving=saving, staff=self.staff, action='approve')

    def test_cannot_process_wajib_saving_in_pokok_service(self):
        saving = make_saving(self.member_user, SavingType.WAJIB)
        with self.assertRaises(ValueError):
            process_pokok_verification(saving=saving, staff=self.staff, action='approve')


# ===========================================================================
# PBI-9 API Tests
# ===========================================================================

class PBI9APITest(APITestCase):

    def setUp(self):
        self.staff = make_user('staff2@ksb.com', role=UserRole.STAFF)
        self.member_user = make_user('mem2@ksb.com', role=UserRole.MEMBER)
        self.profile = self.member_user.member_profile
        self.profile.status = MemberStatus.VERIFIED
        self.profile.save()
        self.saving = make_saving(self.member_user, SavingType.POKOK)

    def _url_queue(self):
        return reverse('pokok-queue')

    def _url_detail(self):
        return reverse('pokok-detail', kwargs={'pk': self.saving.pk})

    def _url_confirm(self):
        return reverse('pokok-confirm', kwargs={'pk': self.saving.pk})

    def test_queue_requires_auth(self):
        resp = self.client.get(self._url_queue())
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_queue_forbidden_for_member(self):
        member = make_user('nomem@ksb.com', role=UserRole.MEMBER)
        resp = self.client.get(self._url_queue(), **auth_headers(member))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_queue_returns_pending_pokok(self):
        resp = self.client.get(self._url_queue(), **auth_headers(self.staff))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_detail_returns_transaction(self):
        resp = self.client.get(self._url_detail(), **auth_headers(self.staff))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['transaction_id'], self.saving.transaction_id)

    def test_confirm_approve_returns_200(self):
        resp = self.client.post(
            self._url_confirm(),
            {'action': 'approve'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['action'], 'approved')
        self.assertIn('member_id', resp.data)

    def test_confirm_reject_requires_reason(self):
        resp = self.client.post(
            self._url_confirm(),
            {'action': 'reject', 'rejection_reason': ''},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_reject_with_reason_returns_200(self):
        resp = self.client.post(
            self._url_confirm(),
            {'action': 'reject', 'rejection_reason': 'Bukti tidak valid'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['action'], 'rejected')

    def test_confirm_invalid_action(self):
        resp = self.client.post(
            self._url_confirm(),
            {'action': 'maybe'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_queue(self):
        resp = self.client.get(
            self._url_queue() + '?search=mem2',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


# ===========================================================================
# PBI-12 Service Tests
# ===========================================================================

class PBI12ServiceTest(APITestCase):

    def setUp(self):
        self.staff = make_user('staff3@ksb.com', role=UserRole.STAFF)
        self.member_user = make_user('activemember@ksb.com', role=UserRole.MEMBER)
        self.profile = self.member_user.member_profile
        self.profile.status = MemberStatus.ACTIVE
        self.profile.member_id = '#MBR-00001'
        self.profile.save()

    def _make_wajib(self):
        return make_saving(self.member_user, SavingType.WAJIB, 100000)

    def _make_sukarela(self):
        return make_saving(self.member_user, SavingType.SUKARELA, 250000)

    # --- WAJIB APPROVE ---

    def test_approve_wajib_saving_status_becomes_success(self):
        saving = self._make_wajib()
        result = process_deposit_verification(saving=saving, staff=self.staff, action='approve')
        saving.refresh_from_db()
        self.assertEqual(saving.status, SavingStatus.SUCCESS)
        self.assertEqual(result['action'], 'approved')

    def test_approve_sukarela_saving_status_becomes_success(self):
        saving = self._make_sukarela()
        result = process_deposit_verification(saving=saving, staff=self.staff, action='approve')
        saving.refresh_from_db()
        self.assertEqual(saving.status, SavingStatus.SUCCESS)
        self.assertEqual(result['action'], 'approved')

    # --- REVIEW SETORAN (amount override) ---

    def test_reviewed_amount_overrides_original_amount(self):
        saving = self._make_sukarela()
        original = saving.amount
        new_amount = Decimal('300000.00')
        result = process_deposit_verification(
            saving=saving,
            staff=self.staff,
            action='approve',
            reviewed_amount=new_amount,
        )
        saving.refresh_from_db()
        self.assertEqual(saving.amount, new_amount)
        self.assertNotEqual(saving.amount, original)
        self.assertEqual(result['final_amount'], str(new_amount))

    def test_reviewed_amount_logged(self):
        saving = self._make_wajib()
        new_amount = Decimal('150000.00')
        process_deposit_verification(
            saving=saving,
            staff=self.staff,
            action='approve',
            reviewed_amount=new_amount,
        )
        log = VerificationLog.objects.filter(saving_transaction=saving).first()
        self.assertEqual(log.reviewed_amount, new_amount)

    # --- REJECT ---

    def test_reject_wajib_saving_status_becomes_rejected(self):
        saving = self._make_wajib()
        process_deposit_verification(
            saving=saving, staff=self.staff, action='reject',
            rejection_reason='Rekening tidak sesuai'
        )
        saving.refresh_from_db()
        self.assertEqual(saving.status, SavingStatus.REJECTED)

    def test_reject_stores_reason(self):
        saving = self._make_sukarela()
        reason = 'Bukti buram'
        process_deposit_verification(
            saving=saving, staff=self.staff, action='reject', rejection_reason=reason
        )
        saving.refresh_from_db()
        self.assertEqual(saving.rejection_reason, reason)

    # --- GUARDS ---

    def test_cannot_approve_already_confirmed(self):
        saving = make_saving(self.member_user, SavingType.WAJIB, 100000, SavingStatus.SUCCESS)
        with self.assertRaises(ValueError):
            process_deposit_verification(saving=saving, staff=self.staff, action='approve')

    def test_cannot_process_pokok_in_deposit_service(self):
        saving = make_saving(self.member_user, SavingType.POKOK)
        with self.assertRaises(ValueError):
            process_deposit_verification(saving=saving, staff=self.staff, action='approve')

    def test_zero_reviewed_amount_raises_error(self):
        saving = self._make_wajib()
        from rest_framework.exceptions import ValidationError
        from verifications.serializers import DepositConfirmSerializer
        s = DepositConfirmSerializer(data={
            'action': 'approve', 'reviewed_amount': 0
        })
        self.assertFalse(s.is_valid())


# ===========================================================================
# PBI-12 API Tests
# ===========================================================================

class PBI12APITest(APITestCase):

    def setUp(self):
        self.staff = make_user('staff4@ksb.com', role=UserRole.STAFF)
        self.member_user = make_user('activem@ksb.com', role=UserRole.MEMBER)
        profile = self.member_user.member_profile
        profile.status = MemberStatus.ACTIVE
        profile.member_id = '#MBR-99999'
        profile.save()
        self.wajib_saving = make_saving(self.member_user, SavingType.WAJIB, 100000)
        self.sukarela_saving = make_saving(self.member_user, SavingType.SUKARELA, 200000)

    def _url_queue(self):
        return reverse('deposit-queue')

    def _url_confirm(self, pk):
        return reverse('deposit-confirm', kwargs={'pk': pk})

    def _url_detail(self, pk):
        return reverse('deposit-detail', kwargs={'pk': pk})

    def test_queue_returns_pending_deposits(self):
        resp = self.client.get(self._url_queue(), **auth_headers(self.staff))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['count'], 2)

    def test_queue_filter_by_saving_type(self):
        resp = self.client.get(
            self._url_queue() + '?saving_type=WAJIB',
            **auth_headers(self.staff)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['saving_type'], 'WAJIB')

    def test_detail_shows_full_transaction(self):
        resp = self.client.get(
            self._url_detail(self.wajib_saving.pk),
            **auth_headers(self.staff)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['saving_type'], 'WAJIB')

    def test_confirm_approve_wajib(self):
        resp = self.client.post(
            self._url_confirm(self.wajib_saving.pk),
            {'action': 'approve'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['action'], 'approved')

    def test_confirm_approve_with_reviewed_amount(self):
        resp = self.client.post(
            self._url_confirm(self.sukarela_saving.pk),
            {'action': 'approve', 'reviewed_amount': '250000.00'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['final_amount'], '250000.00')

    def test_confirm_reject_requires_reason(self):
        resp = self.client.post(
            self._url_confirm(self.wajib_saving.pk),
            {'action': 'reject'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_reject_with_reason(self):
        resp = self.client.post(
            self._url_confirm(self.sukarela_saving.pk),
            {'action': 'reject', 'rejection_reason': 'Nominal kurang'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['action'], 'rejected')

    def test_member_cannot_access_confirm_endpoint(self):
        resp = self.client.post(
            self._url_confirm(self.wajib_saving.pk),
            {'action': 'approve'},
            format='json',
            **auth_headers(self.member_user),
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_confirm_already_confirmed(self):
        # Approve once
        self.client.post(
            self._url_confirm(self.wajib_saving.pk),
            {'action': 'approve'},
            format='json',
            **auth_headers(self.staff),
        )
        # Try again
        resp = self.client.post(
            self._url_confirm(self.wajib_saving.pk),
            {'action': 'approve'},
            format='json',
            **auth_headers(self.staff),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)