from django.contrib import admin
from django.urls import path
from store_api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stores/', views.store_list),
    path('stores/<int:id>', views.store_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
