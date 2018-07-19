import json

from flask import abort, Blueprint, request, Response

from service import handlers


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        github_username = request.args['github']
        bitbucket_username = request.args['bitbucket']
    except IndexError as exc:
        return Response('No {} in request params'.format(exc), status=400)

    github_response = handlers.get_user_profile('github', github_username)
    bitbucket_response = handlers.get_user_profile('bitbucket', bitbucket_username)
    return Response('{}', status=200)
