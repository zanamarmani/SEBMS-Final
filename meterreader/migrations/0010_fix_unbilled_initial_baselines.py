from django.db import migrations
from django.db.models import Exists, OuterRef


def reset_unbilled_initial_baselines(apps, schema_editor):
    Reading = apps.get_model('meterreader', 'MeterReading')
    Bill = apps.get_model('bill', 'Bill')
    earlier = Reading.objects.filter(
        meter_id=OuterRef('meter_id'), reading_date__lt=OuterRef('reading_date')
    )
    billed = Bill.objects.filter(meter_id=OuterRef('meter_id'))
    Reading.objects.filter(
        processed=False, last_reading=500, meter_id__isnull=False,
        reading_date__isnull=False,
    ).annotate(has_earlier=Exists(earlier), has_bill=Exists(billed)).filter(
        has_earlier=False, has_bill=False,
    ).update(last_reading=0)


class Migration(migrations.Migration):
    dependencies = [
        ('meterreader', '0009_alter_meterreading_last_reading'),
        ('bill', '0003_bill_bill_meter_month_idx_bill_bill_paid_idx_and_more'),
    ]
    operations = [migrations.RunPython(reset_unbilled_initial_baselines, migrations.RunPython.noop)]
