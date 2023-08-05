"""event-insight.py
    This library provides a way to access IBM Watson Bluemix services.
    A Python Bluemix-Watson API which would make this module redundant is currently in stalled development by the
    Bluemix team. For now, this file's methodology is sufficient."""

import json
import os
import requests
from time import gmtime
import urllib


def _import_credentials(filename='concept_insight_credentials.json'):
    """
    Internal method which finds the credentials file describing the token that's needed to access Watson/Bluemix
    services.

    :param filename -- The filename at which Concept Insights service credentials are stored. Defaults to
    `concept_insight_credentials.json`.
    """
    if filename in [f for f in os.listdir('.') if os.path.isfile(f)]:
        data = json.load(open(filename))['credentials']
        return data
    else:
        raise IOError(
            'This API requires a Bluemix/Watson credentials token to work. Did you forget to define '
            'one? For more information refer to:\n\nhttps://github.com/ResidentMario/watsongraph#setup')


def _generate_token(filename='concept_insight_credentials.json', token_file='token.json'):
    """
    Generate the Base64 token that IBM uses for API authorization. Wraps `import_credentials()`. Itself a submethod
    of the `getToken()` method. See also `validateToken()`.

    :param filename -- The filename at which Concept Insights service credentials are stored. Defaults to
    `concept_insight_credentials.json`.
    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    credentials = _import_credentials(filename)
    r = requests.get(
        "https://gateway.watsonplatform.net/authorization/api/v2/token\?url=https://stream.watsonplatform.net" +
        "/concept-insights/api",
        auth=(credentials['username'], credentials['password']))
    if r.status_code == requests.codes.ok:
        f = open(token_file, 'w')
        f.write(json.dumps({'token': r.text, 'time': gmtime()}, indent=4))
        return r.text
    else:
        raise RuntimeError(
            'Could not resolve a Bluemix/Watson API token using the given credentials.' +
            'Are your account credentials correct?')


def _validate_token(token_file='token.json'):
    """
    The generateToken() method creates a JSON file with both a token and a time parameter.
    This methods checks if the token file is still valid. Tokens live for an hour, so if the token was generated
    less than an hour ago it should work. In that case the additional overhead of regenerating the token is not
    necessary! This method is a submethod of the primary-use `getToken()` method. See also `generateToken()`, above.

    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    if token_file in [f for f in os.listdir('.') if os.path.isfile(f)]:
        """
        The timestamp is in UTC. The timestamp is in the format [year, month, day, hour, minute, second, ..., ..., ...]
        Generated via `gmtime()` in `generateToken()`. See https://docs.python.org/2/library/time.html#time.struct_time
        In our case it's simplest to compare the hour parameter and make sure we haven't incremented into the next
        hour yet.
        """
        timestamp = json.load(open(token_file))['time']
        hourstamp = timestamp[3]
        if hourstamp - gmtime()[3] == 0:
            return True
        else:
            return False
    else:
        return False


def get_token(token_file='token.json'):
    """
    This is the primary-use access method meant to be used throughout the application. Implements `validateToken()`
    and `generateToken()` submethods, above. If a token exists that was created within the current hour, it is still
    valid, reused, and returned (fast). If a token exists but has expired, or does not exist at all, one is created
    and returned (requires networking, slower).

    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    if _validate_token():
        return json.load(open(token_file))['token']
    else:
        return _generate_token()


def annotate_text(text, content_type='text/plain', token_file='token.json'):
    """
    Given the text to be analyzed and a previous generated access token this method returns the result of a Watson
    API call to `annotate_text`. This method returns the raw, unprocessed result of an API call; its
    output is meant to be processed by other methods making use of API calls made using this method.

    :param text -- The text to be annotated.
    :param content_type -- This optional parameter defaults to `text/plain`, which expects plaintext input.
    `text/html` is the alternative option.
    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    token = get_token(token_file)
    base_url = 'https://gateway.watsonplatform.net/concept-insights/api/v2/graphs/wikipedia/en-20120601/annotate_text'
    headers = {'X-Watson-Authorization-Token': token, 'Content-Type': content_type, 'Accept': 'application/json'}
    dat = text.encode(encoding='UTF-8', errors='ignore')
    r = requests.post(base_url, headers=headers, data=dat)
    # Catch a recurring error of unknown server-side provenance. Further details:
    # https://github.com/ResidentMario/watsongraph/issues/6
    r.raise_for_status()
    return json.loads(r.text)


def get_related_concepts(label, level=0, limit=10, token_file='token.json'):
    """
    Given the name of a concept within the Wikipedia concept graph, returns the result of an API call to the
    `label_search` Watson method. This method requires the name of the concept that is to be searched for.
    That name must be precise.

    :param label -- The Concept label for whom relations are being fetched. Note that this method is executed on a
    label, not a Concept--executing it on a Concept would incur unnecessary additional overhead.
    :param level -- The limit placed on the depth of the graph. A limit of 0 is highest, corresponding with the
    most popular articles; a limit of 5 is the broadest and graphs to the widest cachet of articles. This
    parameter is a parameter that is passed directly to the IBM Watson API call.
    :param limit -- a cutoff placed on the number of related concepts to be returned. This parameter is passed
    directly to the IBM Watson API call.
    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    headers = {'X-Watson-Authorization-Token': get_token(token_file),
               'Content-Type': 'text/plain',
               'Accept': 'application/json'}
    # Percent encode the URI according to Wikipedia's encoding scheme.
    # noinspection PyUnresolvedReferences
    label = urllib.parse.quote(label.replace(' ', '_'), safe='_,')
    base_url = 'https://gateway.watsonplatform.net/concept-insights/api/v2/graphs/wikipedia/en-20120601'
    base_url += '/related_concepts?concepts=["/graphs/wikipedia/en-20120601/concepts/' + label
    base_url += '"]&level=' + str(level) + '&limit=' + str(limit)
    r = requests.get(base_url, headers=headers)
    r.raise_for_status()
    return json.loads(r.text)


# noinspection PyUnresolvedReferences
def get_relation_scores(label, list_of_target_labels, token_file='token.json'):
    """
    Given the name of a concept within the Wikipedia concept graph and a list of other concepts to be checked against,
    returns the result of an API call to the `relation_scores` Watson method. This method requires the name of
    the concept that is to be searched for. That name must be precise.

    :param label -- The Concept label for whom relations are being fetched. Note that this method is executed on a
    label, not a Concept--executing it on a Concept would incur unnecessary additional overhead.
    :param list_of_target_labels -- A list of other labels for which matching correlations will be fetched.
    :param token_file -- The filename at which the token (which this application saves as a file, not an object)
    will be stored. Defaults to `token.json`.
    """
    headers = {'X-Watson-Authorization-Token': get_token(token_file),
               'Content-Type': 'text/plain',
               'Accept': 'application/json'}
    # Percent encode the URI according to Wikipedia's encoding scheme.
    s_label = urllib.parse.quote(label.replace(' ', '_'), safe='_,')
    list_of_target_labels = [urllib.parse.quote(lb.replace(' ', '_'), safe='_,') for lb in list_of_target_labels]
    base_url = 'https://gateway.watsonplatform.net/concept-insights/api/v2/graphs/wikipedia/en-20120601'
    base_url += '/concepts/' + s_label + '/relation_scores?concepts=['
    for t_label in list_of_target_labels:
        base_url += '"/graphs/wikipedia/en-20120601/concepts/' + t_label + '",'
    base_url = base_url[:-1] + ']'
    r = requests.get(base_url, headers=headers)
    r.raise_for_status()
    return json.loads(r.text)
