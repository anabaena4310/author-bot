# Generated by Django 4.2 on 2023-05-12 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_authorinfo_book_content1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content1',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content2',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content3',
            field=models.FileField(blank=True, upload_to=''),
        ),
    ]
