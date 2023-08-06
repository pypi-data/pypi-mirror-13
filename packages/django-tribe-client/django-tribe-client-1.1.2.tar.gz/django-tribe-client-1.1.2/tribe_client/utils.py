import requests
import json
from app_settings import *


def get_access_token(authorization_code):
    """
    Takes the temporary, short-lived authorization_code returned by tribe and
    sends it back (with some other ids and secrets) in exchange for an
    access_token.

    Arguments:
    authorization_code -- a string of characters returned by Tribe when it
    redirects the user from the page where they authorize the client to access
    their resources

    Returns:
    access_token -- another string of characters, with which users can remotely
    access their resources.

    """
    parameters = {
        "client_id": TRIBE_ID, "client_secret": TRIBE_SECRET,
        "grant_type": "authorization_code",  "code": authorization_code,
        "redirect_uri": TRIBE_REDIRECT_URI
    }
    tribe_connection = requests.post(ACCESS_TOKEN_URL, data=parameters)
    result = tribe_connection.json()
    if 'access_token' in result:
        access_token = result['access_token']
        return access_token
    else:
        return None


def retrieve_public_genesets(options={}):
    """
    Returns only public genesets. This will not return any of the
    private ones since no oauth token is sent with this request.

    Arguments:
    options -- An optional dictionary to be sent as request parameters
    (to filter the types of genesets requested, etc.)

    Returns:
    Either -

    a) A list of genesets (as dictionaries), or
    b) An empty list, if the request failed.
    """

    genesets_url = TRIBE_URL + '/api/v1/geneset/'

    try:
        tribe_connection = requests.get(genesets_url, params=options)
        result = tribe_connection.json()
        genesets = result['objects']
        return genesets

    except:
        return []


def retrieve_public_versions(geneset, options={}):
    """
    Returns only public versions. As with retrieve_public_genesets() above,
    this will not return any private versions since no oauth token is
    sent with this request.

    Arguments:
    options -- An optional dictionary to be sent as request parameters
    geneset -- The resource URI for the desired geneset

    Returns:
    Either -

    a) A list of versions (as dictionaries), or
    b) An empty list, if the request failed.
    """

    versions_url = TRIBE_URL + '/api/v1/version/'
    options['geneset__id'] = geneset
    options['xrdb'] = CROSSREF

    try:
        tribe_connection = requests.get(versions_url, params=options)
        result = tribe_connection.json()
        versions = result['objects']
        return versions

    except:
        return []


def retrieve_user_object(access_token):
    """
    Makes a get request to tribe using the access_token to get the user's info
    (the user should only have permissions to see the user object that
    corresponds to them).

    Arguments:
    access_token -- The OAuth token with which the user has access to their
    resources. This is a string of characters.

    Returns:
    Either -

    a) 'OAuth Token expired' if the access_token has expired,
    b) An empty list [] if the access_token is completely invalid, or
    c) The user object this user has access to (in the form of a dictionary)

    """

    parameters = {'oauth_consumer_key': access_token}

    try:
        tribe_connection = requests.get(TRIBE_URL + '/api/v1/user',
                                        params=parameters)
        result = tribe_connection.json()
        user = result['objects']  # This is in the form of a list
        meta = result['meta']

        if 'oauth_token_expired' in meta:
            return ('OAuth Token expired')
        else:
            return user[0]  # Grab the first (and only) element in the list
    except:
        return []


def retrieve_user_genesets(access_token, options={}):
    """
    Returns any genesets created by the user.

    Arguments:
    access_token -- The OAuth token with which the user has access to
    their resources. This is a string of characters.

    options -- An optional dictionary to be sent as request parameters

    Returns:
    Either -

    a) A list of genesets (as dictionaries), or
    b) An empty list, if the request failed.
    """

    try:
        get_user = retrieve_user_object(access_token)

        if (get_user == 'OAuth Token expired' or get_user == []):
            return []

        else:
            options['oauth_consumer_key'] = access_token
            options['creator'] = str(get_user['id'])
            options['show_tip'] = 'true'
            options['full_annotations'] = 'true'

            genesets_url = TRIBE_URL + '/api/v1/geneset/'

            tribe_connection = requests.get(genesets_url, params=options)
            result = tribe_connection.json()
            meta = result['meta']
            genesets = result['objects']
            return genesets

    except:
        return []


