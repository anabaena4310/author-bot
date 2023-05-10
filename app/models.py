from django.db import models

from django.contrib.auth.models import User


class AuthorInfo(models.Model):
    author_name = models.CharField(max_length=20)
    intoroduction = models.CharField(max_length=50)
    author_type = models.CharField(max_length=10)
    book_name1 = models.CharField(max_length=30, blank=True)
    book_content1 = models.TextField(blank=True)
    book_name2 = models.CharField(max_length=30, blank=True)
    book_content2 = models.TextField(blank=True)
    book_name3 = models.CharField(max_length=30, blank=True)
    book_content3 = models.TextField(blank=True)

class BookInfo(models.Model):
    book_name = models.CharField(max_length=30)
    # part_content_sum_list は「,」区切りのリストとして扱う
    part_content_sum_list = models.CharField(max_length=10000)
    author = models.ForeignKey(AuthorInfo, on_delete=models.CASCADE)
