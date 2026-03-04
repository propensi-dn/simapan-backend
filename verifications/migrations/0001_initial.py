import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('savings', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[('APPROVE', 'Approve'), ('REJECT', 'Reject')],
                    max_length=10,
                )),
                ('rejection_reason', models.TextField(blank=True)),
                ('reviewed_amount', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Amount after staff review/edit (if different from submitted)',
                    max_digits=14,
                    null=True,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('saving_transaction', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='verification_logs',
                    to='savings.savingtransaction',
                )),
                ('staff', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='verification_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]