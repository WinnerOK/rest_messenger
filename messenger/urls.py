from django.conf.urls import url
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from .views import PingView, PersonViewSet, MessageView

schema_view = get_schema_view(
    openapi.Info(
        title="Messenger API",
        default_version="v1"
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

router = DefaultRouter()
router.register(r'users', PersonViewSet, basename='user')
router.register(r'messages', MessageView, basename="message")

urlpatterns = [
    path('', include(router.urls)),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("ping", PingView.as_view()),
]
