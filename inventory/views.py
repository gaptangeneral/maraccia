from django.shortcuts import get_object_or_404, render, redirect
from .models import Inventory
from django.contrib.auth.decorators import login_required
from .forms import AddInventoryForm, UpdateInventoryForm
from django.urls import reverse
from django.contrib import messages
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import json

@login_required
def inventory_list(request):
    inventories = Inventory.objects.all()
    context = {
        "title": "Inventory List",
        "inventories": inventories
    }
    return render(request, "inventory/inventory_list.html", context=context)

@login_required
def per_product_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        'inventory': inventory
    }
    return render(request, "inventory/per_product.html", context=context)

@login_required
def add_product(request):
    if request.method == "POST":
        add_form = AddInventoryForm(data=request.POST)
        if add_form.is_valid():
            new_inventory = add_form.save(commit=False)
            new_inventory.sales = float(add_form.cleaned_data['cost_per_item']) * float(add_form.cleaned_data['quantity_sold'])
            new_inventory.save()
            messages.success(request, "Ürün Ekleme Başarılı")
            return redirect("inventory_list")
    else:
        add_form = AddInventoryForm()

    return render(request, "inventory/inventory_add.html", {"form": add_form})


@login_required
def delete_inventory(request, pk):
    inventory= get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.error(request, "Ürün Silindi")
    return redirect("inventory_list")

@login_required
def update_inventory(request, pk):
    inventory= get_object_or_404(Inventory, pk=pk)
    if request.method=="POST":
        updateForm=UpdateInventoryForm(data=request.POST)
        if updateForm.is_valid():
            inventory.name=updateForm.data['name']
            inventory.quantity_in_stock=updateForm.data['quantity_in_stock']
            inventory.quantity_sold=updateForm.data['quantity_sold']
            inventory.cost_per_item=updateForm.data['cost_per_item']
            inventory.sales = float(inventory.cost_per_item)*float(inventory.quantity_sold)
            inventory.save()
            messages.success(request, "Ürün Güncelleme Başarılı")
            return redirect("inventory_list")
        
    else:
        updateForm=UpdateInventoryForm(instance=inventory)
    context = {"form":updateForm}
    return render(request, "inventory/inventory_update.html",context=context)

@login_required
def dashboard(request):
    inventories = Inventory.objects.all()

    df = read_frame(inventories)

    sales_graph = df.groupby(by="last_sale_date", as_index=False, sort=False)['sales'].sum()
    sales_graph = px.line(sales_graph, x="last_sale_date", y="sales", title="Sales Trend")
    sales_graph = sales_graph.to_html(full_html=False, include_plotlyjs=False)  # Düzeltme burada

    best_performing_product_df = df.groupby(by="name").sum().sort_values(by="quantity_sold")
    best_performing_product = px.bar(
        best_performing_product_df,
        x=best_performing_product_df.index,
        y='quantity_sold',  # quantity_sold sütunu
        title="Best Performing Product"
    )
    best_performing_product = best_performing_product.to_html(full_html=False, include_plotlyjs=False)

    most_product_in_stock_df = df.groupby(by="name").sum().sort_values(by="quantity_in_stock")
    most_product_in_stock = px.pie(most_product_in_stock_df,
                                   names=most_product_in_stock_df.index,
                                   values=most_product_in_stock_df.quantity_in_stock,
                                   title="Most Product In Stock"
                                   )

    most_product_in_stock = most_product_in_stock.to_html(full_html=False, include_plotlyjs=False)

    context = {
        "sales_graph": sales_graph,
        "best_performing_product": best_performing_product,
        "most_product_in_stock": most_product_in_stock
    }

    return render(request, "inventory/dashboard.html", context=context)
