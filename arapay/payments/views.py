from django.http import HttpResponse


def index(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello <b>%s</b>" % request.user.email)
    else:
        return HttpResponse("Hello World!<br><a href='%s'><button>Login</button></a>" % '/login')
