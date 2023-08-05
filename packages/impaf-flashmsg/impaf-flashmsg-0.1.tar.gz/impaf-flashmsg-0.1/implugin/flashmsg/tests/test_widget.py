from impaf.testing import RequestCase
from impaf.testing import PyTestCase
from impaf.testing import cache

from ..widget import FlashMessageWidget
from ..models import FlashMessage


class TestFlashMessageWidget(RequestCase, PyTestCase):
    _object_cls = FlashMessageWidget

    @cache
    def object(self):
        self.mregistry()
        obj = super().object()
        obj.feed_request(self.mrequest())

        return obj

    @cache
    def session(self):
        self.mrequest().session = {}
        return self.mrequest().session

    @cache
    def context(self):
        self.object().context = {}
        return self.object().context

    def test_simple(self):
        widget = self.object()
        session = self.session()
        session['flash_messages'] = [FlashMessage('one', 'info').to_dict()]
        context = self.context()

        widget.make()

        message = context['messages'][0]
        assert message.to_dict() == FlashMessage('one', 'info').to_dict()
