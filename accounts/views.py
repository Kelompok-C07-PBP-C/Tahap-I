"""Authentication views."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from .forms import LoginForm, RegistrationForm


class AuthLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return reverse("home")


class AuthLogoutView(LogoutView):
    next_page = reverse_lazy("auth:login")


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("auth:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful. Please log in.")
        return super().form_valid(form)
