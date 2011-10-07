Dependencies
============

* GData Python library (download from http://code.google.com/p/gdata-python-client/downloads/list)
* Django sessions framework configured and enabled in settings.py

Setup
-----

* make sure the gdata python libraries are added to your python installation's site-packages directory
* place the google_oauth dir either in your django project or somewhere accessible on your python path (if placing inside your project dir, you'll need to reference it by prefixing your project's name in import statements)
* in your settings.py file
	* add google_oauth as an installed app
	* add GDATA_CONSUMER_KEY and GDATA_CONSUMER_SECRET and set them to the values you recieved when registering your domain with Google (alternatively set both to 'anonymous')
* in your project's top level url.py file, add a url pattern line to include google_oauth.urls, specifying a namespace and app name. Example:
	(r'^google/oauth/', include('google_oauth.urls', namespace='google_oauth', app_name='google_oauth'))

Usage Instructions
------------------

NOTE: Integration may not be the most elegant, but for now it works.

* In your views file, import from the evernote_oauth views the following as needed:
	- view functions and utility functions
		- oauth_start
		- get_client
		- clear_google_oauth_session
		- oauth_get_access_token
	- session key constants
		- GOOGLE_OAUTH_REQ_TOKEN
		- GOOGLE_OAUTH_TOKEN
* Perform a check to determine whether evernote authentication (or reauthentication) is required (e.g. by examining session variables, checking the session expiry age, or trying to invoke the evernote service and handling an authentication expired exception).
* If authentication is not needed, proceed with your application view logic. 
* Otherwise, return oauth_start(request)
	- this will automatically redirect the user to authenticate with Google, and Google will use the value of request.build_absolute_uri(request.path) as the callback URL
	- your view function, to handle the callback invoked by Google, needs to invoke the oauth_get_access_token method, which will store the authentication tokens as django session variables, indexed by the session key constants. After the call to oauth_get_access_token, most likely you'll want to redirect the user once more to request.build_absolute_uri(request.path), and this time, your application view logic will be performed
	- in summary, your view function will be invoked 3 times: first by the user requesting it, second by Evernote as a callback with authentication parameters, and third by the view itself after the authentication parameters are stored in the session (this third redirect is performed in order to clear the authentication token from the address bar)


Usage Example
-------------
	from siteapps_v1.google_oauth.views import oauth_start, get_client, clear_google_oauth_session, oauth_get_access_token
	from siteapps_v1.google_oauth.views import GOOGLE_OAUTH_REQ_TOKEN, GOOGLE_OAUTH_TOKEN

	import gdata.gauth
	import gdata.docs.client


	def get_folder_list(request):
	    """Test callback view"""
	    if request.session.get(GOOGLE_OAUTH_TOKEN, False):
	        client = get_client(
	            request.session[GOOGLE_OAUTH_TOKEN].token,
	            request.session[GOOGLE_OAUTH_TOKEN].token_secret,
	        )
	        
	        # do stuff
	        ...
	        ...

	    elif request.session.get(GOOGLE_OAUTH_REQ_TOKEN, False):
	        oauth_get_access_token(request)
	        return HttpResponseRedirect("http://" + request.get_host() + request.path)
	    else:
	        return oauth_start(request)