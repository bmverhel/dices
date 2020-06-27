# Generated by Django 3.0.7 on 2020-06-13 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speechdb', '0006_speech_part'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speech',
            name='addr',
            field=models.ManyToManyField(blank=True, related_name='addresses', to='speechdb.CharacterInstance'),
        ),
    ]
