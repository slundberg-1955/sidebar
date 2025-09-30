import msal
from django.conf import settings

def get_msal_app():
    return msal.ConfidentialClientApplication(
        settings.CLIENT_ID,
        authority=settings.AUTHORITY,
        client_credential=settings.CLIENT_SECRET,
    )

def get_token(request):
    token = request.session.get('token')
    if not token:
        msal_app = get_msal_app()
        result = msal_app.acquire_token_for_client(scopes=settings.SCOPE)
        request.session['token'] = result.get('access_token')
        token = result.get('access_token')
    return token