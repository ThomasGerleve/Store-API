from django.contrib import admin
from django.urls import path
from store_api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stores/', views.StoreListCreateAPIView.as_view()),
    path('stores/<int:pk>', views.StoreRetrieveUpdateDestroyAPIView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
