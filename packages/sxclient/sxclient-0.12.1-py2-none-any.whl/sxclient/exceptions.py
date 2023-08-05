'''
Exceptions specific for the package.

Copyright (C) 2012-2015 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.

'''

__all__ = [
    'SXClientException', 'InvalidOperationParameter', 'InvalidUserKeyError',
    'SXClusterError', 'SXClusterNotFound', 'SXClusterInternalError',
    'SXClusterFatalError', 'SXClusterNonFatalError'
]


class SXClientException(Exception):
    '''
    General exception type for library-specific exceptions.
    '''


class InvalidOperationParameter(SXClientException):
    '''
    Should be raised when a parameter passed to operation is invalid.
    '''


class InvalidUserKeyError(SXClientException):
    '''
    Should be raised when a user key is invalid.
    '''


class SXClusterError(SXClientException):
    '''
    Should be raised when a problem occurs during communication with the
    cluster.
    '''


class SXClusterNonFatalError(SXClusterError):
    '''
    Should be raised when the cluster communication problem is non-fatal.
    '''


class SXClusterRequestTimeout(SXClusterNonFatalError):
    '''
    Should be raised when there's a request timeout.
    '''


class SXClusterTooManyRequests(SXClusterNonFatalError):
    '''
    Should be raised when there's too many requests to cluster.
    '''


class SXClusterNotFound(SXClusterNonFatalError):
    '''
    Should be raised when cluster responds with 404.
    '''


class SXClusterInternalError(SXClusterNonFatalError):
    '''
    Should be raised when cluster responds with >= 500.
    '''


class SXClusterFatalError(SXClusterError):
    '''
    Should be raised when the cluster communication problem is fatal.
    '''


class SXClusterClientError(SXClusterFatalError):
    '''
    Should be raised when the cluster communication problem is due to
    client's error.
    '''


class SXClusterPayloadTooLarge(SXClusterClientError):
    '''
    Should be raised when trying to upload a file bigger then volume's
    free space.
    '''


class SXClusterBadRequest(SXClusterClientError):
    '''
    Should be raised when making an invalid request to cluster.
    '''


class SXClusterUnauthorized(SXClusterClientError):
    '''
    Should be raised when trying to access cluster with invalid credentials.
    '''


class SXClusterForbidden(SXClusterClientError):
    '''
    Should be raised when trying to access cluster without expected privileges.
    '''
