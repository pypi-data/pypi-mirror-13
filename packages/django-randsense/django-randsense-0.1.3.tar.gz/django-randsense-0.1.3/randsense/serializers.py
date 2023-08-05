from rest_framework import serializers

from randsense.models import Sentence


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ('id', 'base',)
