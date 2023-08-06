import requests.exceptions


class ApiError(requests.exceptions.HTTPError):
    def __init__(self, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)
        self.returned_data = self.response.json()

    def __str__(self):
        if 'message' in self.returned_data:
            return '{0} {1}: {2} ({3})'.format(
                self.returned_data['statusCode'], self.returned_data['error'],
                self.returned_data['message'], self.response.url)
        else:
            return '{0} {1} ({2})'.format(
                self.returned_data['statusCode'], self.returned_data['error'],
                self.response.url)
