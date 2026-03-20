from rest_framework import serializers
from .models import Budget
from categories.models import Category


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount_limit', 'month', 'year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_category(self, value):
        user = self.context['request'].user
        if value and value.user != user:
            raise serializers.ValidationError("This category does not belong to you.")
        return value

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        category = data.get('category')
        month = data.get('month')
        year = data.get('year')

        # Check for duplicate budget on update
        instance = self.instance
        qs = Budget.objects.filter(user=user, category=category, month=month, year=year)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A budget for this category and month already exists.")
        return data