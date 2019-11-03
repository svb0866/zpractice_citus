# Generated by Django 2.2.6 on 2019-11-03 12:03

import ckeditor.fields
import clients.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_clamd.validators
import django_multitenant.fields
import django_multitenant.mixins
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50)),
                ('suffix', models.CharField(blank=True, max_length=10, null=True)),
                ('preferred_name', models.CharField(blank=True, max_length=50, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('client_minor', models.BooleanField(blank=True, default=False)),
                ('send_text_appointment_reminders', models.BooleanField(blank=True, default=False)),
                ('send_email_appointment_reminders', models.BooleanField(blank=True, default=False)),
                ('billing_type', models.CharField(blank=True, choices=[('self', 'Self Pay'), ('insurance', 'Insurance')], default='self', max_length=15)),
                ('referred_by', models.CharField(blank=True, max_length=50, null=True)),
                ('phone1', models.CharField(blank=True, max_length=20, null=True)),
                ('text_message_consent_1', models.BooleanField(blank=True, default=False)),
                ('phone2', models.CharField(blank=True, max_length=20, null=True)),
                ('text_message_consent_2', models.BooleanField(blank=True, default=False)),
                ('phone3', models.CharField(blank=True, max_length=20, null=True)),
                ('text_message_consent_3', models.BooleanField(blank=True, default=False)),
                ('primary_email', models.EmailField(max_length=50, unique=True)),
                ('primary_email_consent', models.BooleanField(blank=True, default=False)),
                ('secondary_email', models.EmailField(blank=True, max_length=50, null=True)),
                ('secondary_email_consent', models.BooleanField(blank=True, default=False)),
                ('access_client_portal', models.BooleanField(blank=True, default=True)),
                ('sex', models.CharField(blank=True, max_length=20, null=True)),
                ('relationship_status', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('zip', models.CharField(blank=True, max_length=6, null=True)),
                ('emergency_first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('emergency_last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('emergency_relation', models.CharField(blank=True, max_length=20, null=True)),
                ('emergency_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('emergency_email', models.CharField(blank=True, max_length=50, null=True)),
                ('emergency_phone_type', models.CharField(blank=True, max_length=20, null=True)),
                ('insurance_company', models.CharField(blank=True, max_length=50, null=True)),
                ('group_id', models.CharField(blank=True, max_length=50, null=True)),
                ('plan_id', models.CharField(blank=True, max_length=50, null=True)),
                ('member_id', models.CharField(blank=True, max_length=50, null=True)),
                ('client_relationship_to_insured', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_sex', models.CharField(blank=True, max_length=20, null=True)),
                ('insured_birth_date', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_phone', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_address', models.CharField(blank=True, max_length=500, null=True)),
                ('insured_city', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_state', models.CharField(blank=True, max_length=50, null=True)),
                ('insured_zip', models.CharField(blank=True, max_length=6, null=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('client_user_obj', django_multitenant.fields.TenantForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
            ],
            options={
                'permissions': (('can_view', 'Can View'), ('can_edit', 'Can Edit'), ('can_add', 'Can Add'), ('can_delete', 'Can Add'), ('can_notes', 'Can View Notes')),
                'unique_together': {('id', 'customer')},
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EmailTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_reminder', ckeditor.fields.RichTextField(blank=True, default='<p>Dear {{client_name}}</p>\n\n<p>This is just a reminder for\xa0appointment with {{assigned_clinician}}\xa0,\xa0 scheduled on {{appointment_date_time}}. Please be present at the clinic at least 15 minutes in advance to complete the appointment procedures.</p>\xa0\n\n<p>Warm Regards,</p>\n<p>{{your_name}}</p>', max_length=10000, null=True)),
                ('new_appointment', ckeditor.fields.RichTextField(blank=True, default='<p>Dear {{client_name}}</p>\n\n<p>Your appointment with {{assigned_clinician}} is scheduled on {{appointment_date_time}}. Please be present at the clinic at least 15 minutes in advance to complete the appointment procedures.</p>\xa0\n\n<p>Warm Regards,</p>\n<p>{{your_name}}</p>', max_length=10000, null=True)),
                ('appointment_reschedule', ckeditor.fields.RichTextField(blank=True, default='<p>Dear {{client_name}}</p>\n\n<p>Your appointment with {{assigned_clinician}}\xa0,\xa0 scheduled on {{old_appointment_date_time}}. Has been rescheduled to{{new_appointment_date_time}}.\xa0Please be present at the clinic at least 15 minutes in advance to complete the appointment procedures. Please dont hesitate to get in touch with us for more details.</p>\n\n\n\n<p>warm regards,</p>\n<p>{{your_name}}</p>', max_length=10000, null=True)),
                ('appointment_canceled', ckeditor.fields.RichTextField(blank=True, default='<p>Dear {{client_name}}</p>\n\n<p>Your appointment with {{assigned_clinician}}\xa0,\xa0 scheduled on {{appointment_date_time}}. Has been canceled. Please dont hesitate to get in touch with us for more details.</p>\n\n\n\n<p>warm regards,</p>\n\n<p> {{your_name}} </p>', max_length=10000, null=True)),
                ('client_onboarding', ckeditor.fields.RichTextField(blank=True, default='<p>Dear {{client_name}}</p>\n\n<p><br />\nYour registration with our practice is completed Your access to the client portal is<br />\n{{access_credential}}</p>\n\n<p><br />\nPlease log in to the portal and update your intake details, your onetime password will expire in 12 hours, you will be able to change your password during your first login.<br/>Please do not hesitate to contact us in case you face any issues.</p>\n\n<p>warm regards,</p>\n\n<p>{{your_name}}</p>', max_length=10000, null=True)),
                ('email_reminder_setting', models.CharField(choices=[('12', '12 Hours'), ('24', '24 Hours'), ('48', '48 Hours'), ('None', 'Manually Send')], default='None', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClientNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('client_note_title', models.CharField(max_length=500)),
                ('client_note_body', ckeditor.fields.RichTextField(blank=True, max_length=5000, null=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('client', django_multitenant.fields.TenantForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ClientFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('file', models.FileField(upload_to=clients.models.upload_path, validators=[django_clamd.validators.validate_file_infection])),
                ('file_name', models.CharField(max_length=50)),
                ('uploaded_by', models.CharField(max_length=50)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('client', django_multitenant.fields.TenantForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ClientEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('subject', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=1000)),
                ('sent_by', models.CharField(max_length=50)),
                ('sent_from_email', models.CharField(max_length=50)),
                ('sent_to_email', models.CharField(max_length=50)),
                ('sent_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(max_length=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(django_multitenant.mixins.TenantModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ClientAdministrativeNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('administrative_note_body', ckeditor.fields.RichTextField(blank=True, max_length=5000, null=True)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified_by', models.CharField(blank=True, max_length=50, null=True)),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='clients.Client')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUserObjectPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Permission')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'unique_together': {('user', 'permission', 'content_object')},
            },
        ),
        migrations.CreateModel(
            name='ProjectGroupObjectPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Permission')),
            ],
            options={
                'abstract': False,
                'unique_together': {('group', 'permission', 'content_object')},
            },
        ),
    ]