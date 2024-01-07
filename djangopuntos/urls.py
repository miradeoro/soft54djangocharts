"""djangopuntos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import path
from myapp.views import *

urlpatterns = [
    path('', search, name='search'),
    path('puntos/', puntos, name='puntos'),
    path('charts/', chart_home, name='charting'),
    path('charts/vtaxvend', charts_vtaxvend_home, name='charting_vtaxvend'),
    path('charts/vtaxperiodo', charts_vtaxperiodo_home, name='charting_vtaxperiodo'),
    path('charts/vtaxmediopago', charts_vtaxmediopago_home, name='charting_vtaxmediopago'),
    path('charts/listadosaldos', charts_listadosaldos_home, name='charting_listadosaldos'),
    path('charts/vtaxdia', charts_vtaxdia_home, name='charting_vtaxdia'),
    path('charts/rankingxcliente', charts_rankingxcliente_home, name='charting_rankingxcliente'),
    path('get_rankingxcliente_data/', get_rankingxcliente_data, name='get_rankingxcliente_data'),
    
    path('get_vtaxmediopago_data/', get_vtaxmediopago_data, name='get_sales_data2'),
    path('get_vtaxvend_data/', get_vtaxvend_data, name='get_vtaxvend_data'),
    path('get_vtaxperiodo_data/', get_vtaxperiodo_data, name='get_vtaxperiodo_data'),
    path('get_listadosaldos_data/', get_listadosaldos_data, name='get_vtaxperiodo_data'),
    path('get_listadosaldos_data_vendedores/', get_listadosaldos_data_vendedores, name='get_vtaxperiodo_data_vendedores'),
    path('get_listadosaldos_data_clientes/', get_listadosaldos_data_clientes, name='get_vtaxperiodo_data_clientes'),

    path('get_vtaxdia_data/', get_vtaxdia_data, name='get_vtaxdia_data'),
    
    path('get_empresas_data/', get_empresas_data, name='get_empresas_data'),
    path('get_sucursales_data/', get_sucursales_data, name='get_sucursales_data')



]
