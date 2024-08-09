from django.db import models
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.URLField(max_length=255, blank=True)
    social_sites = models.ManyToManyField('SocialSite', blank=True, related_name='profile')
    life_events = models.ManyToManyField('LifeEvent', blank=True, related_name='profile')
    location = models.CharField(max_length=255, blank=True)
    job = models.CharField(max_length=255, blank=True)
    of_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    can_post = models.BooleanField(default=False)

class SocialSite(models.Model):
    SITE_CHOICES = [
        ('FB', 'Facebook'),
        ('TW', 'Twitter'),
        ('IG', 'Instagram'),
        ('LI', 'LinkedIn'),
    ]
    site = models.CharField(max_length=2, choices=SITE_CHOICES)
    url = models.URLField(max_length=255, blank=True)

class LifeEvent(models.Model):
    EVENT_CHOICES = [
        ('GY', 'Gyerekem született'),
        ('MH', 'Új munkahelyem lett'),
    ]
    event = models.CharField(max_length=2, choices=EVENT_CHOICES)
    date = models.DateTimeField()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    VISIBILITY_CHOICES = [
        ('PUB', 'Publikus'),
        ('PRI', 'Privát'),
    ]
    visibility = models.CharField(max_length=3, choices=VISIBILITY_CHOICES)

class Class(models.Model):
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
    start_year = models.IntegerField(default=datetime.date.today().year-4)
    link_to_group = models.URLField(max_length=255, blank=True)

class Poll(models.Model):
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    end_date = models.DateTimeField(blank=True, null=True)
    options = models.ManyToManyField('Option', related_name='poll')

class Option(models.Model):
    content = models.TextField()
    votes = models.IntegerField(default=0)
    users = models.ManyToManyField(User, blank=True)

class Event(models.Model):
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




