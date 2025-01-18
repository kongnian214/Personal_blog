from django.urls import path
from .views import SysMenuNameListView, MenuListView

urlpatterns = [
    path('menu_name/', SysMenuNameListView.as_view(), name='menu_name'),
    path('menus/', MenuListView.as_view(), name='menu-list'),
]
