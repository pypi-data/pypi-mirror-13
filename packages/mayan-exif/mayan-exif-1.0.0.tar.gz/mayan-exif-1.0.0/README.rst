Description
-----------
Mayan EDMS app that extract image documents' EXIF data.

License
-------
This project is open sourced under the `MIT License`_.

.. _`MIT License`: https://gitlab.com/mayan-edms/versionlifespan/raw/master/LICENSE


Installation
------------
Clone repository in a directory outside of Mayan EDMS::

    git clone https://gitlab.com/mayan-edms/exif.git

Symlink the app into your Mayan EDMS' app folder::

    ln -s <repository directory>/exif/ <Mayan EDMS directory>/mayan/apps

In your settings/local.py file add `exif` to your `INSTALLED_APPS` list::

    INSTALLED_APPS += (
        'exif',
    )

Run the migrations for the app::

    ./manage.py migrate

Settings
--------
**EXIF_BACKEND**: Specifies the backend used to extract the EXIF data, default: exif.backends.exiftool.EXIFTool

Requirements
------------
**ExifTool** http://www.sno.phy.queensu.ca/~phil/exiftool/

Usage
-----
EXIF data is extracted automatically upon initial document upload or version uploads. The EXIF data is available via the
.exif_value_of. accessor of the document version model. Example: {{ document.exif_value_of.FileType }} or {{ document.latest_version.exif_value_of.FileType }} returns the 'PNG' string for PNG image files. This accessor can be used anywhere template expressions are used: indexing, smart links, etc.

Development
-----------
EXIF Backends are just a class with a single method called `execute` which receives a document
version instance and returns a dictionary of EXIF tags with their corresponding values. The default backend
calls `exiftool` using the JSON parameter and then turn that JSON result into a Python dictionary::

    class EXIFTool(object):
        def execute(self, document_version):
            new_file_object, temp_filename = tempfile.mkstemp()

            try:
                document_version.save_to_file(filepath=temp_filename)
                result = exiftool(temp_filename)
                return json.loads(result.stdout)[0]
            finally:
                fs_cleanup(filename=temp_filename)


