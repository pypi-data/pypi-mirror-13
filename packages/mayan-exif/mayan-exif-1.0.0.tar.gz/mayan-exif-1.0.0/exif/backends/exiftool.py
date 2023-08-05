from __future__ import unicode_literals

import json
import logging
import tempfile

import sh

from common.utils import fs_cleanup

from .literals import EXIFTOOL_PATH

try:
    exiftool = sh.Command(EXIFTOOL_PATH)
except sh.CommandNotFound:
    exiftool = None
else:
    exiftool = exiftool.bake('-j')

logger = logging.getLogger(__name__)


class EXIFTool(object):
    def execute(self, document_version):
        new_file_object, temp_filename = tempfile.mkstemp()

        try:
            document_version.save_to_file(filepath=temp_filename)
            result = exiftool(temp_filename)
            return json.loads(result.stdout)[0]
        finally:
            fs_cleanup(filename=temp_filename)
