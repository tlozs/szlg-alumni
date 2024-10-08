from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from APP.models import Profile, Class, SocialSite, LifeEvent, Post
from django.core.validators import URLValidator
import datetime

def validate_token(token):
    if not User.objects.filter(auth_token__key=token).exists():
        raise serializers.ValidationError('Invalid token.')

def seriailze_user(user, token=""):
    profile = user.profile
    social_sites = profile.social_sites.all()
    life_events = profile.life_events.all()
    of_class = profile.of_class
    year = of_class.year if of_class else None
    return {
        'token': token.key if token else "",
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        
        'profile_id': profile.id,
        'profile_picture': profile.profile_picture,
        'location': profile.location,
        'job': profile.job,
        'can_post': profile.can_post,

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

def serialize_post(post):
    return {
            'id': post.id,
            'author': f'{post.author.last_name} {post.author.first_name}',
            'author_image': post.author.profile.profile_picture,
            'title': post.title,
            'image': post.image,
            'content': post.content,
            'created_at': post.created_at,
            'visibility': post.visibility,
            'type_of_post': post.type_of_post,
        }

def merge_social_database_with_incoming(profile, new):
    new_data = {site['site']: site['url'] for site in new}
    current_data = profile.social_sites.all()

    # Update existing sites
    for a_site in new_data:
        currently_present_keys = current_data.filter(site=a_site)
        if currently_present_keys.exists():
            if currently_present_keys.first().url != new_data[a_site]:
                currently_present_keys.update(url=new_data[a_site])
        else:
            profile.social_sites.create(site=a_site, url=new_data[a_site])

    # Delete sites that are not in the new data
    for a_site in current_data:
        if a_site.site not in new_data:
            a_site.delete()

def merge_event_database_with_incoming(profile, new):
    new_data = [[event['event'], event['date']] for event in new]
    current_data = profile.life_events.all()

    # Mark events that are not in the new data to delete them
    marked_to_delete = []
    for an_event in current_data:
        if [an_event.event, an_event.date.strftime('%Y-%m-%dT%H:%M:%SZ')] not in new_data:
            marked_to_delete.append({'event': an_event.event, 'object': an_event})

    to_create = []

    # Update existing events based on the new data
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

    # try to reuse marked events if possible, or delete them
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
    
    username = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not (username and password):
            raise serializers.ValidationError('Both username/email and password are required.')
        else:
            user_name = User.objects.filter(username=username).first()
            user_email = User.objects.filter(email=username).first()
            user = user_name if user_name else user_email
            if not user:
                raise serializers.ValidationError(f'User {username} does not exist.')
            else:
                if not user.check_password(password):
                    raise serializers.ValidationError('Incorrect password.')
                else:
                    token, created = Token.objects.get_or_create(user=user)
                    return {
                        'token': token.key,
                    }
                
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
                raise serializers.ValidationError('Another user with this username already exists.')
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('Another user with this email already exists.')
            return attrs

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(user=user)
        token, created = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
        }
    
class EditProfileSerializer(serializers.Serializer):
    class Meta:
        model = User, Profile
        fields = ['email', 'username', 'first_name', 'last_name', 'profile_picture', 'social_sites', 'life_events', 'location', 'job', 'of_class', 'can_post']
    
    token = serializers.CharField()
    email = serializers.EmailField(max_length=255, required=False)
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    profile_picture = serializers.URLField(max_length=255, allow_blank=True, required=False)
    social_sites = serializers.ListField(child=serializers.DictField(child=serializers.CharField()), required=False)
    life_events = serializers.ListField(child=serializers.DictField(child=serializers.CharField()), required=False)
    location = serializers.CharField(max_length=255, allow_blank=True, required=False)
    job = serializers.CharField(max_length=255, allow_blank=True, required=False)
    class_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        token = attrs.get('token')
        email = attrs.get('email')
        username = attrs.get('username')
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        profile_picture = attrs.get('profile_picture')
        social_sites = attrs.get('social_sites')
        life_events = attrs.get('life_events')
        location = attrs.get('location')
        job = attrs.get('job')
        class_id = attrs.get('class_id')


        validate_token(token)
        if not (email or username or first_name or last_name or profile_picture or social_sites or life_events or location or job or class_id):
            raise serializers.ValidationError('Do not spam with empty requests.')
        user = User.objects.get(auth_token__key=token)
        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            raise serializers.ValidationError('Another user with this email already exists.')
        if username and User.objects.filter(username=username).exclude(id=user.id).exists():
            raise serializers.ValidationError('Another user with this username already exists.')
        if class_id and not Class.objects.filter(id=class_id).exists():
            raise serializers.ValidationError(f'The provided class of id {class_id} in the request does not exist.')
        if social_sites:
            for a_site in social_sites:
                site = a_site.get('site')
                url = a_site.get('url')
                if not (site and url):
                    raise serializers.ValidationError('Both site and url fields are required for social sites.')
                if site not in [pair[0] for pair in SocialSite.SITE_CHOICES]:
                    raise serializers.ValidationError(f'Invalid social site {site}. Must be one of {SocialSite.SITE_CHOICES}.')
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
                    raise serializers.ValidationError(f'Invalid life event {event}. Must be one of {LifeEvent.EVENT_CHOICES}.')
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
                except:
                    raise serializers.ValidationError(f'Invalid date format for life event {event}. Must be in the format YYYY-MM-DDTHH:MM:SSZ')        
        
        return attrs
    
    def modify(self, validated_data):
        user = User.objects.get(auth_token__key=validated_data.get('token'))
        user.email = validated_data.get('email', user.email)
        user.username = validated_data.get('username', user.username)
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.save()
        profile = user.profile
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

class GetUsersSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['token']
    
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('token')
        user_id = self.context.get('user_id')
        validate_token(token)
        if user_id and not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError(f'User with id {user_id} does not exist.')
        return attrs
    
    def get_users(self, validated_data):
        users = User.objects.all()
        return [seriailze_user(user) for user in users]
    
    def get_me(self, validated_data):
        user = User.objects.get(auth_token__key=validated_data.get('token'))
        return seriailze_user(user, Token.objects.get(user=user))
    
    def get_by_id(self, validated_data):
        user_id = self.context.get('user_id')
        user = User.objects.get(id=user_id)
        return seriailze_user(user)

class CreatePostSerializer(serializers.Serializer):
    class Meta:
        model = Post
        fields = ['content', 'created_at', 'visibility']

    token = serializers.CharField()
    title = serializers.CharField()
    image = serializers.URLField()
    content = serializers.CharField()
    visibility = serializers.CharField()
    type_of_post = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get('token')
        content = attrs.get('content')
        visibility = attrs.get('visibility')
        type_of_post = attrs.get('type_of_post')

        validate_token(token)
        user = User.objects.get(auth_token__key=token)
        profile = user.profile
        if not profile.can_post:
            raise serializers.ValidationError('You are not allowed to post.')
        else:
            if not (user.first_name and user.last_name):
                raise serializers.ValidationError('You must provide first name and last name to post.')
            if not profile.profile_picture:
                raise serializers.ValidationError('You must have a profile picture to enable posting.')
        if not content:
            raise serializers.ValidationError('Content is required.')
        if visibility not in [pair[0] for pair in Post.VISIBILITY_CHOICES]:
            raise serializers.ValidationError(f'Invalid visibility option {visibility}. Must be one of {Post.VISIBILITY_CHOICES}.')
        if type_of_post not in [pair[0] for pair in Post.TYPE_CHOICES]:
            raise serializers.ValidationError(f'Invalid type of post {type_of_post}. Must be one of {Post.TYPE_CHOICES}.')

            

        ## email visible to others?
        ## url users/me...

        return attrs
    
    def create(self, validated_data):
        author = User.objects.get(auth_token__key=validated_data.get('token'))
        title = validated_data.get('title')
        image = validated_data.get('image')
        content = validated_data.get('content')
        visibility = validated_data.get('visibility')
        type_of_post = validated_data.get('type_of_post')
        post = Post.objects.create(author=author, title=title, image=image, content=content, visibility=visibility, type_of_post=type_of_post)
        return serialize_post(post)

class GetPostsSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['token']
    
    token = serializers.CharField(required=False)

    def validate(self, attrs):
        token = attrs.get('token')
        if token:
            validate_token(token)
        return attrs
    
    def get_posts(self, validated_data):
        posts = Post.objects.all() if validated_data.get('token') else Post.objects.filter(visibility='PUB')
        return [serialize_post(post) for post in posts]
    
class DeletePostSerializer(serializers.Serializer):
    class Meta:
        model = Post
        fields = ['token', 'post_id']

    token = serializers.CharField()
    post_id = serializers.IntegerField()

    def validate(self, attrs):
        token = attrs.get('token')
        post_id = attrs.get('post_id')

        validate_token(token)
        if not Post.objects.filter(id=post_id).exists():
            raise serializers.ValidationError(f'Post with id {post_id} does not exist.')
        author = Post.objects.get(id=post_id).author
        request_user = User.objects.get(auth_token__key=token)
        if author != request_user:
            raise serializers.ValidationError('You can only delete your posts.')
        return attrs
    
    def delete_post(self, validated_data):
        post = Post.objects.get(id=validated_data.get('post_id'))
        post.delete()
        return {'message': 'Post deleted.'}