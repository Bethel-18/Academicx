from django.urls import path
from .views import RegisterView, GenerateView, FlashcardListCreateView, VideoListCreateView, TextbookListCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('generate/', GenerateView.as_view(), name='generate'),
    path('flashcards/', FlashcardListCreateView.as_view(), name='flashcards'),
    path('videos/', VideoListCreateView.as_view(), name='videos'),
    path('textbooks/', TextbookListCreateView.as_view(), name='textbooks'),
]
