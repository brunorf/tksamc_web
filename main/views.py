from django.shortcuts import render
from django.http.response import HttpResponse

# Create your views here.

def post_list(request):
    # return render(request, 'blog/post_list.html', {})
    return HttpResponse('teste')
