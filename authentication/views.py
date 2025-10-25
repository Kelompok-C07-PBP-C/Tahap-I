"""Authentication views."""
from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from interaksi.models import Wishlist
from katalog.filters import VenueFilter
from manajemen_lapangan.models import Venue
from rent.models import Booking, Payment

from .forms import LoginForm, RegistrationForm
from .mixins import AdminRequiredMixin, EnsureCsrfCookieMixin


class AuthLoginView(LoginView):
    template_name = "authentication/login.html"
    authentication_form = LoginForm

    def get_success_url(self) -> str:
        return reverse("home")


class AuthLogoutView(LoginRequiredMixin, View):
    """Log out the current user and redirect them to the login page."""

    success_url = reverse_lazy("authentication:login")

    def _logout(self, request: HttpRequest) -> None:
        logout(request)
        messages.success(request, "You have been logged out successfully.")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self._logout(request)
        return redirect(self.success_url)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "authentication/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful. Please log in.")
        return super().form_valid(form)


class HomeView(EnsureCsrfCookieMixin, TemplateView):
    template_name = "authentication/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        venue_filter = VenueFilter(self.request.GET, queryset=Venue.objects.all())
        popular_venues = (
            Venue.objects.annotate(bookings_count=Count("bookings"))
            .order_by("-bookings_count")
            .prefetch_related("addons")[:3]
        )
        wishlist_ids: set[int] = set()
        if self.request.user.is_authenticated:
            wishlist_ids = set(
                Wishlist.objects.filter(user=self.request.user).values_list("venue_id", flat=True)
            )
        context.update(
            {
                "filter": venue_filter,
                "venues": venue_filter.qs[:6],
                "popular_venues": popular_venues,
                "wishlist_ids": wishlist_ids,
                "testimonials": [
                    {
                        "name": "Rindu Aurellia",
                        "role": "Koordinator Tim Futsal Anak Padi",
                        "image": "https://blogger.googleusercontent.com/img/a/AVvXsEha0jebkzt4VdaSYEd7LkT-ti2-zrf2MC5h6VjkSQNIf8x_6MgiJU6Qe3F7qF5F7mxXFXzTkSJoYhrf_YBy0rMEM-Hm8lg7iD063VW9TUvYaIhLVW5w_F5yUkZOfyPwG_gKp8ZEBKyyNLHDHrXXRuc5iEyTL4gUUIbdKHnenH50xaaPT6YmERUXZtneZlM",
                        "paragraphs": [
                            "Jujur, sebagai koordinator tim futsal 'Anak Padi', dulu saya yang paling stres setiap mau ngatur jadwal main. Prosesnya manual sekali: harus cari rekomendasi lapangan di Google, telepon atau WhatsApp adminnya satu-satu, lalu menunggu balasan mereka yang seringkali lama.",
                            "Sejak menemukan RagaSpace, semua masalah itu selesai. Aplikasinya benar-benar game-changer buat kami. Saya bisa lihat semua jadwal lapangan yang tersedia di sekitar kami secara real-time. Tinggal pilih jam, bayar, dan langsung dapat konfirmasi instan.",
                        ],
                    },
                    {
                        "name": "Tania Putri",
                        "role": "Pelatih Basket SMA Bima",
                        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80",
                        "paragraphs": [
                            "RagaSpace bikin koordinasi latihan jadi jauh lebih gampang. Jadwalnya jelas dan bisa langsung saya bagi ke semua anak asuh lewat satu tautan.",
                            "Sebelumnya saya sering batalin latihan mendadak karena lapangan double booking. Sekarang semua terkontrol dengan notifikasi otomatisnya.",
                        ],
                    },
                    {
                        "name": "Nadya Aulia",
                        "role": "Founder Komunitas Yoga Senja",
                        "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=400&q=80",
                        "paragraphs": [
                            "Komunitas kami sering pindah venue, dan itu biasanya makan waktu untuk survei satu per satu. Lewat RagaSpace, saya bisa bandingkan fasilitas dengan cepat sebelum booking.",
                            "Pembayarannya praktis, ada invoice resmi, dan tim venue juga responsif karena sudah terintegrasi di sistem.",
                        ],
                    },
                    {
                        "name": "Raisa Dewi",
                        "role": "Marketing Manager Event Lokal",
                        "image": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
                        "paragraphs": [
                            "Kami sering gelar event komunitas, dan butuh venue yang bisa di-book jauh hari. RagaSpace kasih visibilitas penuh soal ketersediaan dan harga.",
                            "Tim supportnya juga proaktif, bantu negosiasi kebutuhan tambahan seperti sound system dan dekorasi.",
                        ],
                    },
                    {
                        "name": "Monica Anggraeni",
                        "role": "Manajer Operasional Klub Badminton Orion",
                        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
                        "paragraphs": [
                            "Dulu kami kesulitan memonitor jam sewa di semua lapangan. Sekarang, jadwal terpusat dan anggota klub bisa booking sesuai slot yang kami buka.",
                            "Laporan transaksi bulanannya rapi, jadi mudah untuk evaluasi performa lapangan dan promo membership.",
                        ],
                    },
                ],
            }
        )
        return context


class UserLandingView(LoginRequiredMixin, TemplateView):
    template_name = "authentication/user_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_bookings": Booking.objects.filter(
                    user=self.request.user,
                    status__in=[
                        Booking.STATUS_ACTIVE,
                        Booking.STATUS_CONFIRMED,
                        Booking.STATUS_COMPLETED,
                    ],
                ).select_related("venue"),
                "wishlist_count": Wishlist.objects.filter(user=self.request.user).count(),
            }
        )
        return context


class AdminLandingView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "authentication/admin_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_venues": Venue.objects.count(),
                "pending_bookings": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
                "confirmed_payments": Payment.objects.filter(status="confirmed").count(),
            }
        )
        return context
