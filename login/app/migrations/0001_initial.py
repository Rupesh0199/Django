# Generated by Django 4.0.6 on 2022-07-18 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Security',
            fields=[
                ('session_id', models.IntegerField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=255)),
                ('auth_key', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('user_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
    ]
