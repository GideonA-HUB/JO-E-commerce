# Generated by Django 4.2.7 on 2025-07-19 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_contactmessage_alter_cateringservice_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='delivery_address',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='customer_email',
            new_name='email',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='customer_phone',
            new_name='phone',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='payment_intent_id',
            new_name='stripe_payment_intent_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='customer_name',
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_instructions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(default='Unknown', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(default='Unknown', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='zip_code',
            field=models.CharField(default='00000', max_length=20),
            preserve_default=False,
        ),
    ]
