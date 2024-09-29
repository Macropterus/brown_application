import datetime, json, logging

import trio
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from brown_application_app.lib import version_helper
from brown_application_app.lib.version_helper import GatherCommitAndBranchData
import requests as apireq
from datetime import datetime

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------


def info( request ):
    """ The "about" view. 
        Can get here from 'info' url, and the root-url redirects here. """
    log.debug( 'starting info()' )
    ## prep data ----------------------------------------------------
    # context = { 'message': 'Hello, world.' }
    context = { 
            'quote': 'The best life is the one in which the creative impulses play the largest part and the possessive impulses the smallest.',
            'author': 'Bertrand Russell' }
    ## prep response ------------------------------------------------
    if request.GET.get( 'format', '' ) == 'json':
        log.debug( 'building json response' )
        resp = HttpResponse( json.dumps(context, sort_keys=True, indent=2), content_type='application/json; charset=utf-8' )
    else:
        log.debug( 'building template response' )
        resp = render( request, 'info.html', context )
    return resp

def daterange(request):
    #Takes in a search string, and then returns the date range of the objects that are returned.
    query = request.GET.get('query', '')
    #optional "rows" parameter lets the user finetune the amount of results going into the function. 100 is default.
    if request.GET.get('rows', '') == '':
        rows = 100
    else:
        rows = request.GET.get('rows', '')
    search_req = 'https://repository.library.brown.edu/api/search/?rows=' + str(rows) + '&q=primary_title:' + query

    search_response = apireq.get(search_req)
    results = search_response.json()
    #total results in the repository
    num_found = results['response']['numFound']
    #the number of results we actually have in our response
    rows_returned = len(results['response']['docs'])

    first_loop = True
    #If the query is empty, or there are no results, we give an appropriate message.
    if rows_returned == 0:
        if query == '':
            resp = HttpResponse('Please input a query (add ?query=[SEARCH STRING] to the url)')
        else:
            resp = HttpResponse('No records found with query ' + query)
    else:
        for doc in results['response']['docs']:
            date = doc['date_dsi']
            #Set the min and max to the date of the first iterated record, to serve as a basepoint
            if first_loop:
                mindate = date
                maxdate = date
                first_loop = False
            else:#Otherwwise, compare and update the min and max if necessary
                if date > maxdate:
                    maxdate = date
                if date < mindate:
                    mindate = date
        #Put together the output to be put into the template
        #It doesn't seem worth it to get into all the possible date formats for this function, so we just truncate everything after the day
        #We also return the rows used versus the total results that could be used in the function, so the user can adjust the row parameter for more accurate output
        context = {
                'quote': 'Dates range from ' + mindate[:10] + ' to ' + maxdate[:10],
                'author': 'Based off of ' + str(rows_returned) + ' results out of a total of ' + str(num_found) }
        resp = render(request, 'daterange.html', context)
    return resp

def datecount(request):
    #Datecount searches a query and returns a count of every object by the year of its date_dsi
    query = request.GET.get('query', '')
    #optional "rows" parameter lets the user finetune the amount of results going into the function. 100 is default.
    if request.GET.get('rows', '') == '':
        rows = 100
    else:
        rows = request.GET.get('rows', '')
    
    search_req = 'https://repository.library.brown.edu/api/search/?rows=' + str(rows) + '&q=primary_title:' + query
    search_response = apireq.get(search_req)

    results = search_response.json()
    rows_returned = len(results['response']['docs'])
    
    #If there are no rows returned, we return a message saying so 
    if rows_returned == 0:
        if query == '':
            resp = HttpResponse('Please input a query (add ?query=[SEARCH STRING] to the url)')
        else:
            resp = HttpResponse('No records found with query ' + query)
    else: #Otherwise, we iterate over the response and count up each year in a dictionary
        years = {}
        for doc in results['response']['docs']:
            date = doc['date_dsi']
            year =  date[:4]
            if year in years:
                years[year]+=1
            else:
                years[year]=1
        #Using \n as a separator and setting the content type to text ensures the output is on multiple lines
        resp = HttpResponse(json.dumps(years, sort_keys=True, separators=("\n", ":")), content_type='text/plain')
    return resp


# -------------------------------------------------------------------
# support urls
# -------------------------------------------------------------------


def error_check( request ):
    """ Offers an easy way to check that admins receive error-emails (in development).
        To view error-emails in runserver-development:
        - run, in another terminal window: `python -m smtpd -n -c DebuggingServer localhost:1026`,
        - (or substitue your own settings for localhost:1026)
    """
    log.debug( 'starting error_check()' )
    log.debug( f'project_settings.DEBUG, ``{project_settings.DEBUG}``' )
    if project_settings.DEBUG == True:  # localdev and dev-server; never production
        log.debug( 'triggering exception' )
        raise Exception( 'Raising intentional exception to check email-admins-on-error functionality.' )
    else:
        log.debug( 'returning 404' )
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )


def version( request ):
    """ Returns basic branch and commit data. """
    log.debug( 'starting version()' )
    rq_now = datetime.datetime.now()
    gatherer = GatherCommitAndBranchData()
    trio.run( gatherer.manage_git_calls )
    info_txt = f'{gatherer.branch} {gatherer.commit}'
    context = version_helper.make_context( request, rq_now, info_txt )
    output = json.dumps( context, sort_keys=True, indent=2 )
    log.debug( f'output, ``{output}``' )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def root( request ):
   return HttpResponseRedirect( reverse('info_url') )

def test( request ):
    type = request.GET.get("type", '')
    response = apireq.get("https://repository.library.brown.edu/api/items/bdr:80246/")
    return HttpResponse(json.dumps(response.json()), content_type='application/json; charset=utf-8')
    



