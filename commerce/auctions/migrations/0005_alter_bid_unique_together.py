# Generated by Django 4.1.6 on 2023-02-18 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0004_alter_bid_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="bid",
            unique_together={("user", "item")},
        ),
    ]
