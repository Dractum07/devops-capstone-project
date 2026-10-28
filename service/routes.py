"""
Accounts Service REST API
"""
from flask import Blueprint, jsonify, make_response, request, url_for
from service.models import Account, DataValidationError

api = Blueprint("api", __name__)

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415


@api.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            paths=url_for("api.list_accounts", _external=True),
        ),
        HTTP_200_OK,
    )


@api.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an Account"""
    check_content_type("application/json")
    try:
        account = Account().deserialize(request.get_json())
    except DataValidationError as error:
        return jsonify(error=str(error)), HTTP_400_BAD_REQUEST
    account.create()
    location_url = url_for("api.read_accounts", account_id=account.id, _external=True)
    return (
        jsonify(account.serialize()),
        HTTP_201_CREATED,
        {"Location": location_url},
    )


@api.route("/accounts", methods=["GET"])
def list_accounts():
    """Lists all Accounts"""
    accounts = [account.serialize() for account in Account.all()]
    return jsonify(accounts), HTTP_200_OK


@api.route("/accounts/<int:account_id>", methods=["GET"])
def read_accounts(account_id):
    """Reads an Account"""
    account = Account.find(account_id)
    if not account:
        return (
            jsonify(error=f"Account with id [{account_id}] could not be found."),
            HTTP_404_NOT_FOUND,
        )
    return jsonify(account.serialize()), HTTP_200_OK


@api.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """Updates an Account"""
    check_content_type("application/json")
    account = Account.find(account_id)
    if not account:
        return (
            jsonify(error=f"Account with id [{account_id}] could not be found."),
            HTTP_404_NOT_FOUND,
        )
    try:
        account.deserialize(request.get_json())
    except DataValidationError as error:
        return jsonify(error=str(error)), HTTP_400_BAD_REQUEST
    account.update()
    return jsonify(account.serialize()), HTTP_200_OK


@api.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """Deletes an Account"""
    account = Account.find(account_id)
    if account:
        account.delete()
    return make_response("", HTTP_204_NO_CONTENT)


def check_content_type(media_type):
    """Aborts with 415 unless the request has the expected Content-Type"""
    from flask import abort  # pylint: disable=import-outside-toplevel

    if request.headers.get("Content-Type") != media_type:
        abort(HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {media_type}")
