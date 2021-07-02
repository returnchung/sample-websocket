# flask-socketio + GCP pub/sub on Cloud Run

## Introduction

[Flask-SocketIO — Flask-SocketIO  documentation](https://flask-socketio.readthedocs.io/en/latest/index.html)

Due to the Cloud Run is an http service, the flask-socketio is prefer solution to wrap websocket as a HTTP endpoint.

Besides, using the GCP pub/sub REST API rather than google-cloud-pubsub python SDK is only way to integrate into flask-socketio framework and avoid multi-threading callback outside of the http context issue.


## [Requirements](requirements.txt)


```
# ...
eventlet==0.30.2
# ...
```

> NOTE: eventlet should be less than 0.31 for compatibility.
> 
> `Gunicorn ImportError: cannot import name 'ALREADY_HANDLED' from 'eventlet.wsgi' in docker`


## Deployment

[Deployment — Flask-SocketIO  documentation](https://flask-socketio.readthedocs.io/en/latest/deployment.html#using-multiple-workers)

- Embedded

```sh
$ python sioproject/main.py
```

- Gunicorn

```sh
$ gunicorn -b :$PORT -k eventlet -w 1 sioproject.main:app
```