def retrieve_user_geneset_versions(access_token, geneset):
    """
    Returns all versions that belong to a specific geneset
    (if user has access to that geneset)

    Arguments:
    access_token -- The OAuth token with which the user has access to
    their resources. This is a string of characters.

    geneset -- The resource URI for the desired geneset

    Returns:
    Either -

    a) A list of versions (as dictionaries), or
    b) An empty list, if the request failed.
    """

    try:
        parameters = {'oauth_consumer_key': access_token,
                      'geneset__id': geneset,
                      'xrdb': CROSSREF}

        versions_url = TRIBE_URL + '/api/v1/version/'
        tribe_connection = requests.get(versions_url, params=parameters)
        result = tribe_connection.json()
        meta = result['meta']
        versions = result['objects']
        return versions

    except:
        return []


def create_remote_geneset(access_token, geneset_info):
    """
    Creates a geneset in Tribe given a 'geneset_info' dictionary.

    Arguments:
    access_token -- The OAuth token with which the user has access to
    their resources. This is a string of characters.

    geneset_info -- The dictionary containing the values for the fields
    in the geneset that is going to be created in Tribe.

    Returns:
    Either -

    a) The newly created geneset (as a dictionary), or
    b) An empty list, if the request failed.
    """

    # This filters organisms by scientific name in the 'organisms' endpoint
    # of Tribe's API. This returns a dictionary with 'meta' and 'objects' keys.
    parameters = {'scientific_name': geneset_info['organism']}
    organism_request = requests.get(TRIBE_URL + '/api/v1/organism',
                                    params=parameters)
    org_response = organism_request.json()

    # The 'objects' key always contains a list (even when there is just one
    # element). Put this organism object's resource_uri in geneset_info.
    organism_obj = org_response['objects'][0]
    geneset_info['organism'] = organism_obj['resource_uri']

    headers = {'Authorization': 'OAuth ' + access_token,
               'Content-Type': 'application/json'}

    payload = json.dumps(geneset_info)
    genesets_url = TRIBE_URL + '/api/v1/geneset'
    geneset_response = requests.post(genesets_url, data=payload,
                                     headers=headers)

    # If something went wrong and the geneset was not created
    # (making the response status something other than 201),
    # return the response as is given by Tribe
    if (geneset_response.status_code != 201):
        return geneset_response

    try:
        geneset_response = geneset_response.json()
        return geneset_response

    except ValueError:
        return geneset_response


def create_remote_version(access_token, version_info):
    """
    Creates a new version for an already existing geneset in Tribe.

    Arguments:
    access_token -- The OAuth token with which the user has access to
    their resources. This is a string of characters.

    version_info -- The dictionary containing the values for the fields
    in the version that is going to be created in Tribe. One of these
    is the resource_uri of the geneset this version will belong to.

    Returns:
    Either -

    a) The newly created version (as a dictionary), or
    b) An empty list, if the request failed.
    """

    headers = {'Authorization': 'OAuth ' + access_token,
               'Content-Type': 'application/json'}

    payload = json.dumps(version_info)
    versions_url = TRIBE_URL + '/api/v1/version'
    version_response = requests.post(versions_url, data=payload,
                                     headers=headers)

    # If something went wrong and the version was not created
    # (making the response status something other than 201),
    # return the response as is given by Tribe
    if (version_response.status_code != 201):
        return version_response

    try:
        version_response = version_response.json()
        return version_response

    except ValueError:
        return version_response


def return_user_object(access_token):
    parameters = {'oauth_consumer_key': access_token}
    tribe_connection = requests.get(TRIBE_URL + '/api/v1/user',
                                    params=parameters)

    try:
        result = tribe_connection.json()
        return result
    except:
        result = '{"meta": {"previous": null, "total_count": 0, ' + \
                 '"offset": 0, "limit": 20, "next": null}, "objects": []}'
        result = json.loads(result)
        return result


def obtain_token_using_credentials(username, password, client_id, client_secret):

    payload = {'grant_type': 'password',
               'username': username,
               'password': password,
               'client_id': client_id,
               'client_secret': client_secret}

    r = requests.post(ACCESS_TOKEN_URL, data=payload)
    tribe_response = r.json()
    return tribe_response['access_token']
