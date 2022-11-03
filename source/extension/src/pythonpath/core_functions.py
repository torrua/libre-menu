# coding: utf-8
"""
Core and Support LibreOffice functions
"""
import inspect
import threading
from os import path
from typing import List, Tuple, NamedTuple
from collections import namedtuple

import uno
from com.sun.star.awt import MessageBoxButtons

from core_constants import URL_WRITER_MODULE, TOOLBAR_BUTTONS_EXECUTIONS


def extension_folder() -> str:
    package_folder = path.dirname(inspect.stack()[0][1])
    return path.abspath(path.join(package_folder, "..\\"))


def get_context():
    return uno.getComponentContext()


def mri(target):
    ctx = get_context()
    mri = ctx.ServiceManager.createInstanceWithContext(
        "mytools.Mri", ctx)
    mri.inspect(target)


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
    context = get_context()
    return context.getServiceManager()


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


def is_menu_buttons_on_toolbar() -> bool:
    standard_bar = "private:resource/toolbar/standardbar"
    module_configuration_manager = get_ui_configuration_manager(URL_WRITER_MODULE)
    toolbar_settings = module_configuration_manager.getSettings(standard_bar, True)
    count = toolbar_settings.getCount()

    for i in range(count):
        for prop in toolbar_settings.getByIndex(i):
            if prop.Name == "CommandURL" and prop.Value in TOOLBAR_BUTTONS_EXECUTIONS:
                return True
    return False


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


def add_menu_buttons(buttons_to_add: List[Tuple]):
    with ModuleConfigurationManager() as manager:
        for button_setting in buttons_to_add:
            manager.insert_by_index(button_setting)


def remove_menu_buttons():
    with ModuleConfigurationManager() as manager:
        for i in reversed(range(manager.count)):
            button_settings = manager.toolbar_settings.getByIndex(i)
            for prop in button_settings:
                if prop.Value in TOOLBAR_BUTTONS_EXECUTIONS:
                    manager.remove_by_index(i)


def run_in_thread(fn):
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run
