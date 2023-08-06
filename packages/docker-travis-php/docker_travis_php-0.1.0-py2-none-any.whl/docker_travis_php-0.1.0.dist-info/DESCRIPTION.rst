Copyright (c) 2015 Jose Diaz-Gonzalez

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

Description: =================
        docker-travis-php
        =================
        
        Shits out a simple dockerfile for php projects based upon a .travis.yml
        
        Literally don't use this and assume it'll work. It probably won't. Hence the description.
        
        Literally the worst. I can't even.
        
        Installation
        ============
        
        Using PIP via PyPI::
        
            pip install docker-travis-php
        
        Using PIP via Github::
        
            pip install git+git://github.com/josegonzalez/docker-travis-php.git#egg=docker-travis-php
        
        Usage
        =====
        
        In a directory with a ``.travis.yml``, run the following:
        
        .. code:: bash
        
            docker-travis-php
        
        You will now have a ``Dockerfile`` in that directory that can be run via the following command:
        
        .. code:: bash
        
            # builds the ``before_script`` and ``script`` sections
            # useful for "local" travis runs
            docker build .
        
        The default debian packages that are installed (before php extensions) are as follows:
        
        - ``git-core``
        - ``libcurl4-openssl-dev``
        - ``libicu-dev``
        - ``php-pear``
        - ``php5-cli``
        
        You can add more by using the following environment variable:
        
        .. code:: bash
        
            export PACKAGES=wget
            docker-travis-php
        
        By default, the following extensions are built:
        
        - ``curl``
        - ``intl``
        - ``mbstring``
        - ``mysql``
        - ``redis``
        - ``xdebug``
        
        You can configure this using the following environment variable:
        
        .. code:: bash
        
            export EXTENSIONS=curl,intl,mbstring
            docker-travis-php
        
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: License :: OSI Approved :: MIT License
Classifier: Programming Language :: Python :: 2.7
