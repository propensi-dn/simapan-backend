import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simapan.settings')

import django

django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('DROP SCHEMA IF EXISTS public CASCADE;')
    cursor.execute('CREATE SCHEMA public;')
    cursor.execute('GRANT ALL ON SCHEMA public TO public;')

print('Database schema reset complete.')
