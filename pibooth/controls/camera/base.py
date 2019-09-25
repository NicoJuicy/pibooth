# -*- coding: utf-8 -*-

import pygame
from PIL import Image, ImageDraw
from pibooth import fonts
from pibooth.pictures import sizing


LANGUAGES = {
    'fr': {
        'smile_message': "Souriez !"
    },
    'en': {
        'smile_message': "Smile !"
    },
    'de': {
        'smile_message': "Bitte lächeln !"
    }
}


class BaseCamera(object):

    def __init__(self, resolution, delete_internal_memory):
        self._cam = None
        self._border = 50
        self._window = None
        self._overlay = None
        self._captures = {}
        self.resolution = resolution
        self.delete_internal_memory = delete_internal_memory

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        self._overlay = text

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay is not None:
            self._overlay = None

    def _post_process_capture(self, capture_path):
        """Rework and return a Image object from file.
        """
        return Image.open(capture_path)

    def get_rect(self):
        """Return a Rect object (as defined in pygame) for resizing preview and images
        in order to fit to the defined window.
        """
        rect = self._window.get_rect()
        res = sizing.new_size_keep_aspect_ratio(self.resolution,
                                                (rect.width - 2 * self._border, rect.height - 2 * self._border))
        return pygame.Rect(rect.centerx - res[0] // 2, rect.centery - res[1] // 2, res[0], res[1])

    def build_overlay(self, size, text, alpha):
        """Return a PIL image with the given text that can be used
        as an overlay for the camera.
        """
        image = Image.new('RGBA', size)
        draw = ImageDraw.Draw(image)

        font = fonts.get_pil_font(text, fonts.get_filename("Amatic-Bold"), size[0], size[1])
        txt_width, txt_height = draw.textsize(text, font=font)

        position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
        draw.text(position, text, (255, 255, 255, alpha), font=font)
        return image

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        raise NotImplementedError

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        raise NotImplementedError

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time and let doing the job.
        Returns when the timeout is reached.
        """
        raise NotImplementedError

    def stop_preview(self):
        """Stop the preview.
        """
        raise NotImplementedError

    def capture(self, filename, effect=None):
        """Capture a new picture.
        """
        raise NotImplementedError

    def get_captures(self):
        """Return all buffered captures as PIL images (buffer dropped after call).
        """
        images = []
        for path in sorted(self._captures):
            images.append(self._post_process_capture(path))
        self.drop_captures()
        return images

    def drop_captures(self):
        """Delete all buffered captures.
        """
        self._captures.clear()

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        raise NotImplementedError
