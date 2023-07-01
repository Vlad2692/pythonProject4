import django_filters
from .models import Post
from django import forms
# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class PostFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="time_in", widget=forms.DateInput(attrs={'type': "date"}),
                                     label='Дата', lookup_expr='date__gte')
    class Meta:
       # В Meta классе мы должны указать Django модель,
       # в которой будем фильтровать записи.
       model = Post
       # В fields мы описываем по каким полям модели
       # будет производиться фильтрация.
       fields = {

           'header': ['icontains'],
           'author': ['in'],
           # 'time_in': ['year__gt'],
       }