# coding: utf-8

import time
import unohelper
from uno import createUnoStruct

from traceback import format_exc as tb
from typing import Tuple, List

from com.sun.star.awt import KeyEvent as KEY_EVENT
from com.sun.star.task import XJobExecutor

from core_constants import DEFAULT_FORMAT_WRITER_NODE_PATH, DEFAULT_FORMAT_WRITER_VALUE
from core_constants import DEFAULT_FORMAT_CALC_NODE_PATH, DEFAULT_FORMAT_CALC_VALUE

from core_constants import DEFAULT_FONT_NODE_PATH, DEFAULT_FONT, DEFAULT_COLOR, SPECIAL_FONT, \
    MISC_NODE_PATH, COLOR_DECIMAL_RED, COLOR_DECIMAL_BLUE, SYS_CHAR_ACCENT, \
    CHECKER_PAIRS_TO_CHECK, CHECKER_ESCAPED_CHARACTERS

from core_constants import BTN_CHECK_PAIRS, \
    BTN_DOTTED_UNDERLINE, BTN_CONFIGURE, BTN_SWITCH_TOOLBAR, BTN_INSERT_ACCENT, \
    BTN_SET_FONTS, BTN_COLOR_DIGITS, BTN_CONFIGURE, TOOLBAR_BUTTONS_NAMES

from core_constants import COLOR_REVISION_TEXT_DISPLAY_DELETE, \
COLOR_REVISION_TEXT_DISPLAY_CHANGED_ATTRIBUTE, COLOR_REVISION_TEXT_DISPLAY_INSERT, \
REVISION_TEXT_DISPLAY_NODE_PATH, JOBS_UPDATE_CHECK_NODE_PATH, ANNOTATION_UNIT

from core_constants import Key, EXTENSION_ID, URL_RESET_ATTRIBUTES, \
    DEFAULT_UI_LANGUAGE, UI_ELEMENT_LABELS, ButtonData, BUTTONS_NAMES, \
    DEFAULT_CHECKER_AUTHOR

from core_functions import get_current_document, call_dispatch, structify, mri
from core_functions import error_box, get_selection, msgbox, app_version
from core_functions import get_text, get_left_cursor, get_right_cursor, set_key_for_command, insert_string
from core_functions import add_menu_buttons, remove_menu_buttons, is_menu_buttons_on_toolbar
from core_functions import run_in_thread, get_ui_language, get_node_configuration
from core_functions import ModuleConfigurationManager, NodeConfigurationManager as NCM


def dotted_underline():
    selection = get_selection()
    if selection.getString():
        selection.CharUnderline = 0 if selection.CharUnderline == 3 else 3


def disable_tracking(func):
    def wrapper():
        doc = get_current_document()
        is_changes_record = doc.RecordChanges
        args_track_record = {"TrackChanges": False}
        call_dispatch(doc, ".uno:TrackChanges", structify(args_track_record))
        func()
        args_track_record = {"TrackChanges": is_changes_record}
        call_dispatch(doc, ".uno:TrackChanges", structify(args_track_record))
    return wrapper


@run_in_thread
@disable_tracking
def set_fonts():
    to_default_font()
    to_markup()


@run_in_thread
@disable_tracking
def color_digits():
    to_default_color()
    to_color()


def to_markup():
    # TODO
    ...


def to_color():
    # TODO
    ...


def to_default_font():
    selection = get_selection()
    if selection.getString():
        selection.setPropertyValue("CharFontName", DEFAULT_FONT)
        return

    doc = get_current_document()
    args = {"CharFontName.FamilyName": DEFAULT_FONT}
    call_dispatch(doc, ".uno:SelectAll", ())
    call_dispatch(doc, ".uno:CharFontName", structify(args))
    doc.getCurrentController().getViewCursor().collapseToEnd()


def to_default_color():
    selection = get_selection()
    if selection.getString():
        selection.setPropertyValue("CharColor", DEFAULT_COLOR)
        return

    doc = get_current_document()
    args = {"Color": DEFAULT_COLOR}
    call_dispatch(doc, ".uno:SelectAll", ())
    call_dispatch(doc, ".uno:Color", structify(args))
    doc.getCurrentController().getViewCursor().collapseToEnd()


