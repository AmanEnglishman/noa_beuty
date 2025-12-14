from django.urls import path
from .views import MonthlyFinanceReportView

urlpatterns = [
    path("monthly/", MonthlyFinanceReportView.as_view(), name="monthly-finance"),
]
