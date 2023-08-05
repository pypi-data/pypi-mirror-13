'''
Copyright (C) 2012-2015 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.tools import toutf8
from sxclient.exceptions import InvalidOperationParameter
from sxclient.operations.base import BaseOperation
from sxclient.models.query_parameters import QueryParameters
from sxclient.query.query_handler import BinaryBodyQueryHandler


__all__ = ['GetBlocks', 'CreateBlocks']


class BinaryOperation(BaseOperation):
    HIDDEN = True
    QUERY_HANDLER = BinaryBodyQueryHandler

    def json_call(self, *args, **kwargs):
        name = self.__class__.__name__
        raise AttributeError(
            "Can't call .json_call method on a binary operation [%s]. "
            "Use raw .call method." % name
        )


class GetBlocks(BinaryOperation):
    '''
    Retrieves one or more blocks of data.

    Required access: ordinary user

    Query-specific parameters:
      - blocksize -- is the size of the blocks to retrieve
      - blocks -- a list of names of blocks to retrive

    You should sort block names alphabetically before passing them to the call
    of this operation to ensure that the response does not depend on block
    order.
    '''

    def _generate_query_params(self, blocksize, blocks):
        full_block_name = ''.join(blocks)
        return QueryParameters(
            sx_verb='GET',
            path_items=['.data', str(blocksize), full_block_name],
        )


class CreateBlocks(BinaryOperation):
    '''
    Saves one or more blocks of data to the SX cluster.

    Required access: valid upload token

    Query-specific parameters:
      - blocksize -- is the size of the blocks to retrieve
      - token -- is the upload token as received in the reply to
        the Initialize File request
      - content -- a binary content to push to the SX cluster. Note that
        if content is smaller then blocksize then it will be padded with nuls.
    '''

    def _generate_query_params(self, blocksize, token, content):
        return QueryParameters(
            sx_verb='PUT',
            path_items=['.data', str(blocksize), token]
        )

    def _generate_body(self, blocksize, token, content):
        blocksize = int(blocksize)
        content_length = len(content)
        rest = content_length % blocksize
        if rest > 0:
            diff = blocksize - rest
            content += '\0' * diff

        return content
