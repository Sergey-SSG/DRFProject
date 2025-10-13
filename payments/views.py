from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson
from users.models import Payment

from .services import StripeService


class CreatePaymentSessionAPIView(APIView):
    """Создание сессии оплаты через Stripe"""

    def post(self, request):
        user = request.user
        course_id = request.data.get("course_id")
        lesson_id = request.data.get("lesson_id")

        # Проверяем, что указан курс или урок
        if not course_id and not lesson_id:
            return Response(
                {"error": "Укажите course_id или lesson_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Получаем объект для оплаты
        if course_id:
            item = get_object_or_404(Course, id=course_id)
            item_type = "course"
        else:
            item = get_object_or_404(Lesson, id=lesson_id)
            item_type = "lesson"

        # Создаем платеж в нашей системе
        payment = Payment.objects.create(
            user=user,
            paid_course=item if item_type == "course" else None,
            paid_lesson=item if item_type == "lesson" else None,
            amount=item.price,
            payment_method="stripe",
            payment_status="pending",
        )

        try:
            # 1. Создаем продукт в Stripe
            product = StripeService.create_product(
                name=item.title, description=item.description
            )

            # 2. Создаем цену в Stripe
            price = StripeService.create_price(
                product_id=product.id, amount=float(item.price)
            )

            # 3. Создаем сессию оплаты
            success_url = request.build_absolute_uri(
                f"/api/payments/success/?payment_id={payment.id}"
            )
            cancel_url = request.build_absolute_uri(
                f"/api/payments/cancel/?payment_id={payment.id}"
            )

            session = StripeService.create_checkout_session(
                price_id=price.id, success_url=success_url, cancel_url=cancel_url
            )

            # Сохраняем данные Stripe в нашем платеже
            payment.stripe_product_id = product.id
            payment.stripe_price_id = price.id
            payment.stripe_session_id = session.id
            payment.stripe_payment_url = session.url
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "payment_url": session.url,
                    "message": "Перейдите по ссылке для оплаты",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            # Если ошибка - помечаем платеж как failed
            payment.payment_status = "failed"
            payment.save()
            return Response(
                {"error": f"Ошибка создания оплаты: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PaymentSuccessAPIView(APIView):
    """Страница успешной оплаты"""

    def get(self, request):
        payment_id = request.GET.get("payment_id")
        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id)
            payment.payment_status = "paid"
            payment.save()

        return Response({"message": "Оплата прошла успешно!"})


class PaymentCancelAPIView(APIView):
    """Страница отмены оплаты"""

    def get(self, request):
        payment_id = request.GET.get("payment_id")
        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id)
            payment.payment_status = "failed"
            payment.save()

        return Response({"message": "Оплата отменена"})
