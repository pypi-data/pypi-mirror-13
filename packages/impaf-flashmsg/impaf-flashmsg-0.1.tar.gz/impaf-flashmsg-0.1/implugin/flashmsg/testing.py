from impaf.testing import ControllerCase
from impaf.testing import cache


class FlashMessageCase(ControllerCase):

    @cache
    def madd_flashmsg(self):
        return self.pobject(self.object(), 'add_flashmsg')
