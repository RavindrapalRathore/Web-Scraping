from scrapy import Request
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            spider.logger.info(f'Retrying {request.url} (status {response.status}): {reason}')
            return self._retry(request, reason, spider) or response

        return response
