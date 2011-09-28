import sys
import time
import urllib
import urllib2
import urlparse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

import gdata.gauth
import gdata.docs.client

#
# NOTE: You must change the consumer key and consumer secret to the 
#       key and secret that you received from Google
#
CONSUMER_KEY = "anonymous"
CONSUMER_SECRET = "anonymous"
SOURCE_NAME = "leehsueh-TJCBDB-v1"
SCOPES = ['https://docs.google.com/feeds/', ]   # include others for multi-scope keys


# session keys
GOOGLE_OAUTH_REQ_TOKEN = 'google_oauth_req_token'
GOOGLE_OAUTH_TOKEN = 'google_oauth_token'

def oauth_start(request):
    """View function that begins the Google OAuth authentication process"""
    client = gdata.docs.client.DocsClient(source=SOURCE_NAME)
    oauth_callback_url = request.build_absolute_uri()
    request_token = client.GetOAuthToken(
        SCOPES,
        oauth_callback_url,
        CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET
    )

    # save in session
    request.session[GOOGLE_OAUTH_REQ_TOKEN] = request_token
    domain = None
    return HttpResponseRedirect(request_token.generate_authorization_url())

def oauth_get_access_token(request):
    # authorized request token
    saved_request_token = request.session[GOOGLE_OAUTH_REQ_TOKEN]
    request_token = gdata.gauth.AuthorizeRequestToken(saved_request_token, request.build_absolute_uri())

    client = gdata.docs.client.DocsClient(source=SOURCE_NAME)
    access_token = client.GetAccessToken(request_token)
    request.session[GOOGLE_OAUTH_TOKEN] = access_token
    return

def oauth_test(request):
    """Test callback view"""
    if request.session.get(GOOGLE_OAUTH_TOKEN, False):
        client = get_client(
            request.session[GOOGLE_OAUTH_TOKEN].token,
            request.session[GOOGLE_OAUTH_TOKEN].token_secret,
        )
        feed = client.GetDocList(uri='/feeds/default/private/full/-/folder')
        c = {
            'feed': feed,
        }
        return render_to_response("google_oauth_info.html", c,
                    context_instance=RequestContext(request))

    elif request.session.get(GOOGLE_OAUTH_REQ_TOKEN, False):
        oauth_get_access_token(request)
        return HttpResponseRedirect("http://" + request.get_host() + request.path)
    else:
        return oauth_start(request)

def get_folder_contents(request, resource_id):
    if request.session.get(GOOGLE_OAUTH_TOKEN, False):
        client = get_client(
            request.session[GOOGLE_OAUTH_TOKEN].token,
            request.session[GOOGLE_OAUTH_TOKEN].token_secret,
        )
        folder = client.GetDoc(resource_id)
        feed = client.GetDocList(uri=folder.content.src + "/-/document")  

        c = {
            'folder': folder,
            'feed': feed,
        }
        return render_to_response("google_oauth_folder.html", c,
                    context_instance=RequestContext(request))

    elif request.session.get(GOOGLE_OAUTH_REQ_TOKEN, False):
        oauth_get_access_token(request)
        return HttpResponseRedirect("http://" + request.get_host() + request.path)

    else:
        return oauth_start(request)

def get_doc_content(request, resource_id):
    if request.session.get(GOOGLE_OAUTH_TOKEN, False):
        client = get_client(
            request.session[GOOGLE_OAUTH_TOKEN].token,
            request.session[GOOGLE_OAUTH_TOKEN].token_secret,
        )
        doc = client.GetDoc(resource_id)
        content = client.GetFileContent(
            uri=doc.content.src + "&exportFormat=html"    
        )
        css_begin_index = content.find('<style type="text/css">')
        css_end_index = content.find('</head>', css_begin_index)
        css_style = content[css_begin_index:css_end_index]
        body_begin = content.find('<body')
        body_end = content.find('</html>')
        body = content[body_begin:body_end]
        c = {
            'doc': doc,
            'style': css_style,
            'body': body
        }
        return render_to_response("google_oauth_doc.html", c,
                    context_instance=RequestContext(request))

    elif request.session.get(GOOGLE_OAUTH_REQ_TOKEN, False):
        oauth_get_access_token(request)
        return HttpResponseRedirect("http://" + request.get_host() + request.path)

    else:
        return oauth_start(request)

def get_client(token, token_secret):
    client = gdata.docs.client.DocsClient(source=SOURCE_NAME)
    client.auth_token = gdata.gauth.OAuthHmacToken(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        token,
        token_secret,
        gdata.gauth.ACCESS_TOKEN
    )
    return client

def clear_google_oauth_session(request):
    """This is not a view function! It is a utility
    for clearing the session values"""
    try:
        del request.session[GOOGLE_OAUTH_TOKEN]
        del request.session[GOOGLE_OAUTH_REQ_TOKEN]
        del request.session[EVERNOTE_EDAM_USERID]
    except KeyError:
        pass
