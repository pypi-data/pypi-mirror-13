"""
Django Feedme

Urls.py

Author: Derek Stegelman
"""

from __future__ import unicode_literals
from django.conf.urls import url

from .views import FeedList, ImportView, AddView, mark_all_as_read, mark_as_read

urlpatterns = [
    url(r'^$', FeedList.as_view(), name="feedme-feed-list"),
    url(r'^by_category/(?P<category>[-\w]+)/$', FeedList.as_view(), name='feedme-feed-list-by-category'),
    url(r'^by_feed/(?P<feed_id>[-\w]+)/$', FeedList.as_view(), name='feedme-feed-list-by-feed'),
    url(r'^import/$', ImportView.as_view(), name='feedme-import-google-takeout'),
    url(r'^mark_all_as_read/$', mark_all_as_read, name='feedme-mark-all-as-read'),
    url(r'^ajax/mark_as_read/$', mark_as_read, name='feedme-mark-as-read-ajax'),
    url(r'^ajax/add/$', AddView.as_view(), name='feedme-add-ajax'),
]
