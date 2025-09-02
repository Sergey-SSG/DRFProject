from django.contrib import admin

from .models import Payment, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "phone", "city")
    list_filter = ("city",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "payment_date",
        "paid_course",
        "paid_lesson",
        "amount",
        "payment_method",
    )
    list_filter = ("payment_method", "payment_date")
