# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from feedme.models import Feed


class Command(BaseCommand):
    """
    Update all feed objects manually.
    """
    help = 'Update all feeds'

    def handle(self, *args, **options):
        count = 0
        for feed in Feed.objects.all():
            count += feed._update_feed()

        print('Updated feeds with {num} new entries'.format(num=count))
