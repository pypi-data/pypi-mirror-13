from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from smart_settings import Namespace

namespace = Namespace(name='exif', label=_('EXIF'))
setting_exif_backend = namespace.add_setting(
    global_name='EXIF_BACKEND', default='exif.backends.exiftool.EXIFTool',
    help_text=_(
        'Full path to the backend to be used to extract the EXIF data.'
    )
)
