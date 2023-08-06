from django.utils.translation import gettext as _

from enumerify.enum import Enum


class DeviceKind(Enum):
    IOS = 0
    ANDROID = 1
    WIN_RT = 2
    WIN_PHONE = 3
    DOT_NET = 4

    i18n = (
        _('iOS'),
        _('Android'),
        _('Windows RT'),
        _('Windows Phone'),
        _('.NET'),
    )

    @classmethod
    def get_parse_choices(cls):
        """
        Maps int values with values that are accepted by the Parse API
        """
        return (
            (cls.IOS, "ios"),
            (cls.ANDROID, "android"),
            (cls.WIN_RT, "winrt"),
            (cls.WIN_PHONE, "winphone"),
            (cls.DOT_NET, "dotnet"),
        )

    @classmethod
    def get_parse_value(cls, value):
        dict_ = dict(cls.get_parse_choices())
        return dict_[value]
