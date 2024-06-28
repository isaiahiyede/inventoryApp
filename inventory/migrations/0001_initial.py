# Generated by Django 5.0.3 on 2024-06-28 08:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('date_added', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Suppliers',
                'ordering': ['-date_added'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ('role', models.CharField(blank=True, max_length=255, null=True)),
                ('apikey', models.CharField(blank=True, max_length=50, null=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('employee', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, null=True)),
                ('description', models.CharField(max_length=500, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6, null=True)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('supplier', models.ManyToManyField(to='inventory.supplier')),
            ],
            options={
                'verbose_name_plural': 'Items',
                'ordering': ['-date_added'],
            },
        ),
    ]