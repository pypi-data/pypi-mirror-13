from mock import sentinel

from impaf.testing import PyTestCase

from ..models import FlashMessage


class TestFlasMessage(PyTestCase):
    _object_cls = FlashMessage

    def test_to_dict(self):
        obj = self.object(sentinel.message, sentinel.msgtype)
        assert obj.to_dict() == {
            'message': sentinel.message,
            'msgtype': sentinel.msgtype,
        }

    def test_from_dict(self):
        obj = self.object()
        obj.from_dict({
            'message': sentinel.message,
            'msgtype': sentinel.msgtype,
        })

        assert obj.message == sentinel.message
        assert obj.msgtype == sentinel.msgtype
