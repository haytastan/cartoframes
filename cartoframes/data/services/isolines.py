from __future__ import absolute_import

from ... import context
from ...auth import get_default_credentials
from carto.exceptions import CartoException
from cartoframes.data import Dataset
import pandas as pd
import uuid


# TODO: add count (num_rows) method to Dataset
def _count(context, dataset):
    if hasattr(dataset, 'dataframe') and dataset.dataframe is not None:
        return len(dataset.dataframe.index)
    elif hasattr(dataset, 'table_name') and dataset.table_name:
        result = context.execute_query("SELECT COUNT(*) FROM {table}".format(table=dataset.table_name))
    else:
        result = context.execute_query("SELECT COUNT(*) FROM ({query}) _query".format(query=dataset.query))
    return result.get('rows')[0].get('count')


def _generate_temp_table_name(base=None):
    return (base or 'table') + '_' + uuid.uuid4().hex[:10]


class Isolines(object):

    def __init__(self, credentials=None):
        self._credentials = credentials or get_default_credentials()
        self._context = context.create_context(self._credentials)

    def isochrones(self, source, range, **args):
        return self._iso(source, range, **args, function='isochrone')

    def isodistances(self, source, range, **args):
        return self._iso(source, range, **args, function='isodistance')

    def _iso(self,
             source,
             range,
             dry_run=False,
             table_name=None,
             if_exists=None,
             dataframe=False,
             is_destination=None,
             mode='car',
             mode_type=None,
             mode_traffic=None,
             resolution=None,
             maxpoints=None,
             quality=None,
             with_source_id=True,
             with_source_geom=False,
             function=None
    ):
        # we could default source_id=True for table source and
        # source_geom=True for dataframe source

        input_dataframe = None
        if isinstance(source, pd.DataFrame):
            input_dataframe = source
            source = Dataset(input_dataframe)

        if dry_run:
            num_rows = _count(self._context, source)
            return {'required_quota': num_rows * len(range)}

        temporary_table_name = False

        if source.table_name:
            source_query = 'SELECT * FROM {table}'.format(table=source.table_name)
        elif hasattr(source, 'query') and source.query:
            source_query = source.query
        else:  # source.is_local()
            # upload to temporary table
            temporary_table_name = _generate_temp_table_name()
            source.upload(table_name=temporary_table_name, credentials=self._credentials)
            source_query = 'SELECT * FROM {table}'.format(table=temporary_table_name)

        iso_function = '_cdb_{function}_exception_safe'.format(function=function)
        # TODO: use **options argument?
        options = {
            'is_destination': is_destination,
            'mode_type': mode_type,
            'mode_traffic': mode_traffic,
            'resolution': resolution,
            'maxpoints': maxpoints,
            'quality': quality
        }
        iso_options = [str(k)+'='+str(v) for k, v in options.items() if v is not None]
        iso_options = "ARRAY[{opts}]".format(opts=','.join(iso_options))
        source_geom = 'source_geom,' if with_source_geom else ''  # TODO: this is redundant with `center`
        source_id = 'source_id,' if with_source_id else ''
        iso_ranges = 'ARRAY[{ranges}]'.format(ranges=','.join([str(r) for r in range]))

        sql = """
          WITH _source AS ({source_query}),
          _isos AS (
              SELECT
                _source.cartodb_id AS source_id,
                _source.the_geom AS source_geom,
                {iso_function}(
                    _source.the_geom,
                    '{mode}',
                    {iso_ranges}::integer[],
                    {iso_options}::text[]
                ) AS _iso
              FROM _source
          )
          SELECT
            row_number() OVER () AS cartodb_id,
            {source_id}
            {source_geom}
            (_iso).data_range,
            (_iso).center,
            (_iso).the_geom
          FROM _isos
        """.format(
              iso_function=iso_function,
              source_query=source_query,
              source_id=source_id,
              source_geom=source_geom,
              mode=mode,
              iso_ranges=iso_ranges,
              iso_options=iso_options
            )

        if table_name:
            dataset = Dataset(sql)
            dataset.upload(table_name=table_name, credentials=self._credentials, if_exists=if_exists)
            result = Dataset(table_name)
            # TODO: should we return a Dataframe if the input was a Dataframe
            # if input_dataframe:
            #     result = result.download()
        else:
            # It would be nice to use execute_long_running_query, but we need the results
            result = Dataset(sql).download()
            # TODO: should we return a Dataset if the input was not a Dataframe?
            # if not input_dataframe:
            #     result = Dataset(result)

        if temporary_table_name:
            Dataset(temporary_table_name, credentials=self._credentials).delete()

        return result
