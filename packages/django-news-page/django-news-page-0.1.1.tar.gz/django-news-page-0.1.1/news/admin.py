from django.contrib import admin
from news.models import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'show', ]
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(News, NewsAdmin)
