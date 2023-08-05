from django.core.management.base import BaseCommand

from models import Sentence


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 1
        for sentence in Sentence.objects.reverse():
            sentence.number = count
            sentence.save()
            if count % 1000 == 0:
                print count, "updated"
            count += 1
        print count, "updated"
