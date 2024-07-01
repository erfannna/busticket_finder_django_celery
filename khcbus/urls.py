from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from account import views


router = routers.DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'informs', views.InformListCreateView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]
