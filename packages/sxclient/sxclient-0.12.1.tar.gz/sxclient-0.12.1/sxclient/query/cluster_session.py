'''
Copyright (C) 2012-2015 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import requests

from sxclient.query.auth import SXAuth
from sxclient.query.hostname_adapter import SXHostnameAdapter


class ClusterSession(requests.Session):
    '''
    Custom session object used by a QueryHandler object.

    Initialization parameters:
      - cluster -- Cluster data structure; cluster.name is used for SSL
        verification
      - user_data -- UserData object used for authentication
    '''

    def __init__(self, cluster, user_data=None):
        super(ClusterSession, self).__init__()
        self.mount('https://', SXHostnameAdapter(assert_hostname=cluster.name))
        if user_data is not None:
            self.auth = SXAuth(user_data)
        self.verify = cluster.verify_ssl_cert
