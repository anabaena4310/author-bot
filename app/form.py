from django import forms
from django.contrib.auth.models import User
from .models import AuthorInfo

class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = AuthorInfo
        fields = ("author_name", "intoroduction", "author_type", "book_name1", "book_content1", "book_name2", "book_content2", "book_name3", "book_content3")
        labels={
           'author_name':'著者名',
           'intoroduction':'自己紹介（任意）',
           'author_type':'著者ジャンル',
           'book_name1':'著書名1',
           'book_content1':'著書内容1',
           'book_name2':'著書名2',
           'book_content2':'著書内容2',
           'book_name3':'著書名3',
           'book_content3':'著者内容3',
           }

# class BookForm(forms.ModelForm):

#     def __init__(self, *args, **kwargs):
#         super(AuthorInfo, self).__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'

#     class Meta:
#         model = BookInfo
#         fields = ("book_name", "text")