'''
Copyright (C) 2012-2015 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.operations.base import BaseOperation
from sxclient.models.query_parameters import QueryParameters


__all__ = ['ListNodes', 'GetNodeStatus']


class ListNodes(BaseOperation):
    '''
    List the cluster's nodes.

    Required access: normal.
    '''

    def call(self):
        nodes = self.cluster.iter_ip_addresses()
        response = self.call_on_nodelist(nodes)
        new_nodes = response.json()[u'nodeList']
        self.cluster.set_ip_addresses(new_nodes)
        return response

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            bool_params={'nodeList'}
        )


class GetNodeStatus(BaseOperation):
    '''
    Get status information about the node specified by the address.

    Required access: admin.

    Query-specific parameters:
      - node_address -- address of the node to connect to
    '''

    def call(self, node_address):
        return self.call_on_node(node_address)

    def _generate_query_params(self):
        return QueryParameters(
            sx_verb='GET',
            path_items=['.status']
        )
