from carto.api_keys import APIKeyManager

from ...auth import get_default_credentials


class AuthAPIClient:
    """AuthAPIClient class is a client of the CARTO Auth API.
    More info: https://carto.com/developers/auth-api/.

    Args:
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            credentials of user account. If not provided, a default credentials
            (if set with :py:meth:`set_default_credentials <cartoframes.auth.set_default_credentials>`)
            will attempted to be used.

    """
    def __init__(self, credentials=None):
        credentials = credentials or get_default_credentials()
        self._api_key_manager = _get_api_key_manager(credentials)

    def create_api_key(self, sources, name, apis=['sql', 'maps'], permissions=['select']):
        tables = []
        for source in sources:
            table_names = source.get_table_names()
            for table_name in table_names:
                tables.append(_get_table_dict(source.schema(), table_name, permissions))

        api_key = self._api_key_manager.create(
            name=name,
            apis=apis,
            tables=tables)

        return api_key.token


def _get_table_dict(schema, name, permissions):
    return {
        'schema': schema,
        'name': name,
        'permissions': permissions
    }


def _get_api_key_manager(credentials):
    auth_client = credentials.get_api_key_auth_client()
    return APIKeyManager(auth_client)
