from django.conf.urls import include, url
from django.contrib import admin

from randsense.views import sentence_list, sentence_detail

urlpatterns = (
    # url(r'^page(?P<page>\d+)/$', FavoriteView.as_view(), name='favorite_view'),
    # url(r'^generate/$', AJAXDetailView.as_view(), name='ajax_detail'),
    # url(r'^favorite/$', 'randsense.views.incorrect_action', name='favorite_action'),
    # url(r'^conan/favorite/(?P<pk>\d+)/$', 'randsense.views.conan_favorite_action', name='conan_favorite_action'),
    # url(r'^incorrect/$', 'randsense.views.incorrect_action', name='incorrect_action'),
    # url(r'^[/]?$', RedirectView.as_view(url="page1/")),
    url(r'^api/sentences/$', sentence_list, name='sentence-list'),
    url(r'^api/sentences/(?P<pk>\d+)/$', sentence_detail, name='sentence-detail')
)
