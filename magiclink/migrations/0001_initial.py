# Generated by Django 3.2.3 on 2021-05-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MagicLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('token', models.TextField()),
                ('expiry', models.DateTimeField()),
                ('redirect_url', models.TextField()),
                ('disabled', models.BooleanField(default=False)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
