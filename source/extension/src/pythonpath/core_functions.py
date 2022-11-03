# coding: utf-8
"""
Core and Support LibreOffice functions
"""
import threading
import time
from typing import Tuple, NamedTuple
from collections import namedtuple

import uno
from com.sun.star.awt import MessageBoxButtons

from core_constants import URL_WRITER_MODULE


def get_context():
    return uno.getComponentContext()


def app_version() -> NamedTuple:
    AppVersion = namedtuple('AppVersion', ['major', 'minor', "patch"])

    sm = uno.getComponentContext().ServiceManager
    service = sm.createInstanceWithContext(
        "com.sun.star.configuration.ConfigurationProvider",
        uno.getComponentContext())

    pv = {"nodepath": "/org.openoffice.Setup/Product", }
    settings = service.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationAccess", structify(pv))
    version_info = settings.getByName("ooSetupVersionAboutBox").split(".")
    version_values = list(map(int, version_info[:3]))
    return AppVersion(*version_values)


def get_service_manager():
    cxt = get_context()
    return cxt.getServiceManager()


def get_desktop():
    sm = get_service_manager()
    return sm.createInstanceWithContext(
        "com.sun.star.frame.Desktop", get_context())


def get_open_documents():
    """Returns currently open documents of type doctype."""
    open_documents = []

    oComponents = get_desktop().getComponents()
    oDocs = oComponents.createEnumeration()

    while oDocs.hasMoreElements():
        oDoc = oDocs.nextElement()
        if oDoc.supportsService("com.sun.star.text.TextDocument"):
            open_documents.append(oDoc)

    return open_documents


def get_current_document():
    sm = get_service_manager()
    return sm.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        get_context()).getCurrentComponent()


def create_instance(name, with_context=False):
    sm = get_service_manager()
    return sm.createInstanceWithContext(name, get_context()) \
        if with_context else sm.createInstance(name)


def msgbox(message, title='LibreOffice', buttons=MessageBoxButtons.BUTTONS_OK, type_msg='infobox'):
    """ Create message box
        type_msg: infobox, warningbox, errorbox, querybox, messbox
        https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1awt_1_1XMessageBoxFactory.html
    """
    toolkit = create_instance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    mb = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return mb.execute()


def warning_box(message):
    msgbox(message, type_msg='warningbox')


def error_box(message):
    msgbox(message, type_msg='errorbox')


def structify(key_pairs) -> Tuple:
    result = []
    for key, value in key_pairs.items():
        struct = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
        struct.Name = key
        struct.Value = value
        result.append(struct)
    return tuple(result)


def call_dispatch(doc, url, args=()):
    frame = doc.getCurrentController().getFrame()
    dispatch = create_instance('com.sun.star.frame.DispatchHelper')
    dispatch.executeDispatch(frame, url, '', 0, args)


def get_selection():
    doc = get_current_document()
    view_cursor = doc.getCurrentController().getViewCursor()
    selection = view_cursor.getText().createTextCursorByRange(view_cursor)
    return selection


def get_text():
    return get_current_document().Text


def get_left_cursor():
    text = get_text()
    cursor = text.createTextCursorByRange(text.getStart())
    return cursor


def get_right_cursor():
    text = get_text()
    cursor = text.createTextCursorByRange(text.getEnd())
    return cursor


def insert_string(string, attrs: dict = None):
    attrs = dict() if not attrs else attrs

    selection = get_selection()
    if selection.getString():
        selection.setPropertyValues(tuple(attrs.keys()), tuple(attrs.values()))
        selection.setString(string)
        return

    controller = get_current_document().CurrentController
    whole_text = get_text()
    cursor = whole_text.createTextCursor()
    cursor.gotoRange(controller.ViewCursor.End, False)
    cursor.setPropertyValues(tuple(attrs.keys()), tuple(attrs.values()))
    cursor.setString(string)


def get_ui_configuration_manager_supplier():
    manager = get_context().getByName(
        "/singletons/com.sun.star.ui.theModuleUIConfigurationManagerSupplier")
    return manager


def get_ui_configuration_manager(module):
    ui_conf_man_sup = get_ui_configuration_manager_supplier()
    manager = ui_conf_man_sup.getUIConfigurationManager(module)
    return manager


def get_configuration_provider():
    return create_instance(
        "com.sun.star.configuration.ConfigurationProvider", True)


def get_node_configuration(node_path):
    args = {
        "nodepath": node_path
    }

    provider = get_configuration_provider()
    configuration = provider.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationUpdateAccess", structify(args))
    return configuration


def set_key_for_command(key, command, remove=False):
    module_manager = create_instance("com.sun.star.frame.ModuleManager")
    list_modules = list(module_manager.getElementNames())

    for module in list_modules:
        ui_configuration_manager = get_ui_configuration_manager(module)
        shortcut_manager = ui_configuration_manager.getShortCutManager()
        if not remove:
            shortcut_manager.setKeyEvent(key, command)
        else:
            shortcut_manager.removeCommandFromAllKeyEvents(key, command)
        # NOTE: Don't remove this or our key will not save!!
        shortcut_manager.store()


def get_document_language():
    selection = get_selection()
    return selection.CharLocale.Language


def get_ui_language():
    lo_lang_node_path = "/org.openoffice.Setup/L10N"
    configuration = get_node_configuration(lo_lang_node_path)
    return configuration.ooLocale[0:2]


class NodeConfigurationManager:
    def __init__(self, node_path):
        self.node_path = node_path
        self.node = get_node_configuration(node_path)

    def __enter__(self):
        return self.node

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.node.commitChanges()


class ModuleConfigurationManager:
    def __init__(self):
        self.standard_bar = "private:resource/toolbar/standardbar"
        self.module_configuration_manager = get_ui_configuration_manager(URL_WRITER_MODULE)
        self.toolbar_settings = self.module_configuration_manager.getSettings(self.standard_bar, True)
        self.count = self.toolbar_settings.getCount()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.module_configuration_manager.replaceSettings(self.standard_bar, self.toolbar_settings)
        # NOTE: Don't remove this or our button will not save after restart!!
        self.module_configuration_manager.store()

    def invoke(self, index, method_name, arg_tuple):
        uno.invoke(
            self.toolbar_settings, method_name,
            (index, uno.Any("[]com.sun.star.beans.PropertyValue", arg_tuple))
        )

    def insert_by_index(self, button):
        self.invoke(self.count, "insertByIndex", button)

    def replace_by_index(self, index, button):
        self.invoke(index, "replaceByIndex", button)

    def remove_by_index(self, index):
        uno.invoke(self.toolbar_settings, "removeByIndex", (index, ))


def run_in_thread(fn):
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run


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


def create_annotation(author: str = "author", content: str = ""):
    def get_current_time():
        t = time.localtime()
        dtv = uno.createUnoStruct("com.sun.star.util.DateTime")
        dtv.Year = t.tm_year
        dtv.Month = t.tm_mon
        dtv.Day = t.tm_mday
        dtv.Hours = t.tm_hour
        dtv.Minutes = t.tm_min
        dtv.Seconds = t.tm_sec
        dtv.NanoSeconds = 0
        return dtv

    anno = get_current_document().createInstance("com.sun.star.text.textfield.Annotation")
    anno.Content = content
    anno.Author = author
    anno.DateTimeValue = get_current_time()
    return anno
