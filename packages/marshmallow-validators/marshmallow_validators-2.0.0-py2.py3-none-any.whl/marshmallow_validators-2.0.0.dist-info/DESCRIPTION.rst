Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Description: **********************
        marshmallow-validators
        **********************
        
        .. image:: https://img.shields.io/pypi/v/marshmallow-validators.svg
            :target: https://pypi.python.org/pypi/marshmallow-validators
            :alt: Latest version
        
        .. image:: https://img.shields.io/travis/marshmallow-code/marshmallow-validators/pypi.svg
            :target: https://travis-ci.org/marshmallow-code/marshmallow-validators
            :alt: Travis-CI
        
        Homepage: http://marshmallow-validators.rtfd.org/
        
        Use 3rd-party validators (e.g. from WTForms and colander) with marshmallow.
        
        .. code-block:: python
        
            from marshmallow import Schema, fields
            from marshmallow_validators.wtforms import from_wtforms
            from wtforms.validators import Email, Length
        
            # Leverage WTForms il8n
            locales = ['de_DE', 'de']
        
            class UserSchema(Schema):
                email = fields.Str(
                    validate=from_wtforms([Email()], locales=locales)
                )
                password = fields.Str(
                    validate=from_wtforms([Length(min=8, max=300)], locales=locales)
                )
        
            UserSchema().validate({'email': 'invalid', 'password': 'abc'})
            # {'email': ['Ungültige Email-Adresse.'],
            # 'password': ['Feld muss zwischen 8 und 300 Zeichen beinhalten.']}
        
        Get It Now
        ==========
        
        ::
        
            $ pip install -U marshmallow-validators
        
        
        Documentation
        =============
        
        Full documentation is available at http://marshmallow-validators.rtfd.org/ .
        
        Project Links
        =============
        
        - Docs: http://marshmallow-validators.rtfd.org/
        - Changelog: http://marshmallow-validators.readthedocs.org/en/latest/changelog.html
        - PyPI: https://pypi.python.org/pypi/marshmallow-validators
        - Issues: https://github.com/marshmallow-code/marshmallow-validators/issues
        
        License
        =======
        
        MIT licensed. See the bundled `LICENSE <https://github.com/marshmallow-code/marshmallow-validators/blob/pypi/LICENSE>`_ file for more details.
        
Keywords: validators marshmallow
Platform: UNKNOWN
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
