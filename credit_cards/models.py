from django.db import models

from banks.models import Bank, PaymentSystem
from users.models import User


class CreditCard(models.Model):
    owner = models.ForeignKey(User, related_name="credit_cards", on_delete=models.CASCADE)
    number = models.CharField(max_length=19, blank=False, null=False)
    expiration_date = models.DateField(blank=False, null=False)
    cvv = models.IntegerField()
    bank = models.ForeignKey(Bank, related_name="cards", on_delete=models.CASCADE)
    payment_system = models.ForeignKey(PaymentSystem, related_name="cards", on_delete=models.CASCADE)

    class Meta:
        db_table = "credit_cards"
