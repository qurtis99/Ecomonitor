from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Pollutant(models.Model):
    pollutant_name = models.CharField(max_length=255, unique=True)
    danger_class = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    GDK = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.pollutant_name


class Enterprise(models.Model):
    enterprise_name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, unique=True)
    type_enterprise = models.CharField(max_length=255)

    def __str__(self):
        return self.enterprise_name

class Record(models.Model):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='records')
    pollutant = models.ForeignKey(Pollutant, on_delete=models.CASCADE, related_name='records')
    year = models.IntegerField(validators=[MinValueValidator(1980), MaxValueValidator(2100)])
    type = models.CharField(max_length=255)
    volume = models.FloatField(validators=[MinValueValidator(0)])

    class Meta:
        unique_together =('year','enterprise','pollutant')

    def __str__(self):
        return f"Record for {self.enterprise.enterprise_name} in {self.year}"




