from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TokenUserAuthenticationSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):

        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()
            if user:
                if user.check_password(password):
                    token, created = Token.objects.get_or_create(user=user)
                    profile = user.profile
                    of_class = profile.of_class
                    social_sites = profile.social_sites.all()
                    life_events = profile.life_events.all()
                    year = of_class.year
                    return {
                        'token': token.key,
                        'user_id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'profile_id': profile.id,
                        'profile_picture': profile.profile_picture,
                        'social_sites': [{'site': site.site, 'url': site.url} for site in social_sites],
                        'life_events': [{'event': event.event, 'date': event.date} for event in life_events],
                        'location': profile.location,
                        'job': profile.job,
                        'class_id': of_class.id,
                        'class_section': of_class.section,
                        'class_start_year': of_class.start_year,
                        'class_end_year': of_class.end_year,
                        'class_image': of_class.image,
                        'class_link_to_group': of_class.link_to_group,
                        'year_id': year.id,
                        'year_link_to_group': year.link_to_group,
                    }
                else:
                    raise serializers.ValidationError('Incorrect password.')
            else:
                raise serializers.ValidationError('User does not exist.')
        else:
            raise serializers.ValidationError('Both username and password are required.')