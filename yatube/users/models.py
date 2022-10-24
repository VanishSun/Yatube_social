from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Адрес почты')
    subject = models.CharField(max_length=100, verbose_name='Тема')
    body = models.TextField(verbose_name='Текст')
    is_answered = models.BooleanField(default=False, verbose_name='Отвечено')

    class Meta:
        verbose_name = 'Контакт'
