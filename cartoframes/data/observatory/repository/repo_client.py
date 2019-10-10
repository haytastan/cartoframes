from __future__ import absolute_import

from ...clients import SQLClient
from ....auth import Credentials
from ..utils import get_subscription_ids


class RepoClient(object):

    __instance = None

    def __init__(self):
        self._user_credentials = None
        self._do_credentials = Credentials('do-metadata', 'default_public')
        self.client = SQLClient(self._do_credentials)

    def set_user_credentials(self, credentials):
        self._user_credentials = credentials

    def get_countries(self, filters=None):
        query = 'SELECT DISTINCT view.country_id AS id FROM datasets_public view'
        return self._run_query(query, filters)

    def get_categories(self, filters=None):
        query = 'SELECT view.* FROM categories_public view'
        return self._run_query(query, filters)

    def get_categories_joined_datasets(self, filters=None):
        query = 'SELECT DISTINCT c.* FROM categories_public c, datasets_public view'
        return self._run_query(query,  filters, ['c.id = view.category_id'])

    def get_providers(self, filters=None):
        query = 'SELECT view.* FROM providers_public view'
        return self._run_query(query, filters)

    def get_variables(self, filters=None):
        query = 'SELECT view.* FROM variables_public view'
        return self._run_query(query, filters)

    def get_variables_groups(self, filters=None):
        query = 'SELECT view.* FROM variables_groups_public view'
        return self._run_query(query, filters)

    def get_geographies(self, filters=None):
        query = 'SELECT view.* FROM geographies_public view'

        extra_condition = []
        if self._user_credentials is not None:
            ids = get_subscription_ids(self._user_credentials)
            extra_condition.append('view.id IN ({})'.format(ids))

        return self._run_query(query, filters, extra_condition)

    def get_geographies_joined_datasets(self, filters=None):
        query = 'SELECT DISTINCT g.* FROM geographies_public g, datasets_public view'
        return self._run_query(query,  filters, ['g.id = view.geography_id'])

    def get_datasets(self, filters=None):
        query = 'SELECT view.* FROM datasets_public view'

        extra_condition = []
        if self._user_credentials is not None:
            ids = get_subscription_ids(self._user_credentials)
            extra_condition.append('view.id IN ({})'.format(ids))

        return self._run_query(query, filters, extra_condition)

    def _run_query(self, query, filters, extra_conditions=None):
        conditions = self._compute_conditions(filters, extra_conditions)

        if len(conditions) > 0:
            where_clause = ' AND '.join(conditions)
            query += ' WHERE {}'.format(where_clause)

        return self.client.query(query)

    def _compute_conditions(self, filters, extra_conditions):
        conditions = extra_conditions or []

        if filters is not None and len(filters) > 0:
            conditions.extend(["view.{} = '{}'".format(key, value) for key, value in filters.items()])

        return conditions

    def __new__(cls):
        if not RepoClient.__instance:
            RepoClient.__instance = object.__new__(cls)
        return RepoClient.__instance
