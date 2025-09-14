import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Простой сервис для работы с Stripe."""

    @staticmethod
    def create_product(name, description=None):
        """Создаем продукт в Stripe."""
        try:
            product = stripe.Product.create(
                name=name,
                description=description[:500] if description else None,
            )
            return product
        except Exception as e:
            raise Exception(f"Ошибка создания продукта: {e}")

    @staticmethod
    def create_price(product_id, amount, currency="rub"):
        """Создаем цену в Stripe."""
        try:
            # Конвертируем рубли в копейки (Stripe требует сумму в копейках)
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
            )
            return price
        except Exception as e:
            raise Exception(f"Ошибка создания цены: {e}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url):
        """Создаем сессию оплаты."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session
        except Exception as e:
            raise Exception(f"Ошибка создания сессии: {e}")
