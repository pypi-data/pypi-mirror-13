from impaf.controller import Controller

from .requestable import FlashMessageRequestable
from .widget import FlashMessageWidget


class FlashMessageController(Controller, FlashMessageRequestable):
    _cls_flash_message_widget = FlashMessageWidget

    def _create_widgets(self):
        super()._create_widgets()
        self.add_widget('flashmsg', self._cls_flash_message_widget())
