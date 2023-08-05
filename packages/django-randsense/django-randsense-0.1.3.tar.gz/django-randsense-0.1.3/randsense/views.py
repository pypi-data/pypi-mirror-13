from rest_framework import status, viewsets
from rest_framework.response import Response

from randsense.models import Sentence
from randsense.serializers import SentenceSerializer


class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def create(self, request, *args, **kwargs):
        sentence = Sentence.objects.create_new()
        serializer = SentenceSerializer(sentence)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


sentence_list = SentenceViewSet.as_view({'get': 'list', 'post': 'create'})
sentence_detail = SentenceViewSet.as_view({'get': 'retrieve'})

# class FavoriteView(ListView):
#     queryset = Sentence.objects.filter(is_favorite=True)
#     template_name = 'sentences/favorites.html'
#     paginate_by = 20
#     context_object_name = 'sentences'
#
#     def get_context_data(self, **kwargs):
#         context = super(FavoriteView, self).get_context_data(**kwargs)
#         try:
#             context['favorites_copy'] = SiteCopy.objects.get(title='favorites')
#         except SiteCopy.DoesNotExist:
#             context['favorites_copy'] = None
#
#         return context


# def favorite_action(request):
#     if request.method == 'POST' and 'pk' in request.POST:
#         s = Sentence.objects.get(pk=request.POST['pk'])
#         s.is_favorite = True
#         s.save()
#     else:
#         print "No pk value sent"
#
#     return http.HttpResponse("You shouldn't be here.")


# def conan_favorite_action(request, pk):
#     s = Sentence.objects.get(pk=pk)
#     s.is_favorite = True
#     s.save()
#
#     return http.HttpResponse("You shouldn't be here.")


# def incorrect_action(request):
#     if request.method == 'POST' and 'pk' in request.POST:
#         s = Sentence.objects.get(pk=request.POST['pk'])
#         s.is_correct = False
#         s.save()
#     else:
#         print "No pk value sent"
#
#     return http.HttpResponse("You shouldn't be here.")


# def tweeted_action(request):
#     if request.method == 'POST' and 'pk' in request.POST:
#         s = Sentence.objects.get(pk=request.POST['pk'])
#         s.is_tweeted = True
#         s.save()
#     else:
#         print "No pk value sent"

#     return http.HttpResponse("You shouldn't be here.")
