# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, blank=True)),
                ('slug', models.SlugField(null=True, editable=False, blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.CharField(max_length=450, blank=True)),
                ('url', models.CharField(max_length=450, blank=True)),
                ('title', models.CharField(max_length=250, null=True, blank=True)),
                ('last_update', models.DateField(null=True, editable=False, blank=True)),
                ('category', models.ForeignKey(blank=True, to='feedme.Category', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_fetched', models.DateField(auto_now_add=True, auto_created=True)),
                ('title', models.CharField(max_length=350, blank=True)),
                ('link', models.URLField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('read', models.BooleanField(default=False)),
                ('guid', models.CharField(max_length=255)),
                ('pub_date', models.DateTimeField()),
                ('feed', models.ForeignKey(blank=True, to='feedme.Feed', null=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='feed',
            unique_together=set([('url', 'user')]),
        ),
    ]
