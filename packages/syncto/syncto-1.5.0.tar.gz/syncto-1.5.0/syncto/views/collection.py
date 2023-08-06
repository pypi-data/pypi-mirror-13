from pyramid.security import NO_PERMISSION_REQUIRED

from cliquet import Service
from cliquet.statsd import statsd_count
from cliquet.errors import raise_invalid

from syncto.authentication import build_sync_client
from syncto.headers import import_headers, export_headers


collection = Service(name='collection',
                     description='Firefox Sync Collection service',
                     path=('/buckets/{bucket_id}/collections'
                           '/{collection_name}/records'),
                     cors_headers=('Next-Page', 'Total-Records',
                                   'Last-Modified', 'ETag', 'Quota-Remaining'))


@collection.get(permission=NO_PERMISSION_REQUIRED)
def collection_get(request):
    collection_name = request.matchdict['collection_name']
    sync_client = build_sync_client(request)

    headers = import_headers(request)

    params = {}
    if '_since' in request.GET:
        try:
            params['newer'] = '%.2f' % (int(request.GET['_since']) / 1000.0)
        except ValueError:
            error_msg = ("_since should be a number.")
            raise_invalid(request,
                          location="querystring",
                          name="_since",
                          description=error_msg)

    if '_limit' in request.GET:
        params['limit'] = request.GET['_limit']

    if '_token' in request.GET:
        params['offset'] = request.GET['_token']

    if '_sort' in request.GET:
        if request.GET['_sort'] in ('-last_modified', 'newest'):
            params['sort'] = 'newest'

        elif request.GET['_sort'] in ('-sortindex', 'index'):
            params['sort'] = 'index'

        elif request.GET['_sort'] in ('last_modified', 'oldest'):
            params['sort'] = 'oldest'

        else:
            error_msg = ("_sort should be one of ('-last_modified', 'newest', "
                         "'-sortindex', 'index', 'last_modified', 'oldest')")
            raise_invalid(request,
                          location="querystring",
                          name="_sort",
                          description=error_msg)

    if 'in_ids' in request.GET:
        params['ids'] = [record_id.strip() for record_id in
                         request.GET['in_ids'].split(',') if record_id]

    records = sync_client.get_records(collection_name, full=True,
                                      headers=headers, **params)

    statsd_count(request, "syncclient.status_code.200")

    for r in records:
        r['last_modified'] = int(r.pop('modified') * 1000)

    # Configure headers
    export_headers(sync_client.raw_resp, request)

    if '_limit' in request.GET and 'Total-Records' in request.response.headers:
        del request.response.headers['Total-Records']

    return {'data': records or []}
