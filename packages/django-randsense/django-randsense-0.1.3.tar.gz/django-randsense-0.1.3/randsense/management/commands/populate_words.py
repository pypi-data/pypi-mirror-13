import os
import xml.etree.ElementTree as xml

from django.core.management.base import BaseCommand

from randsense.models import Word


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            help="Path to a lexicon file"
        )

    def handle(self, *args, **options):
        filename = options.get('file')
        if not filename:
            exit("Please provide a filename")

        xml_tree = xml.parse(os.path.join(filename))
        root = xml_tree.getroot()

        for word in root:
            w = Word()
            for line in word:
                if line.tag != 'id':
                    if line.text:
                        setattr(w, line.tag.strip(), line.text.strip())
                    else:
                        setattr(w, line.tag.strip().replace("-", "_"), True)
            w.save()

            line = "Saved <{word} - {category}> to database.".format(
                word=w.base,
                category=w.category,
            )
            print(line)
