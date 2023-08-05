# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('base', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_favorite', models.BooleanField(default=False)),
                ('is_correct', models.BooleanField(default=True)),
                ('from_ip', models.CharField(max_length=64)),
                ('number', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('base', models.CharField(max_length=64)),
                ('category', models.CharField(max_length=64)),
                ('past', models.CharField(blank=True, null=True, max_length=64)),
                ('past_participle', models.CharField(blank=True, null=True, max_length=64)),
                ('present_participle', models.CharField(blank=True, null=True, max_length=64)),
                ('present3s', models.CharField(blank=True, null=True, max_length=64)),
                ('transitive', models.BooleanField(default=False)),
                ('intransitive', models.BooleanField(default=False)),
                ('ditransitive', models.BooleanField(default=False)),
                ('linking', models.BooleanField(default=False)),
                ('plural', models.CharField(blank=True, null=True, max_length=64)),
                ('noncount', models.BooleanField(default=False)),
                ('place', models.BooleanField(default=False)),
                ('person', models.BooleanField(default=False)),
                ('demon', models.BooleanField(default=False)),
                ('predicative', models.BooleanField(default=False)),
                ('qualitative', models.BooleanField(default=False)),
                ('classifying', models.BooleanField(default=False)),
                ('comparative', models.BooleanField(default=False)),
                ('superlative', models.BooleanField(default=False)),
                ('color', models.BooleanField(default=False)),
                ('sentence_modifier', models.BooleanField(default=False)),
                ('verb_modifier', models.BooleanField(default=False)),
                ('intensifier', models.BooleanField(default=False)),
                ('is_plural', models.BooleanField(default=False)),
                ('coordinating', models.BooleanField(default=False)),
                ('and_literal', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('base',),
            },
        ),
    ]
