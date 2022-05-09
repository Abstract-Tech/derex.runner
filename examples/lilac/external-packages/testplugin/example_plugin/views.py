from django.http import HttpResponse


def example(request):
    return HttpResponse("<h1>The example edX plugin is installed correctly</h1>")
