class ImagefyException(Exception):
    pass


class ImagefyOperationException(ImagefyException):
    def __init__(self, message, operation, status=None, original_exc=None):
        super(ImagefyOperationException, self).__init__(message)
        self.operation = operation
        self.status = status
        self.original_exc = original_exc
