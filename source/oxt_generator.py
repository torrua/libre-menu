# -*- coding: utf-8 -*-
import base64
import os
import pathlib
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

import files_content
from config import log
from files_content import DIRECTORY_TEMP_FILES, FOLDER_META_INF, FOLDER_ICONS, \
    DEFAULT_OUTPUT_EXTENSION, EXTENSION_VERSION

from extension.src.pythonpath.core_constants import EXTENSION_NAME


def create_temp_structure(output_directory_path: str = DIRECTORY_TEMP_FILES) -> None:
    """
    param output_directory_path:
    :return:
    """
    os.makedirs(output_directory_path, exist_ok=True)
    os.makedirs(os.path.join(output_directory_path, FOLDER_META_INF), exist_ok=True)
    os.makedirs(os.path.join(output_directory_path, FOLDER_ICONS), exist_ok=True)
    log.info("Create the Temporary directory '%s'", output_directory_path)


def generate_extension() -> None:
    """
    :return:
    """

    log.info("Generate extension")
    create_temp_structure()
    copy_extension_folders()
    create_icon_files()
    create_basic_files()
    create_oxt()
    remove_temp_structure()
    log.info("Complete creating extension")


def create_basic_files(
        output_directory_path: str = DIRECTORY_TEMP_FILES) -> None:
    """
    param output_directory_path:
    :return:
    """
    for file_name, file_content in files_content.files.items():
        if file_name == "manifest.xml":
            file_name = os.path.join(output_directory_path, FOLDER_META_INF, file_name)
        else:
            file_name = os.path.join(output_directory_path, file_name)

        with open(file_name, 'w+', encoding="utf-8") as file:
            file.write(file_content)
        log.info("Create basic file '%s'", file_name)


def generate_base64_from_file(path: str):
    with open(path, "rb") as encoding_file:
        return base64.b64encode(encoding_file.read())


def create_icon_files(output_directory_path: str = DIRECTORY_TEMP_FILES) -> None:
    """
    param output_directory_path:
    :return:
    """

    for icon_name, icon_file in files_content.icons.items():
        icon_path = os.path.join(output_directory_path, FOLDER_ICONS, icon_name)
        with open(icon_path, "wb") as icon:
            icon.write(base64.decodebytes(icon_file))
            log.info("Create icon file '%s'", icon_path)


def copy_extension_folders(temp_directory_path: str = DIRECTORY_TEMP_FILES) -> None:
    """
    param temp_directory_path:
    :return:
    """
    shutil.copytree(DIRECTORY_EXTENSION, temp_directory_path, dirs_exist_ok=True)


def create_oxt():

    os.makedirs(DIRECTORY_PROJECT_BUILDS, exist_ok=True)
    extension_name = f"{EXTENSION_NAME}_{EXTENSION_VERSION}.{DEFAULT_OUTPUT_EXTENSION}"
    output_extension_path = os.path.join(DIRECTORY_PROJECT_BUILDS, extension_name)

    file_paths = []
    for root, _, _files in os.walk(DIRECTORY_TEMP_FILES):
        for filename in _files:
            if root.endswith("__pycache__"):
                continue
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    with ZipFile(output_extension_path, 'w', ZIP_DEFLATED) as oxt:
        for file in file_paths:
            oxt.write(file, file.replace(DIRECTORY_TEMP_FILES, ''))
            log.info("Packing file: %s", os.path.basename(file))

        log.info("Closing archive. DONE")
        oxt.close()


def remove_temp_structure(output_directory_path: str = DIRECTORY_TEMP_FILES) -> None:
    """
    param output_directory_path:
    :return:
    """
    shutil.rmtree(output_directory_path, ignore_errors=True)
    log.info("Remove the Temporary directory '%s'", output_directory_path)


if __name__ == '__main__':
    DIRECTORY_PROJECT_SOURCE = str(pathlib.Path(__file__).parent.absolute())
    DIRECTORY_EXTENSION = os.path.join(DIRECTORY_PROJECT_SOURCE, "extension")
    DIRECTORY_PROJECT = pathlib.Path(DIRECTORY_PROJECT_SOURCE).parent.absolute()
    DIRECTORY_PROJECT_BUILDS = os.path.join(DIRECTORY_PROJECT, "builds")
    generate_extension()
