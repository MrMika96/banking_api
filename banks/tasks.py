import logging

from django.apps import apps
from forex_python.converter import CurrencyRates

from practice_2.celery import app


@app.task(default_retry_delay=600, max_retrues=7)
def update_currency_rates():
    logger = logging.getLogger(__name__)
    logger.info(msg="Execute change_expiration_status_for_card")
    rates = CurrencyRates()
    Currency = apps.get_model('banks', 'Currency')
    currencies = Currency.objects.all()
    for currency in currencies:
        for rate in currency.rates:
            currency.rates[rate] = rates.get_rate(currency.name, rate)
        currency.save(update_fields=['rate'])
    logger.info(msg="Complete!")
