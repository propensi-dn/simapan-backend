from decimal import Decimal
from django.utils import timezone
from dateutil.relativedelta import relativedelta


def calculate_credit_score(member) -> dict:
    """
    Simple credit scoring based on payment history.
    Score range: 300 - 850
    """
    score = 700
    loans = member.loans.exclude(status='PENDING')

    has_active_overdue = False

    for loan in loans:
        for installment in loan.installments.all():
            if installment.status == 'PAID':
                score += 10
            elif installment.status == 'UNPAID' and installment.due_date < timezone.now().date():
                score -= 30
                has_active_overdue = True

        if hasattr(loan, 'bad_debt'):
            score -= 100

    if not has_active_overdue:
        score += 50

    score = max(300, min(850, score))

    if score >= 750:
        label = 'Excellent'
    elif score >= 650:
        label = 'Good'
    elif score >= 500:
        label = 'Fair'
    else:
        label = 'Poor'

    return {'score': score, 'label': label}


def has_bad_debt(member) -> bool:
    """Cek apakah member punya kredit macet aktif"""
    from loans.models import BadDebt
    return BadDebt.objects.filter(loan__member=member).exists()


def simulate_installment(amount: Decimal, tenor: int) -> dict:
    """
    Simulasi cicilan flat rate 0.5% per bulan
    """
    INTEREST_RATE = Decimal('0.005')
    total_interest = amount * INTEREST_RATE * tenor
    total_repayment = amount + total_interest
    monthly = total_repayment / tenor
    principal_per_month = amount / tenor
    interest_per_month = amount * INTEREST_RATE

    return {
        'principal': amount,
        'interest_rate': float(INTEREST_RATE * 100),
        'interest_per_month': round(interest_per_month, 2),
        'principal_per_month': round(principal_per_month, 2),
        'monthly_installment': round(monthly, 2),
        'total_interest': round(total_interest, 2),
        'total_repayment': round(total_repayment, 2),
        'tenor': tenor,
    }


def generate_installment_schedule(loan) -> list:
    """
    Generate jadwal cicilan berdasarkan loan.
    Disbursed date = hari ini, cicilan pertama = 1 bulan setelah pencairan.
    """
    INTEREST_RATE = Decimal('0.005')
    principal_per_month = loan.amount / loan.tenor
    interest_per_month = loan.amount * INTEREST_RATE
    monthly_amount = principal_per_month + interest_per_month

    start_date = loan.disbursed_at.date() if loan.disbursed_at else timezone.now().date()

    schedule = []
    for i in range(1, loan.tenor + 1):
        due_date = start_date + relativedelta(months=i)
        schedule.append({
            'installment_number': i,
            'due_date': due_date,
            'amount': round(monthly_amount, 2),
            'principal_component': round(principal_per_month, 2),
            'interest_component': round(interest_per_month, 2),
        })

    return schedule


def create_installments(loan):
    """Buat record Installment setelah loan dicairkan"""
    from loans.models import Installment

    schedule = generate_installment_schedule(loan)
    installments = []

    for item in schedule:
        installments.append(Installment(
            loan=loan,
            installment_number=item['installment_number'],
            due_date=item['due_date'],
            amount=item['amount'],
            principal_component=item['principal_component'],
            interest_component=item['interest_component'],
        ))

    Installment.objects.bulk_create(installments)
    return installments