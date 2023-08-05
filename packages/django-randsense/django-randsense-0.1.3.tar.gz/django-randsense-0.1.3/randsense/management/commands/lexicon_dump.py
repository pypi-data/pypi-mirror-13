import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand

from models import Word


class Command(BaseCommand):
    def handle(self, *args, **options):
        words = Word.objects.all()
        fields = [field.name for field in Word._meta.fields]

        root = ET.Element("lexicon")

        for word in words:
            word_element = ET.SubElement(root, "word")
            for field in fields:
                if field == 'id': continue
                if word.__dict__[field]:
                    f = ET.SubElement(word_element, str(field))
                    if str(word.__dict__[field]) != 'True':
                        f.text = str(word.__dict__[field])

        print ET.tostring(root)