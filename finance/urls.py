from django.urls import path
from .views import (
    MonthlyFinanceReportView,
    ExpenseListView,
    ExpenseCreateView,
    ExpenseUpdateView,
    ExpenseDeleteView,
    IncomeListView,
    IncomeCreateView,
    IncomeUpdateView,
    IncomeDeleteView,
)

urlpatterns = [
    path("monthly/", MonthlyFinanceReportView.as_view(), name="monthly-finance"),
    path("expenses/", ExpenseListView.as_view(), name="expense_list"),
    path("expenses/add/", ExpenseCreateView.as_view(), name="expense_create"),
    path("expenses/<int:pk>/edit/", ExpenseUpdateView.as_view(), name="expense_update"),
    path("expenses/<int:pk>/delete/", ExpenseDeleteView.as_view(), name="expense_delete"),
    path("incomes/", IncomeListView.as_view(), name="income_list"),
    path("incomes/add/", IncomeCreateView.as_view(), name="income_create"),
    path("incomes/<int:pk>/edit/", IncomeUpdateView.as_view(), name="income_update"),
    path("incomes/<int:pk>/delete/", IncomeDeleteView.as_view(), name="income_delete"),
]
