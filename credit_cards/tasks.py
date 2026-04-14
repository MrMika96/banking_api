"""Module with celery tasks for credit card app."""
import logging

from django.apps import apps
from django.utils import timezone

from banking_api.celery import app


@app.task
def change_expiration_status_for_card():
    """Task what changes credit card expiration date."""
    logger = logging.getLogger(__name__)
    logger.info(msg="Execute change_expiration_status_for_card")
    CreditCard = apps.get_model("credit_cards", "CreditCard") # noqa N806
    expired_cards = CreditCard.objects.filter(
        expiration_date__lte=timezone.now().date()
    )
    expired_cards.update(is_expired=True)
    logger.info(msg=f"Complete! Cards updated: {expired_cards.count()}")
