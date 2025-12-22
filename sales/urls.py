from django.urls import path
from . import views

urlpatterns = [
    # страницы
    path("today/", views.sales_today, name="sales_today"),
    path("new/", views.sale_create, name="sale_create"),

    # кнопка "Печать" → кладёт в очередь
    path(
        "print/<int:sale_id>/",
        views.enqueue_print,
        name="sale_print"
    ),

    # API для print_agent
    path("print/next/", views.get_next_print),
    path("print/done/<int:sale_id>/", views.mark_printed),
    path("api/print/<int:sale_id>/",views.receipt_png, name="receipt_png"
)

]
