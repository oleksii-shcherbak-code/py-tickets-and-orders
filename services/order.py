import datetime
from typing import Optional, Dict, List

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.db.models import QuerySet

from db.models import Order, Ticket


@transaction.atomic
def create_order(
    tickets: List[Dict[str, int]],
    username: str,
    date: Optional[str] = None,
) -> Order:
    user = get_user_model().objects.get(username=username)

    if date:
        created_at = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO db_order (created_at, user_id)
                VALUES (%s, %s)
                """,
                (created_at, user.id),
            )
            order_id = cursor.lastrowid

        order = Order.objects.get(id=order_id)

    else:
        order = Order.objects.create(user=user)

    for ticket_data in tickets:
        Ticket.objects.create(
            movie_session_id=ticket_data["movie_session"],
            order=order,
            row=ticket_data["row"],
            seat=ticket_data["seat"],
        )

    return order


def get_orders(username: Optional[str] = None) -> QuerySet[Order]:
    queryset = Order.objects.all()
    if username:
        queryset = queryset.filter(user__username=username)
    return queryset
