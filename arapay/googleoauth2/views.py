from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from oauth2client.client import OAuth2WebServerFlow

from arapay import settings

FLOW = OAuth2WebServerFlow(client_id=settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON['web']['client_id'],
                           client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON['web']['client_secret'],
                           scope='email',
                           redirect_uri=settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON['web']['redirect_uris'][0])


@login_required
def login(request):
    auth_uri = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(auth_uri)


@login_required
def oauthcallback(request):
    code = request.GET.get('code', '')
    if code:
        # Code received
        credentials = FLOW.step2_exchange(code)
        print(credentials)
        print(type(credentials))
        return HttpResponse('login successful')

    error = request.GET.get('error', '')
    if error:
        # Error, prop access denied
        return HttpResponse('Error=%s' % error)

    # ???
    return HttpResponseBadRequest('Code or Error status was not received.')
