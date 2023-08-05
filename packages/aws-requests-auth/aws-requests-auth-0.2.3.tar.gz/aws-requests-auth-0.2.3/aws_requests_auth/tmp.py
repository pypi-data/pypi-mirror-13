from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import connections


access_key = 'foo'
secret_key = 'bar'
host = 'search-gb-search-services-mkqma5oe24zugqqbojsuewvv7m.us-east-1.es.amazonaws.com'
port = 80
aws_region = 'us-east-1'
aws_service = 'es'

# access_key = 'fake_access_key'
# secret_key = 'fake_secret_key'
# host = 'search-foo.us-east-1.es.amazonaws.com'
# port = 80
# aws_region = 'us-east-1'
# aws_service = 'es'

auth = AWSRequestsAuth(aws_access_key=access_key,
                       aws_secret_access_key=secret_key,
                       aws_host=host,
                       aws_region=aws_region,
                       aws_service=aws_service)

es_client = Elasticsearch(host=host,
                          port=port,
                          connection_class=RequestsHttpConnection,
                          http_auth=auth)

connections.connections.create_connection(host=host,
                                          port=port,
                                          http_auth=auth,
                                          connection_class=RequestsHttpConnection)

def do_tests(es_client):
    print '\n\nRunning info'
    es_client.info()

    print '\n\nRunning stats("*'')'
    es_client.indices.stats('*')

    print '\n\nRunning stats(" foo.*'')'
    es_client.indices.stats(' foo.*')

    print '\n\nRunning /account/?human=True'
    es_client.indices.get('account', human=True)

do_tests(es_client)
