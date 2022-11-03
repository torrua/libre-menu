# coding: utf-8
from __future__ import annotations

from dataclasses import dataclass

EXTENSION_NAME = "lomenu"
EXTENSION_VERSION = "0.0.1"
EXTENSION_AUTHOR = "torrua"
EXTENSION_ID = f"org.{EXTENSION_AUTHOR}.extensions.{EXTENSION_NAME}"
EXTENSION_TITLE = f"{EXTENSION_AUTHOR}'s features for LibreOffice"
FOLDER_ICONS = "icons"

DEFAULT_FONT = "Arial"
SPECIAL_FONT = "Noto Sans"

DEFAULT_FORMAT_WRITER_VALUE = "MS Word 2007 XML"
DEFAULT_FORMAT_CALC_VALUE = "Calc MS Excel 2007 XML"

DEFAULT_CHECKER_AUTHOR = "Pair Checker"
CHECKER_PAIRS_TO_CHECK = [("«", "»",), ("„", "“",), ("‚", "‘",), ("(", ")",), ("[", "]",), ("{", "}",), ]
CHECKER_ESCAPED_CHARACTERS = ['(', ')', '[', ']', '{', '}', ]

DEFAULT_COLOR = -1
COLOR_DECIMAL_RED = 12582912
COLOR_DECIMAL_BLUE = 28864

COLOR_REVISION_TEXT_DISPLAY_DELETE = 16711680
COLOR_REVISION_TEXT_DISPLAY_CHANGED_ATTRIBUTE = 2777241
COLOR_REVISION_TEXT_DISPLAY_INSERT = 43315

SYS_CHAR_ACCENT = 769

LANGUAGE_RU = "RU"
LANGUAGE_EN = "EN"
DEFAULT_UI_LANGUAGE = LANGUAGE_RU

# =========================== URL DATA =================================

BTN_RESET_ATTRIBUTES = "ResetAttributes"
URL_RESET_ATTRIBUTES = f".uno:{BTN_RESET_ATTRIBUTES}"

URL_WRITER_MODULE = "com.sun.star.text.TextDocument"
ANNOTATION_UNIT = "com.sun.star.text.textfield.Annotation"
DEFAULT_FONT_NODE_PATH = "/org.openoffice.Office.Writer/DefaultFont"
DEFAULT_FORMAT_WRITER_NODE_PATH = "/org.openoffice.Setup/Office/Factories/org.openoffice.Setup:Factory['com.sun.star.text.TextDocument']"
DEFAULT_FORMAT_CALC_NODE_PATH = "/org.openoffice.Setup/Office/Factories/org.openoffice.Setup:Factory['com.sun.star.sheet.SpreadsheetDocument']"

MISC_NODE_PATH = "/org.openoffice.Office.Common/Misc"
REVISION_TEXT_DISPLAY_NODE_PATH = "/org.openoffice.Office.Writer/Revision/TextDisplay/"
JOBS_UPDATE_CHECK_NODE_PATH = "/org.openoffice.Office.Jobs/Jobs/org.openoffice.Office.Jobs:Job['UpdateCheck']/Arguments"


# https://www.openoffice.org/api/docs/common/ref/com/sun/star/awt/Key.html
class Key:
    CTRL = 2
    ALT = 4
    ZERO = 256
    SIX = 262
    SEVEN = 263
    EIGHT = 264
    NINE = 265
    A = 512
    B = 513
    D = 515
    SPACE = 1284
    ENTER = 1280

# =========================== BUTTON DATA =================================


BTN_DOTTED_UNDERLINE = "BTN_DOTTED_UNDERLINE"
BTN_SET_FONTS = "BTN_SET_FONTS"
BTN_COLOR_DIGITS = "BTN_COLOR_DIGITS"
BTN_SWITCH_TOOLBAR = "BTN_SWITCH_TOOLBAR"
BTN_CONFIGURE = "BTN_CONFIGURE"
BTN_CHECK_PAIRS = "BTN_CHECK_PAIRS"
BTN_INSERT_ACCENT = "BTN_INSERT_ACCENT"

UI_ELEMENT_LABELS = {
    LANGUAGE_RU: {
        BTN_INSERT_ACCENT:          "Вставить ударение",
        BTN_DOTTED_UNDERLINE:       "Подчеркнуть пунктиром",
        BTN_SET_FONTS:              "Задать шрифты",
        BTN_COLOR_DIGITS:           "Покрасить цифры",
        BTN_CHECK_PAIRS:            "Проверить парные символы",
        BTN_SWITCH_TOOLBAR:         "Показать/скрыть кнопки",
        BTN_CONFIGURE:              "Применить настройки",
    },
    LANGUAGE_EN: {
        BTN_INSERT_ACCENT:          "Insert Accent",
        BTN_DOTTED_UNDERLINE:       "Dotted Underline",
        BTN_SET_FONTS:              "Set Fonts",
        BTN_COLOR_DIGITS:           "Color digits",
        BTN_CHECK_PAIRS:            "Check paired symbols",
        BTN_SWITCH_TOOLBAR:         "Show/Hide Buttons",
        BTN_CONFIGURE:              "Configure",
    },
}

@dataclass
class ButtonData:
    name: str

    @property
    def url(self) -> str:
        return f'{EXTENSION_ID}.{self.name}'

    @property
    def execute(self) -> str:
        return f"service:{self.url}?execute"

    @property
    def image_node(self) -> str:
        return f"""
      <node oor:name="{self.url}" oor:op="replace">
        <prop oor:name="URL">
          <value>{self.execute}</value>
        </prop>
        <node oor:name="UserDefinedImages">
          <prop oor:name="ImageSmallURL" oor:type="xs:string">
            <value>%origin%/{FOLDER_ICONS}/{self.name}.png</value>
          </prop>
          <prop oor:name="ImageBigURL" oor:type="xs:string">
            <value>%origin%/{FOLDER_ICONS}/{self.name}.png</value>
          </prop>
        </node>
      </node>
"""

    def menu_node(self, number:  int) -> str:
        return f"""
          <!-- {self.name} -->
          <node oor:name="N{number:03d}" oor:op="replace">
            <prop oor:name="URL" oor:type="xs:string">
              <value>{self.execute}</value>
            </prop>

            <prop oor:name="Title" oor:type="xs:string">
              <value/>
              <value xml:lang="en-US">{self.label_text(LANGUAGE_EN)}</value>
              <value xml:lang="ru-RU">{self.label_text(LANGUAGE_RU)}</value>
            </prop>

            <prop oor:name="Target" oor:type="xs:string">
              <value>_self</value>
            </prop>

            <prop oor:name="Context" oor:type="xs:string">
              <value>{URL_WRITER_MODULE}</value>
            </prop>
          </node>
"""

    def label_text(self, language: str) -> str:
        return UI_ELEMENT_LABELS.get(language).get(self.name)

    @staticmethod
    def generate_images_nodes(button_names: list) -> str:
        return "".join([ButtonData(name).image_node for name in button_names])

    @staticmethod
    def generate_submenu_nodes(button_names: list) -> str:
        return "".join([ButtonData(name).menu_node(index) for index, name in enumerate(button_names, 1)])


BUTTONS_NAMES = list(UI_ELEMENT_LABELS.get(DEFAULT_UI_LANGUAGE).keys())
TOOLBAR_BUTTONS_NAMES = [BTN for BTN in BUTTONS_NAMES if BTN not in (BTN_CONFIGURE, BTN_SWITCH_TOOLBAR)]
TOOLBAR_BUTTONS_EXECUTIONS = [ButtonData(NAME).execute for NAME in TOOLBAR_BUTTONS_NAMES]
