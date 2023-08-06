# print('caca'*1000)
# import haystack
# except Exception:
#     print('dumnezaii tai' * 1000)
# from haystack.exceptions import MissingDependency
# from django.core.exceptions import ImproperlyConfigured
# from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend


def check(request):
    return {'1': 2}
    # if error:
    #     return {'elasticsearch': {'error': error}}
    # try:
    #     actual_backend = connections['default'].get_backend()
    # except (NameError, MissingDependency):
    #     actual_backend = None
    # actual_backend = default_engine.get_backend()
    # if actual_backend and not isinstance(actual_backend, ElasticsearchSearchBackend):
    #     raise ImproperlyConfigured('Elastic search is not your default')

    # try:
    #     cluster_health = actual_backend.conn.cluster.health()
    #     info = actual_backend.conn.info()
    # except (AttributeError, ConnectionError) as e:
    #     return {'elasticsearch': {'error': str(e)}}
    # except ConnectTimeoutError as e:
    #     return {'elasticsearch': {'error': str(e)}}

    # return {
    #     'elasticsearch': {
    #         'cluster_health': cluster_health,
    #         'info': info}}


# def _elasticsearch_lookup():
#     for engine in connections:
#         if isinstance(engine.get_backend(), ElasticsearchSearchBackend):
#             return engine.get_backend()
