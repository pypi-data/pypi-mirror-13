from implugin.beaker import BeakerRequestable
from .models import FlashMessage


class FlashMessageRequestable(BeakerRequestable):

    def add_flashmsg(self, *args, **kwargs):
        data = self.request.session.get('flash_messages', [])
        data.append(FlashMessage(*args, **kwargs).to_dict())
        self.request.session['flash_messages'] = data
