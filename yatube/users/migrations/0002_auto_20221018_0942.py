# Generated by Django 2.2.16 on 2022-10-18 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name': 'Контакт'},
        ),
        migrations.AlterField(
            model_name='contact',
            name='body',
            field=models.TextField(verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Адрес почты'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='is_answered',
            field=models.BooleanField(default=False, verbose_name='Отвечено'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject',
            field=models.CharField(max_length=100, verbose_name='Тема'),
        ),
    ]
