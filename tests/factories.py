"""factory_boy factories for SEBMS tests."""
import datetime

import factory
from django.contrib.auth import get_user_model

from SDO.models import Tariff
from bill.models import Bill
from consumer.models import Consumer
from meterreader.models import Meter, MeterReading

User = get_user_model()
PASSWORD = "Str0ngPass!x"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@sebms.test")
    password = factory.PostGenerationMethodCall("set_password", PASSWORD)
    is_active = True


class SDOUserFactory(UserFactory):
    is_sdo = True


class OfficeStaffUserFactory(UserFactory):
    is_office_staff = True


class MeterReaderUserFactory(UserFactory):
    is_meter_reader = True


class ConsumerUserFactory(UserFactory):
    is_consumer = True


class TariffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tariff
        django_get_or_create = ("tariff_type",)

    tariff_type = "domestic"
    price_100 = 3
    price_200 = 4
    price_300 = 5
    price_above = 6


class ConsumerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Consumer

    user = factory.SubFactory(ConsumerUserFactory)
    consumer_number = factory.Sequence(lambda n: f"C{n:06d}")
    consumer_name = factory.Sequence(lambda n: f"Consumer {n}")
    consumer_address = factory.Sequence(lambda n: f"House {n}, Street {n}")
    consumer_tariff = factory.SubFactory(TariffFactory)
    consumer_division = "division1"
    approved = True


class UnapprovedConsumerFactory(ConsumerFactory):
    approved = False


class MeterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meter

    meter_number = factory.Sequence(lambda n: 100000 + n)
    meter_type = "single"
    consumer = factory.SubFactory(ConsumerFactory)


class MeterReadingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MeterReading

    meter = factory.SubFactory(MeterFactory)
    last_reading = 500
    new_reading = 700
    reading_date = factory.Sequence(
        lambda n: datetime.date(2026, 1, 1) + datetime.timedelta(days=n)
    )
    processed = False
    meter_status = True


class BillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bill

    billmonth = datetime.date(2026, 1, 15)
    duedate = datetime.date(2026, 1, 30)
    detectionunit = 0
    averageunit = 0
    units = 200
    unitsconsumed = 200
    payableamount = 700
    payable_after_due_date = 770
    meter = factory.SubFactory(MeterFactory)
    paid = False
