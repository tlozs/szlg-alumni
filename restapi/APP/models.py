from django.db import models
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    def __str__(self):
        return f"{self.user.username} [{self.user.email}]"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.URLField(max_length=255, default='https://i.postimg.cc/hvhBb2vp/Group-3.png')
    social_sites = models.ManyToManyField('SocialSite', blank=True, related_name='profile')
    life_events = models.ManyToManyField('LifeEvent', blank=True, related_name='profile')
    location = models.CharField(max_length=255, blank=True)
    job = models.CharField(max_length=255, blank=True)
    of_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    can_post = models.BooleanField(default=False)

class SocialSite(models.Model):
    class Meta:
        verbose_name = 'Social Site'
        verbose_name_plural = 'Social Sites'

    def __str__(self):
        return f"{self.site} [{self.url}]"

    SITE_CHOICES = [
        ('FB', 'Facebook'),
        ('TW', 'Twitter'),
        ('IG', 'Instagram'),
        ('LI', 'LinkedIn'),
    ]
    site = models.CharField(max_length=2, choices=SITE_CHOICES)
    url = models.URLField(max_length=255, blank=True)

class LifeEvent(models.Model):
    class Meta:
        verbose_name = 'Life Event'
        verbose_name_plural = 'Life Events'
    
    def __str__(self):
        return f"{self.event} [{self.date}]"
    
    EVENT_CHOICES = [
        ('GY', 'Gyerekem született'),
        ('MH', 'Új munkahelyem lett'),
    ]
    event = models.CharField(max_length=2, choices=EVENT_CHOICES)
    date = models.DateTimeField()

class Post(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.title} [{self.author}] post on {self.created_at}"

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    title = models.CharField(max_length=255)
    image = models.URLField(max_length=255, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    VISIBILITY_CHOICES = [
        ('PUB', 'Publikus'),
        ('PRI', 'Privát'),
    ]
    visibility = models.CharField(max_length=3, choices=VISIBILITY_CHOICES)
    TYPE_CHOICES = [
        ('ES', 'Esemény'),
        ('HI', 'Hír'),
    ]
    type_of_post = models.CharField(max_length=2, choices=TYPE_CHOICES)

class Class(models.Model):
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.start_year}-{self.end_year} {self.section}"

    @property
    def start_year(self):
        return int(self.year.start_year)
    end_year = models.IntegerField()
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
    ]
    section = models.CharField(max_length=1, choices=SECTION_CHOICES)
    image = models.URLField(max_length=255, blank=True)

    # neccesairy because start_year is derived from this
    year = models.ForeignKey('Year', on_delete=models.PROTECT, related_name='classes')
    
    link_to_group = models.URLField(max_length=255, blank=True)


class Year(models.Model):
    class Meta:
        verbose_name = 'Year'
        verbose_name_plural = 'Years'
    
    def __str__(self):
        return f"{self.start_year}"

    start_year = models.IntegerField(default=datetime.date.today().year-4)
    link_to_group = models.URLField(max_length=255, blank=True)

class Poll(models.Model):
    class Meta:
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'

    def __str__(self):
        return f"{self.question} [{self.created_at}]"

    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    end_date = models.DateTimeField(blank=True, null=True)
    options = models.ManyToManyField('Option', related_name='poll')

class Option(models.Model):
    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

    def __str__(self):
        return f"{self.poll.question} {self.content} [{self.votes}]"

    content = models.TextField()
    votes = models.IntegerField(default=0)
    users = models.ManyToManyField(User, blank=True)

class Event(models.Model):
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} at {self.location} [{self.start_date}]"

    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    link = models.URLField(max_length=255, blank=True)
    image = models.URLField(max_length=255, blank=True)
    target_users = models.ManyToManyField(User, blank=True, related_name='target_events')
    target_classes = models.ManyToManyField('Class', blank=True, related_name='target_events')
    target_years = models.ManyToManyField('Year', blank=True, related_name='target_events')




