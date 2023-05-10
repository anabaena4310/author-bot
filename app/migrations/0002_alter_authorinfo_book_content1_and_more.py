# Generated by Django 4.2 on 2023-05-09 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content1',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content2',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_content3',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_name1',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_name2',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='authorinfo',
            name='book_name3',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.CreateModel(
            name='BookInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_name', models.CharField(max_length=30)),
                ('part_content_sum_list', models.CharField(max_length=10000)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.authorinfo')),
            ],
        ),
    ]
