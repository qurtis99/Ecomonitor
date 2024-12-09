from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Pollutant(models.Model):
    # Існуючі поля
    pollutant_name = models.CharField(max_length=255, unique=True)
    danger_class = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    GDK = models.FloatField(validators=[MinValueValidator(0)])
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    CANCEROGENIC_CHOICES = [
        ('cancerogenic', 'Канцерогенний'),
        ('non_cancerogenic', 'Неканцерогенний'),
    ]
    cancer_risk_type = models.CharField(max_length=20,choices=CANCEROGENIC_CHOICES, default='non_cancerogenic')
    rfc = models.FloatField(validators=[MinValueValidator(0.0)],verbose_name="RFC середньодобова концентрація",default = 0.0)


    def update_related_records(self, danger_class_changed=False):
        from .models import Record
        records = Record.objects.filter(pollutant=self)

        if danger_class_changed:
            storage_records = records.filter(
                type__in=[
                    "Викиди в атмосферне повітря",
                    "Викиди в водні об'єкти",
                    "Викиди в водні об'єкти (Озера)",
                    "Зберігання речовин у спеціально відведених місцях",
                    "Зберігання речовин в межах населеного пункту",
                    "Створення радіоактивних речовин (Високоактивних)",
                    "Створення радіоактивних речовин (Середньоактивні та низькоактивні)",
                ]
            )
            for record in storage_records:
                record.calculated_tax = record.calculate_tax()
                record.save()
        else:
            # Оновлюємо для інших типів (крім "Зберігання...")
            non_storage_records = records.exclude(
                type__in=[
                    "Зберігання речовин у спеціально відведених місцях",
                    "Зберігання речовин в межах населеного пункту"
                ]
            )
            non_storage_records.update(
                tax_rate=self.tax_rate
            )
            # Оновлюємо calculated_tax для non-storage записів
            for record in non_storage_records:
                record.calculated_tax = record.calculate_tax()
                record.save()

    def save(self, *args, **kwargs):
        # Перевіряємо, чи змінився клас небезпеки
        danger_class_changed = False
        if self.pk:
            old_instance = Pollutant.objects.get(pk=self.pk)
            if old_instance.danger_class != self.danger_class:
                danger_class_changed = True

        super().save(*args, **kwargs)  # Зберігаємо модель

        # Оновлюємо пов'язані записи
        self.update_related_records(danger_class_changed=danger_class_changed)

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
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    calculated_tax = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    # Нові поля
    risk_type = models.CharField(max_length=20, default='non_cancerogenic')  # Канцерогенний або неконцерогенний
    current_risk = models.FloatField(default=0.0)  # Рівень ризику
    risk_level = models.CharField(max_length=20, default='low')  # Низький, середній, високий

    class Meta:
        unique_together = ('year', 'enterprise', 'pollutant')

    def calculate_tax(self):
        """Обчислює податок залежно від типу забруднення."""
        base_rate = self.pollutant.tax_rate
        if self.type == "Викиди в атмосферне повітря":
            return self.volume * base_rate
        elif self.type == "Викиди в водні об'єкти":
            return self.volume * base_rate
        elif self.type == "Викиди в водні об'єкти (Озера)":
            return self.volume * base_rate * 1.5
        elif self.type == "Зберігання речовин у спеціально відведених місцях":
            if self.pollutant.danger_class == 1:
                return self.volume * 1546.22
            elif self.pollutant.danger_class == 2:
                return self.volume * 56.32
            elif self.pollutant.danger_class == 3:
                return self.volume * 14.12
            elif self.pollutant.danger_class == 4:
                return self.volume * 5.50
        elif self.type == "Зберігання речовин в межах населеного пункту":
            if self.pollutant.danger_class == 1:
                return self.volume * 1546.22 *3
            elif self.pollutant.danger_class == 2:
                return self.volume * 56.32 * 3
            elif self.pollutant.danger_class == 3:
                return self.volume * 14.12 * 3
            elif self.pollutant.danger_class == 4:
                return self.volume * 5.50 * 3
        elif self.type == "Створення радіоактивних речовин (Високоактивних)":
            return self.volume * base_rate * 50
        elif self.type == "Створення радіоактивних речовин (Середньоактивні та низькоактивні)":
            return self.volume * base_rate * 2
        return 0.0

    def calculate_risk(self):
        concentration = self.volume / 365
        if self.pollutant.cancer_risk_type == 'cancerogenic':
            self.current_risk = (concentration * 20 * 365 * 70) / (70 * 70 * 365)
            self.risk_type = 'cancerogenic'
        else:
            self.current_risk = concentration / self.pollutant.rfc
            self.risk_type = 'non_cancerogenic'

        if self.pollutant.cancer_risk_type == 'cancerogenic':
            # Визначення рівня ризику
            if self.current_risk < 1:
                self.risk_level = 'low'
            elif 1 <= self.current_risk < 10:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'high'
        else:
            # Визначення рівня ризику
            if self.current_risk < 1:
                self.risk_level = 'low'
            elif 1 <= self.current_risk < 10:
                self.risk_level = 'medium'
            else:
                self.risk_level = 'high'


    def save(self, *args, **kwargs):
        self.tax_rate = self.pollutant.tax_rate
        self.calculated_tax = self.calculate_tax()
        self.calculate_risk()  # Додаємо обчислення ризику
        super().save(*args, **kwargs)




    class Meta:
        unique_together = ('year', 'enterprise', 'pollutant')


    def __str__(self):
        return f"Record for {self.enterprise.enterprise_name} in {self.year}"




