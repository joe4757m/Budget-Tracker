from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Q
from decimal import Decimal
import datetime

from transactions.models import Transaction
from budgets.models import Budget
from categories.models import Category


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Default to current month/year if not provided
        today = datetime.date.today()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        # Filter transactions for this month
        transactions = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        )

        # Total income & expenses
        total_income = transactions.filter(
            type=Transaction.TransactionType.INCOME
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        total_expenses = transactions.filter(
            type=Transaction.TransactionType.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        balance = total_income - total_expenses

        # Spending breakdown by category
        spending_by_category = (
            transactions.filter(type=Transaction.TransactionType.EXPENSE)
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        # Budget vs actual spending
        budgets = Budget.objects.filter(user=user, month=month, year=year)
        budget_vs_actual = []
        for budget in budgets:
            spent = transactions.filter(
                type=Transaction.TransactionType.EXPENSE,
                category=budget.category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

            budget_vs_actual.append({
                'category': budget.category.name,
                'limit': budget.amount_limit,
                'spent': spent,
                'remaining': budget.amount_limit - spent,
                'is_over': spent > budget.amount_limit
            })

        return Response({
            'month': month,
            'year': year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'spending_by_category': list(spending_by_category),
            'budget_vs_actual': budget_vs_actual,
        })