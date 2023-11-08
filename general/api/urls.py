from rest_framework.routers import SimpleRouter
from general.api.views import UserViewSet, PostViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = router.urls
