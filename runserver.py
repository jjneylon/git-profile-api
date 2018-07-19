from service import app
from service.routes import api_blueprint


app.register_blueprint(api_blueprint)


if __name__ == '__main__':
    app.run()
