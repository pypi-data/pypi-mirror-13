"""Unit test utilities.
"""

__author__ = ['Ryan Barrett <granary@ryanb.org>']

import appengine_config

import requests

from oauth_dropins.webutil.testutil import *


class TestCase(HandlerTest):
  """Base test class. Supports mocking requests calls."""

  def setUp(self):
    super(TestCase, self).setUp()
    for method in 'get', 'post':
      self.mox.StubOutWithMock(requests, method, use_mock_anything=True)
    self.stub_requests_head()

  def stub_requests_head(self):
    # don't make actual HTTP requests to follow original post url redirects
    def fake_head(url, **kwargs):
      resp = requests.Response()
      resp.url = url
      if '.' in url or url.startswith('http'):
        resp.headers['content-type'] = 'text/html; charset=UTF-8'
        resp.status_code = 200
      else:
        resp.status_code = 404
      return resp
    self.mox.stubs.Set(requests, 'head', fake_head)

    self._is_head_mocked = False  # expect_requests_head() sets this to True

  def expect_requests_head(self, *args, **kwargs):
    if not self._is_head_mocked:
      self.mox.StubOutWithMock(requests, 'head', use_mock_anything=True)
      self._is_head_mocked = True
    return self._expect_requests_call(*args, method=requests.head, **kwargs)

  def expect_requests_get(self, *args, **kwargs):
    return self._expect_requests_call(*args, method=requests.get, **kwargs)

  def expect_requests_post(self, *args, **kwargs):
    return self._expect_requests_call(*args, method=requests.post, **kwargs)

  def _expect_requests_call(self, url, response='', status_code=200,
                            content_type='text/html', method=requests.get,
                            redirected_url=None, response_headers=None,
                            **kwargs):
    """
    Args:
      redirected_url: string URL or sequence of string URLs for multiple redirects
    """
    resp = requests.Response()

    resp._text = response
    resp._content = (response.encode('utf-8') if isinstance(response, unicode)
                     else response)
    resp.encoding = 'utf-8'

    resp.url = url
    if redirected_url is not None:
      if isinstance(redirected_url, basestring):
        redirected_url = [redirected_url]
      assert isinstance(redirected_url, (list, tuple))
      resp.url = redirected_url[-1]
      for u in [url] + redirected_url[:-1]:
        resp.history.append(requests.Response())
        resp.history[-1].url = u

    resp.status_code = status_code
    resp.headers['content-type'] = content_type
    if response_headers is not None:
      resp.headers.update(response_headers)

    kwargs.setdefault('timeout', appengine_config.HTTP_TIMEOUT)
    if method is requests.head:
      kwargs['allow_redirects'] = True

    call = method(url, **kwargs)
    call.AndReturn(resp)
    return call
