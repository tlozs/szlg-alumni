from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from APP.models import Profile, Class, SocialSite, LifeEvent
from django.core.validators import URLValidator
import datetime

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

def merge_social_database_with_incoming(profile, new):
    new_data = {site['site']: site['url'] for site in new}
    current_data = profile.social_sites.all()

    # Update existing sites
    for a_site in new_data:
        filtered = current_data.filter(site=a_site)
        if filtered.exists():
            if filtered.first().url != new_data[a_site]:
                filtered.update(url=new_data[a_site])
        else:
            profile.social_sites.create(site=a_site, url=new_data[a_site])

    # Delete sites that are not in the new data
    for a_site in current_data:
        if a_site.site not in new_data:
            a_site.delete()

def merge_event_database_with_incoming(profile, new):
    new_data = [[event['event'], event['date']] for event in new]
    current_data = profile.life_events.all()

    # Mark events to delete, maybe they can be reused
    marked_to_delete = []
    for an_event in current_data:
        if [an_event.event, an_event.date.strftime('%Y-%m-%dT%H:%M:%SZ')] not in new_data:
            marked_to_delete.append({'event': an_event.event, 'object': an_event})

    to_create = []

    # Update existing events
    for an_event in new_data:
        filtered = current_data.filter(event=an_event[0])
        if filtered.exists():
            if not filtered.filter(date=an_event[1]).exists():
                maybe_reusable = [item for item in marked_to_delete if item['event'] == an_event[0]]
                if maybe_reusable:
                    item_to_reuse = maybe_reusable[0]['object']
                    marked_to_delete.remove(maybe_reusable[0])
                    item_to_reuse.date = an_event[1]
                    item_to_reuse.save()
                else:
                    to_create.append(an_event)
        else:
            profile.life_events.create(event=an_event[0], date=an_event[1])

    # Delete events that are not in the new data, or reuse them
    for an_event in marked_to_delete:
        target_object = an_event['object']
        if to_create:
            needed_dates = [event[1] for event in to_create]
            exact_date = target_object.date.strftime('%Y-%m-%dT%H:%M:%SZ')
            if exact_date in needed_dates:
                target_object.event = to_create[needed_dates.index(exact_date)][0]
                target_object.save()
            else:
                target_object.event = to_create[0][0]
                target_object.date = to_create[0][1]
                target_object.save()
        else:
            an_event['object'].delete()

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
                raise serializers.ValidationError(f'User {username} does not exist.')
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
    
class EditProfileSerializer(serializers.Serializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'social_sites', 'life_events', 'location', 'job', 'of_class']
    
    token = serializers.CharField()
    profile_picture = serializers.URLField(max_length=255, allow_blank=True, required=False)
    social_sites = serializers.ListField(child=serializers.DictField(child=serializers.CharField()), required=False)
    life_events = serializers.ListField(child=serializers.DictField(child=serializers.CharField()), required=False)
    location = serializers.CharField(max_length=255, allow_blank=True, required=False)
    job = serializers.CharField(max_length=255, allow_blank=True, required=False)
    class_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        token = attrs.get('token')
        profile_picture = attrs.get('profile_picture')
        social_sites = attrs.get('social_sites')
        life_events = attrs.get('life_events')
        location = attrs.get('location')
        job = attrs.get('job')
        class_id = attrs.get('class_id')

        if not token:
            raise serializers.ValidationError('Token is required.')
        if not User.objects.filter(auth_token__key=token).exists():
            raise serializers.ValidationError('Invalid token.')
        if not (profile_picture or social_sites or life_events or location or job or class_id):
            raise serializers.ValidationError('Do not spam with empty requests.')
        if class_id and not Class.objects.filter(id=class_id).exists():
            raise serializers.ValidationError(f'The provided class of id {class_id} in the request does not exist.')
        if social_sites:
            for a_site in social_sites:
                site = a_site.get('site')
                url = a_site.get('url')
                if not (site and url):
                    raise serializers.ValidationError('Both site and url fields are required for social sites.')
                if site not in [pair[0] for pair in SocialSite.SITE_CHOICES]:
                    raise serializers.ValidationError(f'Invalid social site {site}.')
                try:
                    URLValidator()(url)
                except:
                    raise serializers.ValidationError(f'Invalid URL for social site {site}.')
        if life_events:
            for an_event in life_events:
                event = an_event.get('event')
                date = an_event.get('date')
                if not (event and date):
                    raise serializers.ValidationError('Both event and date fields are required for life events.')
                if event not in [pair[0] for pair in LifeEvent.EVENT_CHOICES]:
                    raise serializers.ValidationError(f'Invalid life event {event}.')
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                except:
                    raise serializers.ValidationError(f'Invalid date format for life event {event}.')        
        
        return attrs
    
    def modify(self, validated_data):
        user = User.objects.get(auth_token__key=validated_data.get('token'))
        profile = user.profile if hasattr(user, 'profile') else None
        if profile:
            profile.profile_picture = validated_data.get('profile_picture', profile.profile_picture)
            profile.location = validated_data.get('location', profile.location)
            profile.job = validated_data.get('job', profile.job)
            profile.save()

            new_social_sites = validated_data.get('social_sites')
            if new_social_sites:
                current_social_sites = profile.social_sites.all()
                if current_social_sites:
                    merge_social_database_with_incoming(profile, new_social_sites)
                else:
                    for a_site in new_social_sites:
                        profile.social_sites.create(site=a_site['site'], url=a_site['url'])

            new_life_events = validated_data.get('life_events')
            if new_life_events:
                current_life_events = profile.life_events.all()
                if current_life_events:
                    merge_event_database_with_incoming(profile, new_life_events)
                else:
                    for an_event in new_life_events:
                        profile.life_events.create(event=an_event['event'], date=an_event['date'])

            class_id = validated_data.get('class_id')
            if class_id:
                profile.of_class = Class.objects.get(id=class_id)
                profile.save()
        return seriailze_user(user, Token.objects.get(user=user))
