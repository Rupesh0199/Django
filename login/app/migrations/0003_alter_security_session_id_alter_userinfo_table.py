# Generated by Django 4.0.6 on 2022-07-19 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_security_role_type_userinfo_role_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='session_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterModelTable(
            name='userinfo',
            table='userinfo',
        ),
    ]