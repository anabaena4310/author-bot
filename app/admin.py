from django.contrib import admin

from .models import AuthorInfo, BookInfo


admin.site.register(AuthorInfo)
admin.site.register(BookInfo)
