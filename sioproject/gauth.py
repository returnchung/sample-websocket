import jwt
import requests
from collections import defaultdict
from datetime import datetime, timedelta


def get_oauth_access_token(
    service_account_credential, scopes, granted_user=None, session=None
):
    """
    Document: https://developers.google.com/identity/protocols/OAuth2ServiceAccount
    Instruction:
     1. Prepare a service account and download the credential JSON file.
     2. Load the credential in string with UTF-8 as the service_account_credential.
        And it contains follows to get access token:
        - User email address
        - Private key
        - Token URI endpoint
     3. Creating a JWT with defined payload, algorithm RS256 and specific private key.
     4. Using the token URI and JWT to get access token.
    """

    _credential = defaultdict(str)
    try:
        _credential.update(service_account_credential)
    except (TypeError, ValueError):
        print(
            f"Invalid service_account_credential {type(service_account_credential)}"
        )
        return ""

    current_time = datetime.now()
    client_email = _credential["client_email"]
    token_uri = _credential["token_uri"]
    encoded_key = _credential["private_key"]
    claim = dict(
        iss=client_email,
        scope=" ".join(scopes),
        aud=token_uri,
        exp=int((current_time + timedelta(hours=1)).timestamp()),
        iat=int(current_time.timestamp()),
        # Additional claims for application that can request permission to act
        # on behalf of a particular user in an organization.
        sub=granted_user,
    )
    try:
        authed_jwt = jwt.encode(claim, encoded_key, algorithm="RS256")
        token_payload = dict(
            grant_type="urn:ietf:params:oauth:grant-type:jwt-bearer",
            assertion=authed_jwt,
        )
        response = requests.post(token_uri, data=token_payload).json()
        return f"""{response["token_type"]} {response["access_token"]}"""
    except Exception as e:
        print(str(e))
        return ""


def get_project_id(service_account_credential):
    # NOTE: Default is "None" string if the project id is not found in credential to
    # prevent the invalid restful api path.

    default = "None"
    _credential = defaultdict(str)
    try:
        _credential.update(service_account_credential)
        return _credential["project_id"] or default
    except (TypeError, ValueError):
        print(
            f"Invalid service_account_credential {type(service_account_credential)}"
        )
        return default
