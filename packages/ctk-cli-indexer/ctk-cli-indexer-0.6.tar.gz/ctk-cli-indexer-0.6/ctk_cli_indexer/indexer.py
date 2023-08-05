import sys, datetime
import elasticsearch

INDEX = 'cli'
DOC_TYPE = 'cli'

def create_elasticsearch_index(es):
    """es should be an elasticsearch.Elasticsearch instance"""
    es.indices.create(index = INDEX, ignore = 400) # ignore already existing index
    es.indices.put_mapping(index = INDEX, doc_type = DOC_TYPE, body = {
        DOC_TYPE : {
            "_timestamp" : { "enabled" : True },
            "properties" : {
                "contributor": {
                    "type"  :  "string",
                    "index" :  "not_analyzed"
                },
                "authors": {
                    "type"  :  "string",
                    "index" :  "not_analyzed"
                },
                "license": {
                    "type"  :  "string",
                    "index" :  "not_analyzed"
                },
            }
        }})
    # es.indices.delete('cli')
    

def update_elasticsearch_index(es, docs, source):
    # retrieve existing documents
    try:
        existing = [doc['_id'] for doc in
                    es.search(INDEX, DOC_TYPE, body = dict(
                        query = dict(
                            term = dict(
                                source = source)
                            )),
                        fields = ['_id'],
                        size = 10000)['hits']['hits']]
    except elasticsearch.exceptions.NotFoundError:
        existing = []

    # now update changed / add new documents:
    for timestamp, doc in docs:
        doc['source'] = source
        doc_id = '%s:%s' % (source, doc['name'])
        timestamp = datetime.datetime.fromtimestamp(timestamp)

        try:
            old = es.get(INDEX, doc_id, DOC_TYPE) # FIXME: with elasticsearch-2.1.1, this produces 404 warnings
        except elasticsearch.exceptions.NotFoundError:
            es.index(INDEX, DOC_TYPE, body = doc, id = doc_id, timestamp = timestamp)
            sys.stdout.write("added new document '%s'.\n" % doc_id)
        else:
            existing.remove(old['_id'])
            if old['_source'] != doc:
                es.index(INDEX, DOC_TYPE, body = doc, id = doc_id, timestamp = timestamp)
                sys.stdout.write("changed document '%s'.\n" % doc_id)
            else:
                sys.stdout.write("leaving '%s' alone, no change...\n" % doc_id)

    # finally, remove existing documents that were not contained in `docs`:
    for doc_id in existing:
        sys.stdout.write("removing '%s', which is no longer in the '%s' JSON...\n" % (doc_id, source))
        es.delete(INDEX, DOC_TYPE, doc_id)
