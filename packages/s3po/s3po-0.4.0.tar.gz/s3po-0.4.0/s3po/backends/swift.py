'''Deal with Swift.'''

import swiftclient.client
from swiftclient.exceptions import ClientException

from ..util import CountFile, retry, logger
from ..exceptions import UploadException, DownloadException


class Swift(object):
    '''Our connection to S3'''
    # The size of the chunk to download / upload
    chunk_size = 1024 * 1024

    def __init__(self, *args, **kwargs):
        # We explicitly disable retries so that we can manage that directly
        kwargs['retries'] = 0
        self.conn = swiftclient.client.Connection(*args, **kwargs)

    def download(self, bucket, key, fobj, retries, headers=None):
        '''Download the contents of bucket/key to fobj'''
        # Make a file that we'll write into
        fobj = CountFile(fobj)

        # Get its original location so we can go back to it if need be
        offset = fobj.tell()

        @retry(retries)
        def func():
            '''The bit that we want to retry'''
            try:
                resp_headers, response = self.conn.get_object(
                    bucket, key, resp_chunk_size=self.chunk_size, headers=headers)

                fobj.seek(offset)
                for chunk in response:
                    print 'Writing %s' % chunk
                    fobj.write(chunk)

                length = resp_headers.get('content-length')
                if not length:
                    logger.warn('No content-length provided -- cannot detect truncation.')
                elif fobj.count != int(length):
                    raise DownloadException('Downloaded only %i of %i bytes' % (
                        fobj.count, length))

            except ClientException:
                raise DownloadException('Key not found.')

        # Invoke the download
        func()

    def upload(self, bucket, key, fobj, retries, headers=None):
        '''Upload the contents of fobj to bucket/key with headers'''
        # Make our headers object
        headers = headers or {}

        @retry(retries)
        def func():
            try:
                self.conn.put_object(
                    bucket, key, fobj, chunk_size=self.chunk_size, headers=headers)
            except ClientException:
                raise UploadException('Failed to upload %s' % key)

        func()
