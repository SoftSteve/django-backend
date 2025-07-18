from rest_framework import serializers
from .models import Post, PostImage, EventSpace, User, Comment, DonationFund, Like
from .image_utils import compress_in_memory 

MAX_IMAGES_PER_POST = 8

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'display_name', 'profile_picture']
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'display_name': {'required': False},
            'profile_picture': {'required': False},
        }


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(use_url=True) 
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'profile_picture', 'email']

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model  = PostImage
        fields = ('image',)

    def get_image(self, obj):
        if obj.image:
            url = obj.image.url  
            request = self.context.get('request')
            return request.build_absolute_uri(url) if request else url
        return None

class PostCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(format='%h %d - %I:%M %p', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comments = PostCommentSerializer(many=True, read_only=True)
    liked = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'caption', 'author', 'created_at', 'images',
            'comments', 'liked', 'like_count', 'event_space',
        ]

    def get_liked(self, obj):
        user = self.context['request'].user
        return obj.likes.filter(user=user).exists()

    def create(self, validated_data):
        request = self.context["request"]
        images_data = request.FILES.getlist("images")

        if len(images_data) > MAX_IMAGES_PER_POST:
            raise serializers.ValidationError({
                "images": f"Limit is {MAX_IMAGES_PER_POST} images per post."
            })

        post = Post.objects.create(**validated_data)

        for f in images_data:
            PostImage.objects.create(
                post=post,
                original_image=compress_in_memory(f)
            )

        return post
    



class DonationFundSerializer(serializers.ModelSerializer):
    card_cover_image = serializers.SerializerMethodField()

    class Meta:
        model  = DonationFund
        fields = [
            'id',
            'card_title',
            'card_description',
            'card_cover_image',  
            'card_venmo_link',
            'card_dono_link',
            'created_at',
        ]

    def get_card_cover_image(self, obj):
        if obj.card_cover_image:
            url = obj.card_cover_image.url
            request = self.context.get('request')
            return request.build_absolute_uri(url) if request else url
        return None


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'original_image', 'post']


class EventSpaceSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    donation_funds = DonationFundSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model  = EventSpace
        fields = "__all__"

    def _normalise_image(self, validated_data):
        upload = validated_data.get("original_cover_image")
        if upload:
            validated_data["original_cover_image"] = compress_in_memory(upload)
        return validated_data


    def create(self, validated_data):
        validated_data = self._normalise_image(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._normalise_image(validated_data)
        return super().update(instance, validated_data)

    def get_cover_image(self, obj):
        if obj.cover_image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.cover_image.url)
                if request else obj.cover_image.url
            )
        return None
