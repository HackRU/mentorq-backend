# Generated by Django 3.0.8 on 2020-10-03 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorq_api', '0005_merge_20201003_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='owner',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
