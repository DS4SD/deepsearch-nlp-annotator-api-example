from connexion.exceptions import OAuthProblem

from nlp_annotator_api.config.config import conf


def check_apikey(token, required_scopes):
    api_key = conf.auth.api_key

    if not api_key:
        return {'uid': 'anonymous'}

    tokens = {
        api_key: {'uid': 'api_key'}
    }

    info = tokens.get(token)

    if not info:
        raise OAuthProblem('Invalid token')

    return info
