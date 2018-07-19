from flask import Blueprint, request


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/user', methods=['GET'])
def get_user_profile():
    return '{}'
