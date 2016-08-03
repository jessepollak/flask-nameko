# flask_nameko

A wrapper for using nameko services with Flask

## Installation

Install it via Clef's PyPI:

    pip install flask_nameko

## Usage

To start using `flask_nameko`, you need to create and configure a new `FlaskPooledClusterRpcProxy` singleton, which you'll use to communicate with your Nameko cluster.

    # __init__.py
    from flask import Flask
    from flask_nameko import FlaskPooledClusterRpcProxy

    rpc = FlaskPooledClusterRpcProxy()

    def create_app():
        app = Flask(__name__)
        app.config.update(dict(
            NAMEKO_AMQP_URI='amqp://localhost'
        ))

        rpc.init_app(app)

    app = create_app()

Then, you can use the `FlaskPooledClusterRpcProxy` singleton just as you would normally use a `ClusterRpcProxy`, by accessing individual services by name and calling methods on them:

    # routes.py

    from . import (
        app,
        rpc
    )

    @app.route('/'):
    def index():
        result = rpc.service.do_something('test')
        return result

## API

### Configuration

`FlaskPooledClusterRpcProxy` accepts all nameko configuration values, prefixed with the `NAMEKO_` prefix. In addition, it exposes additional configuration options:

* `NAMEKO_INITIAL_CONNECTIONS (int, default=2)` - the number of initial connections to the Nameko cluster to create
* `NAMEKO_MAX_CONNECTIONS (int, default=8)` - the max number of connections to the Nameko cluster to create before raises an error
* `NAMEKO_LAZY_LOAD_SERVICCES (bool, default=False)` - whether connections to services should be loaded when the service is accessed (False) or when a method is called on a service (True)

### Proxies

*flask_nameko.**FlaskPooledClusterRpcProxy**(app=None, lazy_load_services=False)*

   This class is used to create a pool of connections to a Nameko cluster. It provides the following options:
   
       * `lazy_load_services` - if this is true, the connection to a service is created when a method is called on a service rather than when the service is accessed

   *init_app(app=None)*

   Configure the proxy for a given app.

## Development

    $ git clone git@github.com:clef/flask_nameko.git flask_nameko
    $ cd flask_nameko
    $ make develop
