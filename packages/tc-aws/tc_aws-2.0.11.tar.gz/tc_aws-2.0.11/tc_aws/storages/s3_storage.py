#coding: utf-8

# Copyright (c) 2015, thumbor-community
# Use of this source code is governed by the MIT license that can be
# found in the LICENSE file.

from tornado.concurrent import return_future

from thumbor.storages import BaseStorage

from ..aws.storage import AwsStorage

class Storage(AwsStorage, BaseStorage):
    """
    S3 Storage
    """
    def __init__(self, context):
        """
        Constructor
        :param Context context: Thumbor's context
        """
        BaseStorage.__init__(self, context)
        AwsStorage.__init__(self, context, 'TC_AWS_STORAGE')

    def put(self, path, bytes):
        """
        Stores image
        :param string path: Path to store data at
        :param bytes bytes: Data to store
        :return: Path where data is stored
        :rtype: string
        """
        self.set(bytes, self._normalize_path(path))

        return path

    @return_future
    def get(self, path, callback):
        """
        Gets data at path
        :param string path: Path for data
        :param callable callback: Callback function for once the retrieval is done
        """

        def parse_body(key):
            if key is None or self._get_error(key) is not None:
                callback(None)
            else:
                callback(key['Body'].read())

        super(Storage, self).get(path, callback=parse_body)


    def resolve_original_photo_path(self, filename):
        """
        Determines original path for file
        :param string filename: File to look at
        :return: Resolved path (here it is the same)
        :rtype: string
        """
        return filename
