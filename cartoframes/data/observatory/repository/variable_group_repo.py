from __future__ import absolute_import

from .constants import DATASET_FILTER
from .entity_repo import EntityRepository


_VARIABLE_GROUP_ID_FIELD = 'id'
_ALLOWED_FILTERS = [DATASET_FILTER]


def get_variable_group_repo():
    return _REPO


class VariableGroupRepository(EntityRepository):

    def __init__(self):
        super(VariableGroupRepository, self).__init__(_VARIABLE_GROUP_ID_FIELD, _ALLOWED_FILTERS)

    def get_by_dataset(self, dataset_id):
        return self._get_filtered_entities({DATASET_FILTER: dataset_id})

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.variable_group import VariableGroup
        return VariableGroup

    def _get_rows(self, filters=None):
        return self.client.get_variables_groups(filters)

    def _map_row(self, row):
        return {
            'id': self._normalize_field(row, self.id_field),
            'name': self._normalize_field(row, 'name'),
            'dataset_id': self._normalize_field(row, 'dataset_id'),
            'starred': self._normalize_field(row, 'starred')
        }


_REPO = VariableGroupRepository()