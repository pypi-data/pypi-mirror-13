import servant
import flask


"""

Javascript -> http://host/blah -> REST Layer |
                                             |
                            | ---------------------> HTTP Service Server via UWSGI
                            |
Bertha -> servant.client -> |
                            |
                            |   ---> local library


"""


@route('/')
def receive(request):
    name = request.PATH[0])
    version = request.PATH[0])
    callback = request.PATH[0])

    client = servant.client.Client(name, verion)
    #client.configure('http', 'payments.clearcare.it', 80)

    cb = getattr(client, callback)
    result = cb(**request.POST)

    results = transform_to_frontend(result)

    return results
