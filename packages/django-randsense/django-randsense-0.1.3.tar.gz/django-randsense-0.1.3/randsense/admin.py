from django.contrib import admin

from randsense.models import Sentence, Word


def favorite(self, request, queryset):
    queryset.update(is_favorite=True)
    l = len(queryset)
    if l == 1:
        self.message_user(request, "Favorited 1 sentence")
    else:
        self.message_user(request, "Favorited {how_many} sentences".format(how_many=len(queryset)))
favorite.short_description = "01 - Favorite selected sentences"


def unfavorite(self, request, queryset):
    queryset.update(is_favorite=False)
    l = len(queryset)
    if l == 1:
        self.message_user(request, "Unfavorited 1 sentence")
    else:
        self.message_user(request, "Unfavorited {how_many} sentences".format(how_many=len(queryset)))
unfavorite.short_description = "02 - Unfavorite selected sentences"


def mark_correct(self, request, queryset):
    queryset.update(is_correct=True)
    l = len(queryset)
    if l == 1:
        self.message_user(request, "Marked 1 sentence as correct")
    else:
        self.message_user(request, "Marked {how_many} sentences as correct".format(how_many=len(queryset)))
mark_correct.short_description = "03 - Mark selected sentences as correct"


def mark_incorrect(self, request, queryset):
    queryset.update(is_correct=False)
    l = len(queryset)
    if l == 1:
        self.message_user(request, "Marked 1 sentence as incorrect")
    else:
        self.message_user(request, "Marked {how_many} sentences as incorrect".format(how_many=len(queryset)))
mark_incorrect.short_description = "04 - Mark selected sentences as incorrect"


class SentenceAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_correct', 'base', 'is_favorite', 'date_created', 'from_ip',)
    list_display_links = ('number', 'base',)
    list_filter = ('is_favorite', 'is_correct',)
    search_fields = ('base',)
    readonly_fields = ('base', 'from_ip', 'number',)

    actions = [favorite, unfavorite, mark_correct, mark_incorrect,]


class WordAdmin(admin.ModelAdmin):
    list_display = ('base', 'category',)
    list_filter = ('category',)
    search_fields = ('base', 'category', 'past', 'past_participle', 'present_participle',)
    fieldsets = (
        (None, {
            'fields': (('base', 'category',),
                        'past', 'past_participle', 'present_participle', 'present3s', 'plural',)
        }),
        ('Attributes', {
            'classes': ['collapse', 'wide', 'extrapretty',],
            'fields': ('transitive', 'intransitive', 'ditransitive', 'linking',
                       'noncount', 'predicative', 'qualitative', 'classifying',
                       'comparative', 'superlative', 'color', 'sentence_modifier',
                       'verb_modifier', 'intensifier', 'coordinating', 'is_plural',
                       'place', 'person', 'demon', 'and_literal'),
        }),
    )


admin.site.register(Sentence, SentenceAdmin)
admin.site.register(Word, WordAdmin)
