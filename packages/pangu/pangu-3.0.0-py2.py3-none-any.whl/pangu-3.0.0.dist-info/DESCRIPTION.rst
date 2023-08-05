Copyright (c) 2013 Vinta

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Description: pangu.py
        ========
        
        .. image:: https://img.shields.io/travis/vinta/pangu.py/master.svg?style=flat-square
            :target: https://travis-ci.org/vinta/pangu.py
        
        .. image:: https://img.shields.io/codecov/c/github/vinta/pangu.py/master.svg?style=flat-square
            :target: https://codecov.io/github/vinta/pangu.py
        
        .. image:: https://img.shields.io/pypi/v/pangu.svg?style=flat-square
            :target: https://pypi.python.org/pypi/pangu
        
        .. image:: https://img.shields.io/pypi/pyversions/pangu.svg?style=flat-square
            :target: https://pypi.python.org/pypi/pangu
        
        .. image:: https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square
            :target: https://vinta.ws
        
        Paranoid text spacing for good readability, to automatically insert whitespace between CJK (Chinese, Japanese, Korean) and half-width characters (alphabetical letters, numerical digits and symbols).
        
        - `pangu.go <https://github.com/vinta/pangu>`_ (Go)
        - `pangu.java <https://github.com/vinta/pangu.java>`_ (Java)
        - `pangu.js <https://github.com/vinta/pangu.js>`_ (JavaScript, both Node.js and Browser)
        - `pangu.objective-c <https://github.com/Cee/pangu.objective-c>`_ (Objective-C)
        - `pangu.php <https://github.com/Kunr/pangu.php>`_ (PHP)
        - `pangu.py <https://github.com/vinta/pangu.py>`_ (Python)
        - `pangu.rb <https://github.com/dlackty/pangu.rb>`_ (Ruby)
        
        Installation
        ============
        
        .. code-block:: bash
        
            $ pip install pangu
        
        Usage
        =====
        
        .. code-block:: py
        
            import pangu
        
            pangu.spacing('新八的構造成分有95%是眼鏡、3%是水、2%是垃圾')
            # output: u'新八的構造成分有 95% 是眼鏡、3% 是水、2% 是垃圾'
        
            pangu.spacing_text("Mr.龍島主道：「Let's Party!各位高明博雅君子！」")
            # output: u"Mr. 龍島主道：「Let's Party! 各位高明博雅君子！」"
        
        ``spacing_text()`` is an alias of ``spacing()``.
        
        
        History
        =======
        
        3.0.0 (2016-01-24)
        ++++++++++++++++++
        
        - Support Python 3.5
        - Refactoring
        - Rename ``text_spacing()`` to ``spacing_text()``
        
        2.5.6.3 (2015-05-18)
        ++++++++++++++++++++
        
        - Add an alias to ``spacing()``: ``text_spacing()``
        - Fix unicode issue in Python 2.x
        
        2.5.6.2 (2015-05-17)
        ++++++++++++++++++++
        
        - Fix setup.py
        
        2.5.6 (2015-05-17)
        ++++++++++++++++++
        
        - Synchronize version number with `paranoid-auto-spacing <https://github.com/vinta/paranoid-auto-spacing>`_
        - Improve Paranoid Text Spacing algorithm
        
        1.0.0 (2014-02-12)
        ++++++++++++++++++
        
        - Hello World
        
Keywords: pangu space white text spacing readability
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Environment :: Console
Classifier: Environment :: Web Environment
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Natural Language :: Chinese (Traditional)
Classifier: Natural Language :: Chinese (Simplified)
Classifier: Natural Language :: Japanese
Classifier: Natural Language :: Korean
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Programming Language :: Python :: 3.5
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: Topic :: Education
Classifier: Topic :: Software Development :: Internationalization
Classifier: Topic :: Software Development :: Libraries
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Topic :: Text Processing
Classifier: Topic :: Text Processing :: General
Classifier: Topic :: Text Processing :: Linguistic
Classifier: Topic :: Utilities
