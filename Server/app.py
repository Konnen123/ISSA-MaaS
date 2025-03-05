from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec import FlaskApiSpec

from Controllers.authentication_controller import login_user, auth_bp, register_user
from Utils.database_init import init_db

app = Flask(__name__)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Backend APIs',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})

docs = FlaskApiSpec(app)

app.register_blueprint(auth_bp)

docs.register(login_user, blueprint='auth')
docs.register(register_user, blueprint='auth')

init_db()

if __name__ == '__main__':
    app.run(debug=True)