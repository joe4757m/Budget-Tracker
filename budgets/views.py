from rest_framework import viewsets, permissions
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user)

        # Optional filter by month/year
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)