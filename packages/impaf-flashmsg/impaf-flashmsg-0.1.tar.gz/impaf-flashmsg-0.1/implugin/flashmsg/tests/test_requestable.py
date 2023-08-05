from impaf.testing import RequestCase
from impaf.testing import PyTestCase

from ..requestable import FlashMessageRequestable


class TestFlashMessageController(RequestCase, PyTestCase):

    _object_cls = FlashMessageRequestable

    def test_add_flashmsg(self):
        mrequest = self.mrequest()
        mrequest.session = {}

        self.object().feed_request(mrequest)
        self.object().add_flashmsg('msg', 'info')

        assert mrequest.session == {
            'flash_messages': [
                {
                    'message': 'msg',
                    'msgtype': 'info',
                },
            ]
        }
