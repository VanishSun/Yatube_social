from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.urls import reverse_lazy
from .forms import CreationForm, ContactForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


def send_msg(email, name, subject, message):
    subject = f"Письмо от {name}"
    body = f""" {subject})

    Имя: {name}
    Адрес почты: {email}
    Тема: {subject}
    Сообдение: {message}

    """
    send_mail(
        subject, body, email, ["vanish.sun@gmail.com"],
    )


def user_contact(request):
    if request.method == 'POST':

        form = ContactForm(request.POST)

        if form.is_valid():
            send_msg(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['body'],
            )

            return redirect('thank-you',)

        return render(request, 'users/contact.html', {'form': form})

    form = ContactForm()
    return render(request, 'users/contact.html', {'form': form})


class Thanks(TemplateView):
    template_name = "users/thank-you.html"
