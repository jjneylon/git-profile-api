import json

from flask import Blueprint, request, Response

from service.handlers import handle_get_profile


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/profile', methods=['GET'])
def get_profile():
    """ Endpoint for a consolidated profile resource """
    try:
        github_username = request.args['github']
        bitbucket_username = request.args['bitbucket']
    except IndexError as exc:
        return Response(json.dumps({"error": "No {} in request params".format(exc)}), status=400)

    profile_dict = handle_get_profile(github_username, bitbucket_username)
    return Response(json.dumps(profile_dict), status=200)
