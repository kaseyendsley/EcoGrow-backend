from django.contrib import admin
from .models import User, Category, Icon, Difficulty, Tag, Quest

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Icon)
admin.site.register(Difficulty)
admin.site.register(Tag)
admin.site.register(Quest)