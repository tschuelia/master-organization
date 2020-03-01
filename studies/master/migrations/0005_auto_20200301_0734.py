# Generated by Django 3.0.3 on 2020-03-01 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0004_auto_20200301_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='max_ects_creditable',
            field=models.IntegerField(blank=True, default=-1, verbose_name='Maximale Anzahl anrechenbarer ECTS'),
        ),
        migrations.AlterField(
            model_name='category',
            name='min_ects_required',
            field=models.IntegerField(blank=True, default=-1, verbose_name='Minimal nötige Anzahl ECTS in diesem Bereich'),
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='max_ects_creditable',
            field=models.IntegerField(blank=True, default=-1, verbose_name='Maximale Anzahl anrechenbarer ECTS'),
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='min_ects_required',
            field=models.IntegerField(blank=True, default=-1, verbose_name='Minimal nötige Anzahl ECTS in dieser Kategorie'),
        ),
    ]
