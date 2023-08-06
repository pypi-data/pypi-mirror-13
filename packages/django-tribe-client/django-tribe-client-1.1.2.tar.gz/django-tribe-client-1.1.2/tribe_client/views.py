from django.shortcuts import \
        get_object_or_404, render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context, loader, RequestContext
from django.utils import html
from tribe_client import utils
from tribe_client.app_settings import *
import json


def connect_to_tribe(request):
    if 'tribe_token' not in request.session:
        return render(request, 'establish_connection.html',
                      {'tribe_url': TRIBE_URL,
                       'access_code_url': ACCESS_CODE_URL,
                       'client_id': TRIBE_ID,
                       'scope': 'write'})
    else:
        return display_genesets(request)


def logout_from_tribe(request):
    request.session.clear()
    return connect_to_tribe(request)


def get_token(request):
    access_code = request.GET.__getitem__('code')
    access_token = utils.get_access_token(access_code)
    request.session['tribe_token'] = access_token
    request.session['tribe_user'] = utils.retrieve_user_object(access_token)
    return redirect('display_genesets')


def display_genesets(request):
    if 'tribe_token' in request.session:
        access_token = request.session['tribe_token']
        get_user = utils.retrieve_user_object(access_token)

        if (get_user == 'OAuth Token expired' or get_user == []):
            request.session.clear()
            return connect_to_tribe(request)

        else:  # The user must be logged in and has access to her/himself
            genesets = utils.retrieve_user_genesets(
                access_token, {'full_genes': 'true', 'limit': 100})
            tribe_user = get_user
            return render(request, 'display_genesets.html',
                          {'tribe_url': TRIBE_URL,
                           'genesets': genesets,
                           'tribe_user': tribe_user})

    else:
        return connect_to_tribe(request)


def display_versions(request, geneset):
    if 'tribe_token' in request.session:
        access_token = request.session['tribe_token']
        get_user = utils.retrieve_user_object(access_token)

        if (get_user == 'OAuth Token expired' or get_user == []):
            request.session.clear()
            return connect_to_tribe(request)

        else:
            versions = utils.retrieve_user_versions(access_token, geneset)
            for version in versions:
                version['gene_list'] = []
                for annotation in version['annotations']:
                    version['gene_list'].append(
                            annotation['gene']['standard_name'])
            return render(request, 'display_versions.html',
                          {'versions': versions})


def return_access_token(request):
    if 'tribe_token' in request.session:
        data = {'access_token': request.session['tribe_token']}
    else:
        data = {'access_token': 'No access token'}
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def create_geneset(request):
    """
    View to handle the creation of genesets on Tribe when users make
    POST request to the '/tribe_client/create_geneset' URL.

    Arguments:
    request -- Request object, which contains a dictionary-like object
    of POST data, among other things.

    * In the POST data, there should be a 'geneset' object that contains
    the information for the geneset being created. This 'geneset' is
    passed in the POST data as a string, which we load as json to get a
    dictionary. The general format for the data in this geneset object is:

    geneset = {
        organism: 'Mus musculus',  # Required
        title: 'Sample title',  # Required

        abstract: 'Sample abstract',  # Optional

        # Genes to be included in the geneset are sent in the 'annotations'
        # dictionary, and this whole dictionary is optional. The geneset
        # can have as many or as few annotations as desired. The format for
        # the annotations dictionary is:
        # {gene_id1: [<list of pubmed ids associated with that gene>],
        #  gene_id2: [<list of pubmed ids associated with that gene>]...}
        # The type of identifier for the gene_ids is whatever is set
        # in the CROSSREF setting.
        annotations: {55982: [20671152, 19583951],
                      18091: [8887666], 67087: [],
                      22410:[]}
    }

    Returns:
    Either -

    a) The Tribe URL of the geneset that has just been created, or
    b) A 401 Unauthorized response if the user is not signed in

    N.B. To gracefully save to Tribe, your interface should handle the
    case when a 400 and 401 responses are returned. One way to do this
    for the 401 Unauthorized response, for example, is to catch the error
    and send the user to the Tribe-login page ('/tribe_client' url, which
    is named 'connect_to_tribe' in urls.py). Another way to handle this
    response is to only allow the users to make a request
    to this view (via a button, etc.) when they are already signed in.

    """
    if not ('tribe_token' in request.session):
        return HttpResponse('Unauthorized', status=401)

    tribe_token = request.session['tribe_token']
    is_token_valid = utils.retrieve_user_object(tribe_token)

    if (is_token_valid == 'OAuth Token expired'):
        request.session.clear()
        return HttpResponse('Unauthorized', status=401)

    geneset_info = request.POST.get('geneset')
    geneset_info = json.loads(geneset_info)
    geneset_info['xrdb'] = CROSSREF

    tribe_response = utils.create_remote_geneset(tribe_token,
                                                 geneset_info)
    try:
        slug = tribe_response['slug']
        creator = tribe_response['creator']['username']
        geneset_url = TRIBE_URL + "/#/use/detail/" + creator + "/" + slug
        html_safe_content = html.escape(geneset_url)
        response = {'geneset_url': html_safe_content}

    # If there is an error and a json object could not be loaded from the
    # response, the create_remote_geneset() util function will return a
    # raw response from Tribe, which will trigger a TypeError when trying
    # to access a key from it like a dictionary.
    except TypeError:
        html_safe_content = html.escape(tribe_response.content)
        return HttpResponseBadRequest('The following error has been returned'
                                      ' by Tribe while attempting to create '
                                      'a geneset: "' + html_safe_content +
                                      '"')

    json_response = json.dumps(response)
    return HttpResponse(json_response, content_type='application/json')


def return_user_obj(request):

    if 'tribe_token' in request.session:
        tribe_token = request.session['tribe_token']

    else:
        tribe_token = None

    tribe_response = utils.return_user_object(tribe_token)

    json_response = json.dumps(tribe_response)
    return HttpResponse(json_response, content_type='application/json')
