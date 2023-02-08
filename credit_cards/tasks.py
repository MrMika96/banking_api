import logging
from datetime import datetime

from django.apps import apps

from practice_2.celery import app


@app.task
def change_expiration_status_for_card():
    logger = logging.getLogger(__name__)
    logger.info(msg="Execute change_expiration_status_for_card")
    CreditCard = apps.get_model('credit_cards', 'CreditCard')
    expired_cards = CreditCard.objects.filter(
        expiration_date__lte=datetime.utcnow().date()
    )
    expired_cards.update(is_expired=True)
    logger.info(msg=f"Complete! Cards updated: {expired_cards.count()}")
