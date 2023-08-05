from boto.s3 import connect_to_region as s3_connect_to_region
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from .base import Base


class S3(Base):
    def __init__(self, configs):
        self.local_key = 'fakes3'
        self.connect(configs)

    def connect_fake(self):
        self.conn = S3Connection(
            'foo',
            'bar',
            is_secure=False,
            port=4567,
            host='localhost',
            calling_format=OrdinaryCallingFormat())

    def connect_real(self, configs):
        self.conn = s3_connect_to_region(
            configs['aws']['region'],
            aws_access_key_id=configs['aws']['access_key'],
            aws_secret_access_key=configs['aws']['secret_key'],
            calling_format=OrdinaryCallingFormat())

    def get_bucket(self, bucket_name):
        bucket_names = [b.name for b in self.conn.get_all_buckets()]
        if bucket_name in bucket_names:
            return self.conn.get_bucket(bucket_name)
        else:
            return self.conn.create_bucket(bucket_name)
