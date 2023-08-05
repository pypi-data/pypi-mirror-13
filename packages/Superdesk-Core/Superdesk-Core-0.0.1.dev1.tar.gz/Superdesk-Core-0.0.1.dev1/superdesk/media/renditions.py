# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from __future__ import absolute_import
from PIL import Image
from io import BytesIO
import logging
from flask import current_app as app
from .media_operations import process_file_from_stream

logger = logging.getLogger(__name__)


def generate_renditions(original, media_id, inserted, file_type, content_type,
                        rendition_config, url_for_media, insert_metadata=True):
    """
    Generate system renditions for given media file id.
    :param BytesIO original: original image byte stream
    :param str media_id: media id
    :param list inserted: list of media ids inserted
    :param str file_type: file_type
    :param str content_type: content type
    :param dict rendition_config: rendition config
    :param url_for_media: function to generate url
    :param bool insert_metadata: boolean to inserted metadata or not. For AWS storage it is false.
    :return: dict of renditions
    """
    rend = {'href': url_for_media(media_id), 'media': media_id, 'mimetype': content_type}
    renditions = {'original': rend}

    if file_type != 'image':
        return renditions

    original.seek(0)
    img = Image.open(original)
    width, height = img.size
    rend.update({'width': width})
    rend.update({'height': height})

    ext = content_type.split('/')[1].lower()
    if ext in ('JPG', 'jpg'):
        ext = 'jpeg'
    ext = ext if ext in ('jpeg', 'gif', 'tiff', 'png') else 'png'
    for rendition, rsize in rendition_config.items():
        size = (rsize['width'], rsize['height'])
        original.seek(0)
        resized, width, height = resize_image(original, ext, size)
        rend_content_type = 'image/%s' % ext
        file_name, rend_content_type, metadata = process_file_from_stream(resized, content_type=rend_content_type)
        resized.seek(0)
        _id = app.media.put(resized, filename=file_name,
                            content_type=rend_content_type,
                            metadata=metadata if insert_metadata else None)
        inserted.append(_id)
        renditions[rendition] = {'href': url_for_media(_id), 'media': _id,
                                 'mimetype': 'image/%s' % ext, 'width': width, 'height': height}
    return renditions


def delete_file_on_error(doc, file_id):
    # Don't delete the file if we are on the import from storage flow
    if doc.get('_import', None):
        return
    app.media.delete(file_id)


def resize_image(content, format, size, keepProportions=True):
    '''
    Resize the image given as a binary stream

    @param content: stream
        The binary stream containing the image
    @param format: str
        The format of the resized image (e.g. png, jpg etc.)
    @param size: tuple
        A tuple of width, height
    @param keepProportions: boolean
        If true keep image proportions; it will adjust the resized
        image size.
    @return: stream
        Returns the resized image as a binary stream.
    '''
    assert isinstance(size, tuple)
    img = Image.open(content)
    if keepProportions:
        width, height = img.size
        new_width, new_height = size
        x_ratio = width / new_width
        y_ratio = height / new_height
        if x_ratio > y_ratio:
            new_height = int(height / x_ratio)
        else:
            new_width = int(width / y_ratio)
        size = (new_width, new_height)

    resized = img.resize(size, Image.ANTIALIAS)
    out = BytesIO()
    resized.save(out, format, quality=85)
    out.seek(0)
    return out, new_width, new_height
