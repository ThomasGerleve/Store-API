from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Store
from .serializers import StoreSerializer

class StoreListCreateAPIView(generics.ListCreateAPIView):
    queryset = Store.objects.all().order_by('id')
    serializer_class = StoreSerializer
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'address', 'opening_hours']

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
          if self.request.user.groups.filter(name='manager').exists():
            self.permission_classes = [IsAuthenticated]
          else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class StoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
          self.permission_classes = [IsAuthenticated]
        else:
          if self.request.user.groups.filter(name='manager').exists():
            self.permission_classes = [IsAuthenticated]
          else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
