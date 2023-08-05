'''
Copyright (C) 2012-2015 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.operations.base import BaseOperation
from sxclient.models.query_parameters import QueryParameters

__all__ = ['GetClusterStatus', 'GetClusterMetadata', 'SetClusterMetadata']


class GetClusterStatus(BaseOperation):
    '''
    Get status information about the cluster.

    Required access: admin.
    '''

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            bool_params={
                'clusterStatus',
                'operatingMode',
                'raftStatus',
                'distZones',
            }
        )


class GetClusterMetadata(BaseOperation):
    '''
    Get metadata associated with the cluster.

    Required access: normal.
    '''

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            bool_params={'clusterMeta'}
        )


class SetClusterMetadata(BaseOperation):
    '''
    Set metadata associated with the cluster.

    Required access: admin.

    Query-specific parameters:
      - clusterMeta -- dictionary containing key-value metadata pairs. The
        values have to be hex-encoded.
    '''

    def _generate_body(self, cluster_meta):
        return {u'clusterMeta': cluster_meta}

    def _generate_query_params(self, cluster_meta):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=['.clusterMeta']
        )
