# fluffy-id

Simple http service to make GUID.

## install

    $ pip install git+http://github.com/yoophi/guid-server.git

## run

Simple shell script to run http server `fluff_id` will be installed when you install this package using `pip`.

    $ fluffy_id runserver [-p 7001 -h 0.0.0.0]
    
## sample request

    $ http :7001/guid
    HTTP/1.0 200 OK
    Content-Length: 52
    Content-Type: application/json
    Date: Wed, 30 Sep 2015 13:37:20 GMT
    Server: Werkzeug/0.10.4 Python/2.7.10

    {
        "guid": 12109964295484212795, 
        "shard_id": 1
    }

    $ http :7001/guid/100
    HTTP/1.0 200 OK
    Content-Length: 54
    Content-Type: application/json
    Date: Wed, 30 Sep 2015 13:37:47 GMT
    Server: Werkzeug/0.10.4 Python/2.7.10

    {
        "guid": 12109964522010284604, 
        "shard_id": 100
    }

