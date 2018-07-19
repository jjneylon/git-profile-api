import argparse

from service import app
from service.routes import api_blueprint


parser = argparse.ArgumentParser(description='Run Git Profile API Server.')
parser.add_argument('-H', '--hostname', type=str, default='127.0.0.1', help='the hostname for the api server')
parser.add_argument('-P', '--port', type=int, default='5000', help='the port for the api server')

args = parser.parse_args()

app.register_blueprint(api_blueprint)


if __name__ == '__main__':
    app.run(args.hostname, port=args.port)
