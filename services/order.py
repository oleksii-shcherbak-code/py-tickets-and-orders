from datetime import datetime
from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet

from db.models import Order, Ticket


@transaction.atomic
def create_order(
    tickets: list[dict[str, int]],
    username: str,
    date: Optional[str] = None,
) -> Order:
    user = get_user_model().objects.get(username=username)

    order = Order.objects.create(user=user)

    if date is not None:
        order.created_at = datetime.strptime(date, "%Y-%m-%d %H:%M")
        order.save()

    for data in tickets:
        Ticket.objects.create(
            movie_session_id=data["movie_session"],
            order=order,
            row=data["row"],
            seat=data["seat"],
        )

    return order


def get_orders(username: Optional[str] = None) -> QuerySet[Order]:
    queryset = Order.objects.select_related("user")

    if username is not None:
        queryset = queryset.filter(user__username=username)

    return queryset
