Copyright (c) 2015 Roberto Rosario

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: Description
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
        
        
        
        
        1.0.0 (2015-12-22)
        ==================
        
        - Initial release
        
Platform: any
Classifier: Development Status :: 5 - Production/Stable
Classifier: Environment :: Web Environment
Classifier: Framework :: Django
Classifier: Intended Audience :: End Users/Desktop
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Operating System :: POSIX
Classifier: Programming Language :: Python
