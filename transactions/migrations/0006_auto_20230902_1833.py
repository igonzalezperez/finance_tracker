from django.db import migrations


def set_created_at(apps, schema_editor):
    Transaction = apps.get_model("transactions", "Transaction")
    for transaction in Transaction.objects.all():
        transaction.created_at = transaction.date
        transaction.save()


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0005_transaction_created_at"),
    ]

    operations = [
        migrations.RunPython(set_created_at),
    ]
