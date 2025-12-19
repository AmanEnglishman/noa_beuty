from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from sales.models import Sale, SaleItem, Expense, Income


@method_decorator(staff_member_required, name='dispatch')
class MonthlyFinanceReportView(TemplateView):
    template_name = "finance/monthly_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = now()
        month = int(self.request.GET.get("month", today.month))
        year = int(self.request.GET.get("year", today.year))

        sales = Sale.objects.filter(
            sale_date__year=year,
            sale_date__month=month
        )

        total_sales = sum(s.total for s in sales)

        extra_incomes = Income.objects.filter(
            date__year=year,
            date__month=month
        )
        total_extra_income = sum(i.amount for i in extra_incomes)

        expenses = Expense.objects.filter(
            date__year=year,
            date__month=month
        )
        total_expenses = sum(e.amount for e in expenses)

        profit = total_sales + total_extra_income - total_expenses

        context.update({
            "year": year,
            "month": month,
            "sales": sales,
            "extra_incomes": extra_incomes,
            "expenses": expenses,
            "total_sales": total_sales,
            "total_extra_income": total_extra_income,
            "total_expenses": total_expenses,
            "profit": profit,
        })

        return context


@method_decorator(staff_member_required, name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = "finance/expense_list.html"
    context_object_name = "expenses"
    ordering = ["-date", "-id"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = sum(expense.amount for expense in context['expenses'])
        return context


@method_decorator(staff_member_required, name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    template_name = "finance/expense_form.html"
    fields = ["date", "description", "amount"]
    success_url = reverse_lazy("expense_list")

    def form_valid(self, form):
        messages.success(self.request, "Расход успешно добавлен")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    template_name = "finance/expense_form.html"
    fields = ["date", "description", "amount"]
    success_url = reverse_lazy("expense_list")

    def form_valid(self, form):
        messages.success(self.request, "Расход успешно обновлен")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = "finance/expense_confirm_delete.html"
    success_url = reverse_lazy("expense_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Расход успешно удален")
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class IncomeListView(ListView):
    model = Income
    template_name = "finance/income_list.html"
    context_object_name = "incomes"
    ordering = ["-date", "-id"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = sum(income.amount for income in context['incomes'])
        return context


@method_decorator(staff_member_required, name='dispatch')
class IncomeCreateView(CreateView):
    model = Income
    template_name = "finance/income_form.html"
    fields = ["date", "description", "amount"]
    success_url = reverse_lazy("income_list")

    def form_valid(self, form):
        messages.success(self.request, "Доход успешно добавлен")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class IncomeUpdateView(UpdateView):
    model = Income
    template_name = "finance/income_form.html"
    fields = ["date", "description", "amount"]
    success_url = reverse_lazy("income_list")

    def form_valid(self, form):
        messages.success(self.request, "Доход успешно обновлен")
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class IncomeDeleteView(DeleteView):
    model = Income
    template_name = "finance/income_confirm_delete.html"
    success_url = reverse_lazy("income_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Доход успешно удален")
        return super().delete(request, *args, **kwargs)
