# Generated by Django 5.1.3 on 2024-11-25 18:44

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enterprise_name', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(max_length=255, unique=True)),
                ('type_enterprise', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Pollutant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pollutant_name', models.CharField(max_length=255, unique=True)),
                ('danger_class', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)])),
                ('GDK', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1980), django.core.validators.MaxValueValidator(2100)])),
                ('type', models.CharField(max_length=255)),
                ('volume', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('enterprise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='main.enterprise')),
                ('pollutant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='main.pollutant')),
            ],
            options={
                'unique_together': {('year', 'enterprise', 'pollutant')},
            },
        ),
    ]
