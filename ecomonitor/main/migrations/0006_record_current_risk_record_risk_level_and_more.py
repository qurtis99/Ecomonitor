# Generated by Django 5.1.3 on 2024-12-09 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_pollutant_cancer_risk_type_pollutant_rfc'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='current_risk',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='record',
            name='risk_level',
            field=models.CharField(default='low', max_length=20),
        ),
        migrations.AddField(
            model_name='record',
            name='risk_type',
            field=models.CharField(default='non_cancerogenic', max_length=20),
        ),
    ]