from mock import MagicMock

from impaf.controller import Controller
from impaf.testing import ControllerCase
from impaf.testing import PyTestCase

from ..controller import FlashMessageController


class MockedFlashMessageController(Controller):

    def _create_widgets(self):
        self._create_widgets_runned = True


class ExampleFlashMessageController(
    FlashMessageController,
    MockedFlashMessageController,
):
    pass


class TestFlashMessageController(ControllerCase, PyTestCase):

    _object_cls = ExampleFlashMessageController

    def test_create_widgets(self):
        widget = MagicMock()
        self._object_cls._cls_flash_message_widget = widget
        madd_widget = self.madd_widget()

        self.object()._create_widgets()

        madd_widget.assert_called_once_with(
            'flashmsg',
            widget.return_value
        )
