from django.contrib import admin
from .models import Profile, SocialSite, LifeEvent, Post, Class, Year, Poll, Option, Event

admin.site.register(Profile)
admin.site.register(SocialSite)
admin.site.register(LifeEvent)
admin.site.register(Post)
admin.site.register(Class)
admin.site.register(Year)
admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(Event)