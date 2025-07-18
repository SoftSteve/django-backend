from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Post, EventSpace, Comment, DonationFund, Like, PostImage
from .serializers import PostSerializer, EventSpaceSerializer, UserSerializer, UserUpdateSerializer, PostCommentSerializer, DonationFundSerializer, GalleryImageSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAuthorOrReadOnly
from .pagination  import StandardLimitOffsetPagination, GalleryLimitOffsetPagination

User = get_user_model()

class EventSpaceLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        space_code = request.query_params.get('code')
        if not space_code:
            return Response({'error': 'No space code provided'})
        
        try:
            space = EventSpace.objects.get(Q(space_code__iexact=space_code))
            if request.user not in space.members.all():
                space.members.add(request.user)
            return Response({'event_id': space.id})
        except EventSpace.DoesNotExist:
            return Response({'error': 'Space not found'}, status=status.HTTP_404_NOT_FOUND)
        
class EventSpacePreviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'No space code provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            space = EventSpace.objects.get(Q(space_code__iexact=code))
            return Response({
                'event_id': space.id,
                'name': space.name,
                'cover_image': space.cover_image.url if space.cover_image else None
            })
        except EventSpace.DoesNotExist:
            return Response({'error': 'Space not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_view(request):
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@method_decorator(login_required, name='dispatch')
class UserSessionView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

@ensure_csrf_cookie
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email") 
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Logged in"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)
    
class CreateAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username__iexact=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
    
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=404)

        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            post.like_count = max(post.like_count - 1, 0)
            post.save()
            return Response({'liked': False, 'like_count': post.like_count})

        post.like_count += 1
        post.save()
        return Response({'liked': True, 'like_count': post.like_count})
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at') 
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_space']
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardLimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_destroy(self, instance):
        return instance.delete()
    

class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PostImage.objects.select_related('post').order_by('-created_at')
    serializer_class = GalleryImageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post__event_space']
    pagination_class = GalleryLimitOffsetPagination
    permission_classes = [IsAuthenticated]
   
class DonationFundViewSet(viewsets.ModelViewSet):
    queryset = DonationFund.objects.all().order_by('-created_at')
    serializer_class = DonationFundSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return DonationFund.objects.filter(
            event_space__in=EventSpace.objects.filter(creator=user) | EventSpace.objects.filter(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    

class EventSpaceViewSet(viewsets.ModelViewSet):
    queryset = EventSpace.objects.none()
    serializer_class = EventSpaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return EventSpace.objects.filter(Q(creator=user) | Q(members=user)).distinct().order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
