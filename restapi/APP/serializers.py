from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

def seriailze_user(user, token):
    profile = user.profile if hasattr(user, 'profile') else None
    social_sites = profile.social_sites.all() if profile else None
    life_events = profile.life_events.all() if profile else None
    of_class = profile.of_class if profile else None
    year = of_class.year if of_class else None
    return {
        'token': token.key,
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        
        'profile_id': profile.id if profile else "",
        'profile_picture': profile.profile_picture if profile else "",
        'location': profile.location if profile else "",
        'job': profile.job if profile else "",

        'social_sites': [{'site': site.site, 'url': site.url} for site in social_sites] if social_sites else "",

        'life_events': [{'event': event.event, 'date': event.date} for event in life_events] if life_events else "",
    
        'class_id': of_class.id if of_class else "",
        'class_section': of_class.section if of_class else "",
        'class_start_year': of_class.start_year if of_class else "",
        'class_end_year': of_class.end_year if of_class else "",
        'class_image': of_class.image if of_class else "",
        'class_link_to_group': of_class.link_to_group if of_class else "",
        
        'year_id': year.id if year else "",
        'year_link_to_group': year.link_to_group if year else "",
    }


class TokenUserAuthenticationSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not (username and password):
            raise serializers.ValidationError('Both username and password are required.')
        else:
            user = User.objects.filter(username=username).first()
            if not user:
                raise serializers.ValidationError('User does not exist.')
            else:
                if not user.check_password(password):
                    raise serializers.ValidationError('Incorrect password.')
                else:
                    token, created = Token.objects.get_or_create(user=user)
                    return seriailze_user(user, token)
                
class CreateAccountSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not (username and email and password):
            raise serializers.ValidationError('All fields are required.')
        else:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError('Username already exists.')
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('Email already exists.')
            return attrs

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = User.objects.create_user(username=username, email=email, password=password)
        return seriailze_user(user, Token.objects.create(user=user))