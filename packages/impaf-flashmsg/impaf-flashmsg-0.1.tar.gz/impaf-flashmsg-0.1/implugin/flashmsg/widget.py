from implugin.jinja2.widget import SingleWidget

from .models import FlashMessage
from .requestable import FlashMessageRequestable


class FlashMessageWidget(SingleWidget, FlashMessageRequestable):

    template = 'implugin.flashmsg:templates/main.jinja2'

    def make(self):
        self.context['messages'] = []
        for data in self.session.get('flash_messages', []):
            obj = FlashMessage()
            obj.from_dict(data)
            self.context['messages'].append(obj)
        self.session['flash_messages'] = []
