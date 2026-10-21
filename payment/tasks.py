"""Celery tasks for the payment app."""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=60,
    time_limit=90,
    acks_late=True,
)
def send_payment_receipt_email(self, bill_id: int, payment_id: int):
    """Email the consumer a payment receipt (off the request thread)."""
    from payment.models import Payment

    try:
        payment = Payment.objects.select_related(
            "bill", "bill__meter", "bill__meter__consumer", "bill__meter__consumer__user"
        ).get(pk=payment_id)
        bill = payment.bill
        if bill is None or bill.id != bill_id:
            logger.warning("Receipt task refs mismatched bill %s/payment %s", bill_id, payment_id)
            return {"sent": False}

        consumer = bill.meter.consumer if bill.meter else None
        recipient = (
            consumer.user.email if consumer and consumer.user_id else None
        )
        if not recipient:
            logger.warning("No recipient email for bill %s", bill_id)
            return {"sent": False}

        send_mail(
            subject=f"[SEBMS] Payment receipt for bill #{bill.id}",
            message=(
                f"Your payment of Rs. {payment.amount} for bill #{bill.id} "
                f"(reference {payment.reference}) has been received.\n"
                f"Bill amount: Rs. {bill.payableamount}\n"
                f"Paid on: {payment.created_at}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
        )
        logger.info("Receipt emailed for bill %s to %s", bill_id, recipient)
        return {"sent": True, "to": recipient}
    except Exception as exc:
        logger.exception("send_payment_receipt_email failed for bill %s", bill_id)
        raise self.retry(exc=exc)
