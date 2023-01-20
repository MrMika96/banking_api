from django.shortcuts import get_object_or_404

from banks.models import Bank, PaymentSystem


def get_payment_numbers(number):
    split_number = list(number)
    payment_number = split_number[0]
    bank_number = ""
    for i in range(1, 7):
        bank_number = bank_number + split_number[i]
    bank = get_object_or_404(Bank, number=bank_number)
    payment_system = get_object_or_404(PaymentSystem, number=payment_number)
    # return bank, payment_system
    return bank