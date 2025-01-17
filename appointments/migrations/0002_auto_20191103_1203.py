# Generated by Django 2.2.6 on 2019-11-03 12:03

from django.db import migrations, models
import django.db.models.deletion
import django_multitenant.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('appointments', '0001_initial'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='client',
            field=django_multitenant.fields.TenantForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer'),
        ),
    ]
