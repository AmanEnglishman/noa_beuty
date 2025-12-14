from django.views.generic import TemplateView
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

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