def change_font_by_pattern(pattern: str, attrs: dict):
    document = get_current_document()
    text = document.Text
    view_cursor = document.getCurrentController().getViewCursor()

    start = text.createTextCursorByRange(view_cursor.Start)
    end = None if view_cursor.isCollapsed() else text.createTextCursorByRange(view_cursor.End)

    replace_descriptor = document.createReplaceDescriptor()
    replace_descriptor.SearchRegularExpression = True
    replace_descriptor.SearchString = pattern
    replace_descriptor.ReplaceString = "&"
    replace_descriptor.setReplaceAttributes(structify(attrs))

    if end is None:
        document.replaceAll(replace_descriptor)
        return

    find = document.findNext(start.End, replace_descriptor)
    while find and text.compareRegionEnds(find, end) >= 0:
        find.setPropertyValues(tuple(attrs.keys()), tuple(attrs.values()))
        find = document.findNext(find.End, replace_descriptor)


def button_class_factory(execute):

    class Button(unohelper.Base, XJobExecutor):
        def __init__(self, ctx):
            self.ctx = ctx

        def trigger(self, args):
            try:
                execute()
            except Exception:
                error_box(tb())
    return Button


def insert_accent():
    insert_string(chr(SYS_CHAR_ACCENT))


def switch_toolbar():
    def bar_button(name: str) -> Tuple:
        button = ButtonData(name)
        return structify({
            'CommandURL': button.execute,
            'Label': button.label_text(get_ui_language().upper()),
            'Type': 0,
            'IsVisible': True
        })

    menu_buttons_to_add = reversed([bar_button(NAME) for NAME in TOOLBAR_BUTTONS_NAMES])
    remove_menu_buttons() if is_menu_buttons_on_toolbar() else add_menu_buttons(menu_buttons_to_add)


def check_pairs():
    delete_existing_comments()
    mark_wrong_pairs()


def create_annotation(content: str = ""):
    def get_current_time():
        t = time.localtime()
        dtv = createUnoStruct("com.sun.star.util.DateTime")
        dtv.Year = t.tm_year
        dtv.Month = t.tm_mon
        dtv.Day = t.tm_mday
        dtv.Hours = t.tm_hour
        dtv.Minutes = t.tm_min
        dtv.Seconds = t.tm_sec
        dtv.NanoSeconds = 0
        return dtv

    anno = get_current_document().createInstance(ANNOTATION_UNIT)
    anno.Content = content
    anno.Author = DEFAULT_CHECKER_AUTHOR
    anno.DateTimeValue = get_current_time()
    return anno


def delete_existing_comments() -> None:
    xDocument = get_current_document()
    oEnum = xDocument.getTextFields().createEnumeration()

    while oEnum.hasMoreElements():
        oField = oEnum.nextElement()
        if not oField.supportsService(ANNOTATION_UNIT) or oField.Author != DEFAULT_CHECKER_AUTHOR:
            continue

        xTextRange = oField.getAnchor()
        oCur = xDocument.getText().createTextCursorByRange(xTextRange)
        oCur.Text.removeTextContent(oField)


def mark_wrong_pairs(list_of_pairs: List[Tuple[str, str]] = CHECKER_PAIRS_TO_CHECK):

    def check_quotes(pair_quotes: Tuple[str, str], quotes_list: List[str]) -> List[bool]:
        """
        :param pair_quotes: Пара проверяемых кавычек,
            например, ("«", "»",)
        :param quotes_list: Общий список кавычек в тексте,
            например, ['„', '“', '„', '“', '„', '“', '“', '„']
        :return: Список с результатами проверки, где True - кавычка на месте, False - ошибочная,
            например, [True, True, True, True, True, True, False, False]

        """
        opening_quote = pair_quotes[0]
        closing_quote = pair_quotes[1]
        quotes_length = len(quotes_list)
        result = list(quotes_list)

        for i in range(quotes_length):

            if result[i] != quotes_list[i]:
                continue

            if i == quotes_length - 1:
                result[i] = False
                continue

            if quotes_list[i] == opening_quote and quotes_list[i + 1] == closing_quote:
                result[i] = result[i + 1] = True
                continue

            result[i] = False
        return result

    def check_one_pair(pair: tuple) -> None:
        xDocument = get_current_document()
        xSearchDescr = xDocument.createSearchDescriptor()
        xSearchDescr.SearchRegularExpression = True
        pattern = rf"\{pair[0]}|\{pair[1]}" \
            if pair[0] in CHECKER_ESCAPED_CHARACTERS \
            else rf"{pair[0]}|{pair[1]}"
        xSearchDescr.SearchString = pattern

        xFounds = [x for x in xDocument.findAll(xSearchDescr)]
        list_of_quotes = [x.String for x in xFounds]
        checked_quotes = check_quotes(pair, list_of_quotes)

        for xFound, okay in zip(xFounds, checked_quotes):
            if okay:
                continue
            oCurs = xDocument.getText().createTextCursorByRange(xFound.getStart())
            oCurs.goRight(1, True)
            xFound.Text.insertTextContent(oCurs, create_annotation(f"Непарный знак '{xFound.String}'"), True)

    for p in list_of_pairs:
        check_one_pair(p)


