from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage(S3Boto3Storage):
    """
    Implementation that extends S3Boto3Storage for multi-tenant setups.
    """
    bucket_name = settings.AWS_CUSTOMER_MEDIA_BUCKET_NAME

    @property  # not cached like in parent of S3Boto3Storage class
    def location(self):
        _location = ""
        return _location

    def url(self, name, parameters=None, expire=30):
        """
        The urls generated for the user media files expire in 30 seconds
        """
        # Preserve the trailing slash after normalizing the path.
        name = self._normalize_name(self._clean_name(name))

        params = parameters.copy() if parameters else {}
        params['Bucket'] = self.bucket.name
        params['Key'] = self._encode_name(name)
        url = self.bucket.meta.client.generate_presigned_url('get_object', Params=params,
                                                             ExpiresIn=expire)
        if self.querystring_auth:
            return url
        return self._strip_signing_parameters(url)
