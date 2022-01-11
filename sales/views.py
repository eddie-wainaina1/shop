from os import name
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Sale
from .forms import SalesSearchForm
from reports.forms import ReportForm
from .utils import get_customer_from_id, get_seller_from_id, get_chart
import pandas as pd 

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin 
# Create your views here.
@login_required
def home_view(request):
    sales_df = None
    positions_df = None
    merged_df = None
    chart = None
    no_data = None
    df = None
    report_form = ReportForm()
    search_form = SalesSearchForm(request.POST or None)
    
    
    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        chart_type = request.POST.get('chart_type')
        results_by = request.POST.get('results_by')
        # print(date_from, ' ',date_to, ' ',chart_type)

        sale_qs = Sale.objects.filter(created__date__gte = date_from, created__date__lte = date_to)
        if len(sale_qs)>0:
            sales_df = pd.DataFrame(sale_qs.values())
            sales_df['customer_id'] = sales_df['customer_id'].apply(get_customer_from_id)
            sales_df['seller_id'] = sales_df['seller_id'].apply(get_seller_from_id)
            sales_df.rename({
                'customer_id': 'customer',
                'seller_id': 'seller',
                'id':'sales_id',}, 
            axis=1, inplace=True)
            sales_df['created'] = sales_df['created'].apply(lambda x: x.strftime('%Y-%m-%d'))

            positions_data = []
            for sale in sale_qs:
                for pos in sale.get_positions():
                    obj = {
                        'position_id':pos.id,
                        'product': pos.product.name,
                        'quantity': pos.quantity,
                        'price': pos.price,
                        'sales_id': pos.get_sales_id(),
                    }
                    positions_data.append(obj)
            positions_df = pd.DataFrame(positions_data)
            merged_df = pd.merge(sales_df,positions_df,on='sales_id')
            
            df = merged_df.groupby('transaction_id',as_index=False)['price'].agg('sum')
            chart = get_chart(chart_type, sales_df, results_by)

            sales_df = sales_df.to_html()
            positions_df = positions_df.to_html()
            merged_df = merged_df.to_html()
            df = df.to_html()
            #print (sales_df)
            # print (positions_df)
            # print('###################')
        else:
            no_data = 'No data available for this date range'

    context = {
        'no_data': no_data,
        'search_form': search_form,
        'report_form': report_form,
        'sales_df': sales_df,
        'positions_df': positions_df,
        'merged_df': merged_df,
        'df': df,
        'chart': chart,
    }
    return render(request, 'sales/home.html', context)

class SalesListView(LoginRequiredMixin,ListView):
    model = Sale
    template_name = 'sales/main.html'
    context_object_name = 'qs'

class SaleDetailView(LoginRequiredMixin,DetailView):
    model = Sale
    template_name = 'sales/detail.html'

@login_required
def sales_list_view(request):
    qs = Sale.objects.all()
    return render(request, 'sales/main.html', {'qs':qs})#object_list

@login_required
def sale_detail_view(request, **kwargs):
    pk = kwargs.get('pk')
    obj = Sale.objects.get(pk = pk)
    return render(request, 'sales/detail.html', {'object':obj})

'''
In the urls:
path('sales/' sale_list_view, name='list'),
path('sales/<pk>/', sale_detail_view, name='detail')
'''
