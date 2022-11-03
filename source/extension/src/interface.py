# coding: utf-8
from traceback import format_exc as tb

import unohelper
from com.sun.star.task import XJobExecutor

from core_constants import BTN_CHECK_PAIRS, BTN_DOTTED_UNDERLINE, \
    BTN_CONFIGURE, BTN_SWITCH_TOOLBAR, BTN_INSERT_ACCENT, \
    BTN_SET_FONTS, BTN_COLOR_DIGITS, ItemData

from core_functions import error_box

from item_functions import color_digits, set_fonts, check_pairs, \
    insert_accent, dotted_underline, switch_toolbar, configure


def item_factory(execute):

    class Item(unohelper.Base, XJobExecutor):
        def __init__(self, ctx):
            self.ctx = ctx

        def trigger(self, args):
            try:
                execute()
            except Exception:
                error_box(tb())
    return Item


item_actions = {
    BTN_COLOR_DIGITS: color_digits,
    BTN_SET_FONTS: set_fonts,
    BTN_CHECK_PAIRS: check_pairs,
    BTN_INSERT_ACCENT: insert_accent,
    BTN_DOTTED_UNDERLINE: dotted_underline,
    BTN_SWITCH_TOOLBAR: switch_toolbar,
    BTN_CONFIGURE: configure,
}

g_ImplementationHelper = unohelper.ImplementationHelper()

for item_name, action in item_actions.items():
    implementation = (item_factory(action), ItemData(item_name).url, ("com.sun.star.task.Job", ))
    g_ImplementationHelper.addImplementation(*implementation)
