# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('doc', models.FileField(upload_to='doc/%Y/%m', verbose_name='Document-File')),
                ('name', models.CharField(max_length=200, db_index=True, verbose_name='Name', default='')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, default='', verbose_name='Name', unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('img', models.ImageField(upload_to='img/%Y/%m', verbose_name='Image-File')),
                ('name', models.CharField(max_length=200, db_index=True, verbose_name='Name', default='')),
                ('target_width', models.IntegerField(choices=[(0, 'original'), (150, '150 px'), (300, '300 px'), (450, '450 px'), (600, '600 px')], verbose_name='Width', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ImageCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, default='', verbose_name='Name', unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('slug', models.SlugField(max_length=80, verbose_name='slug')),
                ('description', models.TextField(blank=True, verbose_name='Meta description for search engines', default='')),
                ('sibling_id', models.IntegerField(verbose_name='Sibling sort order', default=10)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('publish_from', models.DateTimeField(blank=True, null=True, verbose_name='Start publishing')),
                ('publish_until', models.DateTimeField(blank=True, null=True, verbose_name='Stop publishing')),
                ('breadcrumbs_cache', models.TextField(blank=True, verbose_name='breadcrumbs cache', default='')),
                ('children_cache', models.TextField(blank=True, verbose_name='children cache', default='')),
                ('template_name', models.CharField(max_length=80, choices=[('standard.html', 'standard.html'), ('sidebar.html', 'sidebar.html')], verbose_name='template')),
                ('parent', models.ForeignKey(related_name='sub_pages', null=True, to='django_neon.Page', blank=True, verbose_name='Parent Page')),
            ],
            options={
                'verbose_name_plural': 'Pages',
                'verbose_name': 'Page',
            },
        ),
        migrations.CreateModel(
            name='Pane',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('content', models.TextField(blank=True, verbose_name='Content')),
                ('markup', models.IntegerField(choices=[(0, 'Plain'), (1, 'reStructuredText'), (2, 'Markdown'), (3, 'dynamic')], verbose_name='Markup', default=0)),
                ('use_mediadb', models.BooleanField(verbose_name='Use MediaDB', default=True)),
                ('order_id', models.IntegerField(verbose_name='Sort order', default=10)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('publish_from', models.DateTimeField(blank=True, null=True, verbose_name='Start publishing')),
                ('publish_until', models.DateTimeField(blank=True, null=True, verbose_name='Stop publishing')),
                ('rendered_content', models.TextField(blank=True, verbose_name='Rendered Content')),
                ('page', models.ForeignKey(to='django_neon.Page', verbose_name='Page', related_name='panes')),
            ],
            options={
                'ordering': ['-order_id'],
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
            ],
        ),
        migrations.AddField(
            model_name='pane',
            name='section',
            field=models.ForeignKey(to='django_neon.Section', verbose_name='Section'),
        ),
        migrations.AddField(
            model_name='image',
            name='collection',
            field=models.ForeignKey(to='django_neon.ImageCollection', verbose_name='Collection'),
        ),
        migrations.AddField(
            model_name='document',
            name='collection',
            field=models.ForeignKey(to='django_neon.DocumentCollection', verbose_name='Collection'),
        ),
    ]
