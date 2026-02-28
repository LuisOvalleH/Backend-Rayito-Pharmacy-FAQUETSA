from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from catalogo.views import CurrentUserView, ProductImageUploadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/uploads/product-image/", ProductImageUploadView.as_view(), name="product_image_upload"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", CurrentUserView.as_view(), name="auth_me"),
    path("api/", include("catalogo.urls")),
]
