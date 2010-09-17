# -*- coding: utf-8 -*-
#flac.py

#Copyright (C) 2008-2009 concentricpuddle

#This audio is part of puddletag, a semi-good music tag editor.

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from mutagen.flac import FLAC, Picture
import util
from util import (strlength, strbitrate, strfrequency, IMAGETYPES, usertags,
    getfilename, getinfo, FILENAME, PATH, INFOTAGS, str_filesize)
import ogg, pdb

PICARGS = ('type', 'mime', 'desc', 'width', 'height', 'depth', 'data')
ATTRIBUTES = ('frequency', 'bitrate', 'length', 'accessed', 'size', 'created',
              'modified', 'bitspersample')

try:
    from puddlestuff.image import imageproperties
    IMAGETAGS = (util.MIMETYPE, util.DESCRIPTION, util.DATA,
                    util.IMAGETYPE)
except ImportError:
    IMAGETAGS = None


class TempTag(ogg.Tag):
    """Flac Tag Class.

    Behaves like Tag class in ogg.py"""
    IMAGETAGS = ()
    mapping = {}
    revmapping = {}

    def __init__(self,filename=None):
        """Links the audio"""
        self.images = None
        if filename is not None:
            self.link(filename)
    
    def _info(self):
        info = self._mutfile.info
        fileinfo = [('Path', self.filepath),
                    ('Size', str_filesize(int(self.size))),
                    ('Filename', self.filename),
                    ('Modified', self.modified)]

        ogginfo = [('Bitrate', 'Lossless'),
                ('Frequency', self.frequency),
                ('Bits Per Sample', self.bitspersample),
                ('Channels', unicode(info.channels)),
                ('Length', self.length)]
        return [('File', fileinfo), ('FLAC Info', ogginfo)]

    info = property(_info)

    def delete(self):
        self.images = []
        ogg.Tag.delete(self)

    def link(self, filename):
        """Links the audio, filename
        returns self if successful, None otherwise."""
        tags, audio = self._init_info(filename, FLAC)

        if audio is None:
            return

        for z in audio:
            self._tags[z.lower()] = audio.tags[z]

        self._images = audio.pictures

        info = audio.info
        self._tags.update({u"__frequency": strfrequency(info.sample_rate),
                    u"__length": strlength(info.length),
                    u'__bitspersample': unicode(info.bits_per_sample)})
        try:
            self._tags[u"__bitrate"] = strbitrate(info.bitrate)
        except AttributeError:
            self._tags[u"__bitrate"] = u'0 kb/s'

        self._tags.update(tags)
        self._set_attrs(ATTRIBUTES)
        self._mutfile = audio
        self.filetype = 'FLAC'
        self._tags['__filetype'] = self.filetype
        return self

if IMAGETAGS:
    class Tag(TempTag):
        IMAGETAGS = IMAGETAGS
        def _picture(self, image):
            try:
                data = image[util.DATA]
            except:
                import pdb
                pdb.set_trace()
                data = image[util.DATA]
            description = image.get(util.DESCRIPTION)
            if not description:
                description = u''
            mime = image.get(util.MIMETYPE)
            imagetype = image.get(util.IMAGETYPE, 3)
            props = imageproperties(data = data)
            props['type'] = imagetype
            props['desc'] = description
            props['width'], props['height'] = props['size']
            args = dict([(z, props[z]) for z in PICARGS])
            p = Picture()
            [setattr(p, z, props[z]) for z in PICARGS]
            return p

        def _getImages(self):
            if self._images:
                return [{'data': image.data, 'description': image.desc,
                            'mime': image.mime, 'imagetype': image.type}
                            for image in self._images]
            return []

        def _setImages(self, images):
            if images:
                self._images = map(self._picture, images)
            else:
                self._images = []

        def __getitem__(self, key):
            if key == '__image':
                return self.images

            return TempTag.__getitem__(self, key)

        def __setitem__(self, key, value):
            if key == '__image':
                self.images = value
                return
            TempTag.__setitem__(self, key, value)

        images = property(_getImages, _setImages)

        def save(self):
            """Writes the tags in self._tags
            to self.filename if no filename is specified."""
            if self._mutfile.tags is None:
                self._mutfile.add_tags()
            if self.filepath != self._mutfile.filename:
                self._mutfile.filename = self.filepath
            audio = self._mutfile

            newtag = {}
            for tag, value in usertags(self._tags).items():
                newtag[tag] = value
            toremove = [z for z in audio if z not in newtag]
            for z in toremove:
                del(audio[z])
            audio.clear_pictures()
            [audio.add_picture(z) for z in self._images]
            audio.update(newtag)
            audio.save()
else:
    Tag = TempTag

filetype = (FLAC, Tag, 'VorbisComment')