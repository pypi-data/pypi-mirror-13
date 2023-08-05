import os
import logging
from parrot.utils import traceback_in_one_line
from parrot.exceptions import SerializerLoaderFromUrlException


logger = logging.getLogger(__name__)


def load(source, loader, destination_dir, name_function, new_url_function):
    """
    Загружает файл по указанному source и сохраняет его в папке
    destination_dir под именем, возвращенным функцией name_function, которая
    принимает только один аргумент - source. Результатом выполнения является
    значение, возвращаемое функцией new_url_function, которая принимает только
    один аргумент - имя, под которым сохраняется загруженный файл.

    :param source:
    :param loader:
    :param destination_dir:
    :param name_function:
    :param new_url_function:
    :return:
    """
    filename = name_function(source)
    filepath = os.path.join(destination_dir, filename)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    try:
        file_data = loader(source)
        if file_data is None:
            return None
        with open(filepath, 'wb') as file_handler:
            file_handler.write(file_data)
    except Exception as exc:
        exc = SerializerLoaderFromUrlException(
            source, exc, traceback_in_one_line()
        )
        logger.warning(exc)
        return None
    else:
        return new_url_function(filename)
