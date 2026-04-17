from django.db import models


class CooperativeBank(models.Model):
    bank_name      = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=150)
    is_active      = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cooperative Bank Account'

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class LandingPageConfig(models.Model):
    title = models.CharField(max_length=255, default="Mewujudkan Masa Depan Keuangan Anda Bersama")
    brand_name = models.CharField(max_length=100, default="SI-MAPAN")
    description = models.TextField(default="Platform aman dan transparan untuk mengelola simpan pinjam masyarakat.")
    hero_image = models.ImageField(upload_to='config/hero/', null=True, blank=True)
    cta_text = models.CharField(max_length=50, default="Daftar sebagai Anggota")

    class Meta:
        verbose_name = "Landing Page Configuration"
        verbose_name_plural = "Landing Page Configuration"

    def __str__(self):
        return "Landing Page Content"

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text="Nama icon (misal: 'pi-wallet')")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class AboutConfig(models.Model):
    vision = models.TextField()
    mission = models.TextField()

    class Meta:
        verbose_name = "About Us Configuration"

    def __str__(self):
        return "Visi & Misi"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question