def configure():
    set_default_font(DEFAULT_FONT)
    set_default_format(DEFAULT_FORMAT_WRITER_NODE_PATH, DEFAULT_FORMAT_WRITER_VALUE)
    set_default_format(DEFAULT_FORMAT_CALC_NODE_PATH, DEFAULT_FORMAT_CALC_VALUE)
    set_colors_of_changes_tracking()
    set_shortcut_keys()
    disable_show_tip_of_the_day()
    disable_collect_usage_information()
    disable_crash_report()
    disable_update_check()


def set_shortcut_keys():
    ctrl_space = KEY_EVENT()
    ctrl_space.Modifiers = Key.CTRL
    ctrl_space.KeyCode = Key.SPACE

    alt_d = KEY_EVENT()
    alt_d.Modifiers = Key.ALT
    alt_d.KeyCode = Key.D

    alt_a = KEY_EVENT()
    alt_a.Modifiers = Key.ALT
    alt_a.KeyCode = Key.A

    commands_list = [
        (ctrl_space, URL_RESET_ATTRIBUTES),
        (alt_d, ButtonData(BTN_DOTTED_UNDERLINE).execute),
        (alt_a, ButtonData(BTN_INSERT_ACCENT).execute), ]

    _ = [set_key_for_command(*item) for item in commands_list]


def set_default_font(font_name: str = DEFAULT_FONT) -> None:
    with NCM(DEFAULT_FONT_NODE_PATH) as node:
        node.Standard = font_name
        node.Caption = font_name
        node.Heading = font_name
        node.Index = font_name
        node.List = font_name


def set_default_format(node: str, value: str) -> None:
    with NCM(node) as format_node:
        format_node.ooSetupFactoryDefaultFilter = value


def disable_show_tip_of_the_day() -> None:
    with NCM(MISC_NODE_PATH) as node:
        node.ShowTipOfTheDay = False


def disable_collect_usage_information() -> None:
    # This option was disabled started from LO 7.3.0
    # See https://bugs.documentfoundation.org/show_bug.cgi?id=140107
    lo_version = app_version()
    if lo_version.major >= 7 and lo_version.minor >= 3:
        return

    with NCM(MISC_NODE_PATH) as node:
        node.CollectUsageInformation = False


def disable_crash_report() -> None:
    with NCM(MISC_NODE_PATH) as node:
        node.CrashReport = False


def set_colors_of_changes_tracking() -> None:
    with NCM(REVISION_TEXT_DISPLAY_NODE_PATH) as node:
        node.Delete.Color = COLOR_REVISION_TEXT_DISPLAY_DELETE
        node.Insert.Color = COLOR_REVISION_TEXT_DISPLAY_INSERT


def disable_update_check() -> None:
    with NCM(JOBS_UPDATE_CHECK_NODE_PATH) as node:
        node.AutoCheckEnabled = False


buttons = {
    BTN_COLOR_DIGITS: color_digits,
    BTN_SET_FONTS: set_fonts,
    BTN_CHECK_PAIRS: check_pairs,
    BTN_INSERT_ACCENT: insert_accent,
    BTN_DOTTED_UNDERLINE: dotted_underline,
    BTN_SWITCH_TOOLBAR: switch_toolbar,
    BTN_CONFIGURE: configure,
}

implementations = [(button_class_factory(func), ButtonData(name).url,) for name, func in buttons.items()]

g_ImplementationHelper = unohelper.ImplementationHelper()

for imp in implementations:
    g_ImplementationHelper.addImplementation(*imp, ("com.sun.star.task.Job", ), )
