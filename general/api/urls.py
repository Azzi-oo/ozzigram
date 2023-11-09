from rest_framework.routers import SimpleRouter
from general.api.views import UserViewSet, PostViewSet, CommentViewSet

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = router.urls
