from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('polls.urls')),
    path('api/users/', include('users.urls')),
    path('client/', TemplateView.as_view(template_name="index.html")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),        # login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),        # rinnovo token
]
