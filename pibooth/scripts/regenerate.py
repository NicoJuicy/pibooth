# -*- coding: utf-8 -*-

"""Pibooth picture regeneration module.
"""

import os
import argparse
from os import path as osp
from datetime import datetime

from PIL import Image

from pibooth.utils import LOGGER, configure_logging
from pibooth.plugins import create_plugin_manager
from pibooth.config import PiConfigParser
from pibooth.pictures import get_picture_factory
from pibooth.counters import Counters


def get_captures(images_folder):
    """Get a list of images from the folder given in input.
    """
    captures_paths = os.listdir(images_folder)
    captures = []
    for capture_path in captures_paths:
        try:
            image = Image.open(osp.join(images_folder, capture_path))
            captures.append(image)
        except OSError:
            LOGGER.info("File %s doesn't seem to be an image", capture_path)
    return captures


def regenerate_all_images(plugin_manager, config, basepath):
    """Regenerate the pibboth images from the raw images and the config.
    """
    if not osp.isdir(osp.join(basepath, 'raw')):
        return

    capture_choices = config.gettuple('PICTURE', 'captures', int, 2)

    for captures_folder in os.listdir(osp.join(basepath, 'raw')):
        captures_folder_path = osp.join(basepath, 'raw', captures_folder)
        if not osp.isdir(captures_folder_path):
            continue
        captures = get_captures(captures_folder_path)
        LOGGER.info("Generating image from raws in folder %s", captures_folder_path)

        if len(captures) == capture_choices[0]:
            idx = 0
        elif len(captures) == capture_choices[1]:
            idx = 1
        else:
            LOGGER.warning("Folder %s doesn't contain the correct number of pictures", captures_folder_path)
            continue

        default_factory = get_picture_factory(captures, config.get('PICTURE', 'orientation'))
        factory = plugin_manager.hook.pibooth_setup_picture_factory(cfg=config,
                                                                    opt_index=idx,
                                                                    factory=default_factory)

        picture_file = osp.join(basepath, captures_folder + "_pibooth.jpg")
        factory.save(picture_file)


def main():
    """Application entry point.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description="This script lets you regenerate the final pictures from the original captures present in the raw directory.")

    parser.add_argument("config_directory", nargs='?', default="~/.config/pibooth",
                        help=u"path to configuration directory (default: %(default)s)")

    options = parser.parse_args()

    configure_logging()
    plugin_manager = create_plugin_manager()
    config = PiConfigParser(osp.join(options.config_directory, "pibooth.cfg"), plugin_manager)

    # Register plugins
    plugin_manager.load_all_plugins(config.gettuple('GENERAL', 'plugins', 'path'),
                                    config.gettuple('GENERAL', 'plugins_disabled', str))

    LOGGER.info("Installed plugins: %s", ", ".join(
        [plugin_manager.get_friendly_name(p) for p in plugin_manager.list_external_plugins()]))

    # Update configuration with plugins ones
    plugin_manager.hook.pibooth_configure(cfg=config)

    # Initialize varibales normally done by the app
    picture_plugin = plugin_manager.get_plugin('pibooth-core:picture')
    picture_plugin.texts_vars['date'] = datetime.now()
    picture_plugin.texts_vars['count'] = Counters(config.join_path("counters.pickle"), taken=0, printed=0, forgotten=0,
                                                  remaining_duplicates=config.getint('PRINTER', 'max_duplicates'))

    for path in config.gettuple('GENERAL', 'directory', 'path'):
        regenerate_all_images(plugin_manager, config, path)


if __name__ == "__main__":
    main()
