import stripe
from django.conf import settings

# Устанавливаем API-ключ из настроек (он загружается из .env)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Создаём HTTP-клиент, который игнорирует системные прокси (обход SOCKS-ошибки)
stripe.default_http_client = stripe.RequestsClient(proxy=None)


def create_stripe_product(name: str) -> str:
    """
    Создаёт продукт в Stripe и возвращает его ID.
    :param name: Название продукта (например, название курса).
    :return: ID созданного продукта.
    """
    product = stripe.Product.create(name=name)
    return product.id


def create_stripe_price(product_id: str, amount: float, currency: str = "rub") -> str:
    """
    Создаёт цену в Stripe и возвращает её ID.
    :param product_id: ID продукта, к которому привязывается цена.
    :param amount: Сумма в основных единицах (рубли). Внутри умножается на 100 (копейки).
    :param currency: Валюта (по умолчанию "rub").
    :return: ID созданной цены.
    """
    # Stripe принимает сумму в минимальных единицах (копейках)
    unit_amount = int(amount * 100)
    price = stripe.Price.create(
        product=product_id,
        unit_amount=unit_amount,
        currency=currency,
    )
    return price.id


def create_stripe_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str
) -> dict:
    """
    Создаёт сессию оплаты в Stripe и возвращает словарь с ID сессии и ссылкой на оплату.
    :param price_id: ID цены, которую нужно оплатить.
    :param success_url: URL, куда перенаправить после успешной оплаты.
    :param cancel_url: URL, куда перенаправить при отмене оплаты.
    :return: Словарь с ключами 'session_id' и 'payment_url'.
    """
    session = stripe.checkout.Session.create(
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="payment",  # Разовый платёж
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {
        "session_id": session.id,
        "payment_url": session.url,
    }


def retrieve_stripe_session(session_id: str) -> stripe.checkout.Session:
    """
    Запрашивает у Stripe информацию о сессии по её ID.
    Возвращает объект Session.
    """
    return stripe.checkout.Session.retrieve(session_id)
