from django.utils.translation import ugettext as _

class DataFormatError(Exception):
    def __init__(self, msg=_('data format error')):
        self.msg = msg

IllegalMixCollation = 1267
