import hashlib
import random
import string

from django.db import models
from django.core.cache import cache
from django.conf import settings

from randsense.inflections import Inflector
from randsense.sentences import process



class SentenceManager(models.Manager):
    @classmethod
    def create_new(cls):
        technical_sentence = []
        base_sentence = []

        pos_sentence = process('S')
        for pos in pos_sentence:
            if "_" in pos:
                new_word = Word.objects.random(category=pos[:pos.index("_")], additional=pos[pos.index("_") + 1:])
            else:
                new_word = Word.objects.random(category=pos)
            technical_sentence.append(new_word)
            base_sentence.append(new_word.base)

        Inflector().inflect(base_sentence, pos_sentence, technical_sentence)

        if 'i' in base_sentence:
            base_sentence[base_sentence.index('i')] = 'I'

        final_sentence = string.capwords(base_sentence[0]) + " " + " ".join(base_sentence[1:])
        if 'whose' in base_sentence or 'whom' in base_sentence:
            final_sentence += "?"
        else:
            final_sentence += "."
        final_sentence = final_sentence.replace(" ,", ",")
        final_sentence = final_sentence.replace(" ;", ";")
        final_sentence = final_sentence.replace(" :", ":")

        sentence = Sentence()
        sentence.base = final_sentence
        # if 'HTTP_X_FORWARDED_FOR' in self.request.META:
        #     sentence.from_ip = self.request.META['HTTP_X_FORWARDED_FOR']
        # else:
        #     sentence.from_ip = self.request.get_host()
        # sentence.number = Sentence.objects.all().count()
        sentence.save()

        return sentence


class Sentence(models.Model):
    base = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=True)
    from_ip = models.CharField(max_length=64)
    number = models.IntegerField(null=True, blank=True)

    objects = SentenceManager()

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return "{base} - {date}".format(
            base=self.base[:50],
            date=self.date_created,
        )


# class SentenceForm(ModelForm):
#     class Meta:
#         model = Sentence


class WordManager(models.Manager):
    @classmethod
    def random(cls, **kwargs):
        if 'additional' in kwargs:
            kwargs[kwargs['additional']] = True
            del kwargs['additional']
        cache_key = "word_filter_" + hashlib.md5(str(kwargs).encode('utf-8')).hexdigest()
        choices = cache.get(cache_key)
        if not choices:
            choices = Word.objects.filter(**kwargs)
            cache.set(cache_key, choices, settings.CACHE_TIME)
        return random.choice(choices)


class Word(models.Model):
    objects = WordManager()
    base = models.CharField(max_length=64)
    category = models.CharField(max_length=64)

    # verbs
    past = models.CharField(max_length=64, null=True, blank=True)
    past_participle = models.CharField(max_length=64, null=True, blank=True)
    present_participle = models.CharField(max_length=64, null=True, blank=True)
    present3s = models.CharField(max_length=64, null=True, blank=True)
    transitive = models.BooleanField(default=False, blank=True)
    intransitive = models.BooleanField(default=False, blank=True)
    ditransitive = models.BooleanField(default=False, blank=True)
    linking = models.BooleanField(default=False, blank=True)

    # nouns
    plural = models.CharField(max_length=64, null=True, blank=True)
    noncount = models.BooleanField(default=False, blank=True)
    place = models.BooleanField(default=False, blank=True)
    person = models.BooleanField(default=False, blank=True)
    demon = models.BooleanField(default=False, blank=True)

    # adjectives
    predicative = models.BooleanField(default=False, blank=True)
    qualitative = models.BooleanField(default=False, blank=True)
    classifying = models.BooleanField(default=False, blank=True)
    comparative = models.BooleanField(default=False, blank=True)
    superlative = models.BooleanField(default=False, blank=True)
    color = models.BooleanField(default=False, blank=True)

    # adverbs
    sentence_modifier = models.BooleanField(default=False, blank=True)
    verb_modifier = models.BooleanField(default=False, blank=True)
    intensifier = models.BooleanField(default=False, blank=True)

    # determiners
    is_plural = models.BooleanField(default=False, blank=True)
    coordinating = models.BooleanField(default=False, blank=True)

    # other
    and_literal = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ('base',)

    def __unicode__(self):
        return u"<{word} - {pos}>".format(word=self.base, pos=self.category)
