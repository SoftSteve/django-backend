from rest_framework.routers import DefaultRouter
from .views import PostViewSet, EventSpaceViewSet
from django.urls import path
from .views import LoginView, LogoutView, get_csrf_token, UserSessionView, EventSpaceLookupView, EventSpacePreviewView, CreateAccountView, UpdateUserView, CommentViewSet, DonationFundViewSet

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('csrf/', get_csrf_token),
    path('auth/session/', UserSessionView.as_view()),
    path('space-lookup/', EventSpaceLookupView.as_view()),
    path('publicspace-lookup/', EventSpacePreviewView.as_view()),
    path('auth/create-account/', CreateAccountView.as_view()),
    path('auth/update-account/', UpdateUserView.as_view()),
    
]

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'eventspace', EventSpaceViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'donationfunds', DonationFundViewSet)

urlpatterns += router.urls

