Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

Description: Yaraprocessor
        =============
        
        `YARA <http://code.google.com/p/yara-project/>`_ is an awesome tool.
        It's aimed at helping malware researchers to identify and classify malware
        samples. With YARA you can create descriptions of malware families based
        on textual or binary patterns contained on samples of those families.
        
        However, sometimes the data you are analyzing needs some manipulation in
        order to achieve the best results. Yaraprocessor allows you to scan data
        streams in few unique ways. It supports scanning data streams in discrete
        chunks, or buffers. These chunks can overlap or be completely disjoint
        depending on the 'processing_mode' selected.
        
        Yaraprocessor was originally written for
        `Chopshop <https://github.com/MITRECND/chopshop>`_. Combined with Chopshop, it
        allows for dynamic scanning of payloads plucked from network packet capture.
        Historically, signature based tools operate over the entire PCAP file. With
        Chopshop and Yaraprocessor, YARA can be ran against individual packet payloads
        as well as a concatenation of some or all of the payloads. Ideally, this makes
        writing signatures easier. Check out the Chopshop module `yarashop
        <https://github.com/MITRECND/chopshop/blob/master/modules/yarashop.py>`_ to see it in action!
        
        Dependencies
        ------------
        
        - `Python 2.7 <http://www.python.org/download/releases/2.7.3/>`_
        - `YARA <http://code.google.com/p/yara-project/>`_
        - `YARA-python bindings <http://code.google.com/p/yara-project/>`_
        
        Installation
        ------------
        
        Simply clone the repository via git:
        
        .. code-block:: bash
        
            $ git clone https://github.com/MITRECND/yaraprocessor.git
        
        Or download the latest release from our `github page
        <https://github.com/MITRECND/yaraprocessor/archive/master.zip>`_.
        
        Once you have the code, run the following command inside the
        Yaraprocessor directory:
        
        .. code-block:: bash
        
            $ python setup.py install
        
        Using it!
        ---------
        
        While yaraprocessor was built for use with
        `Chopshop <https://github.com/MITRECND/chopshop>`_, it aims for simple
        and straightforward usage and integration with other tools. Simply
        import yaraprocessor, instantiate a "Processor" object, and start
        analyzing data.
        
        .. code-block:: python
        
            from yaraprocessor import Processor
        
            # Yara rules are passed as a list of filenames
            p = Processor(['/full/path/to/rules, relative/path/to/other/rules'])
        
            # By default, the processor will operate in 'raw' mode, meaning it
            # will scan whatever data you give it. Note that in 'raw' mode, you
            # are required to call 'analyze', which will return yara matches if
            # found.
            p.data = data
            results = p.analyze()
        
            # 'analyze' returns yara matches and also stores them in 'p.results'
            # for convenient access.
            if p.results:
                for match in p.results:
                    print match
        
            # When operating in other processing modes, data will be continuously
            # buffered and automatically processed when the buffer fills. In these
            # modes, you don't have to ever call 'p.analyze'; instead simply check
            # for results.
        
            if p.results:
                for match in p.results:
                    print match
        
        Contributing
        ------------
        
        We love to hear from people using our tools and code. Feel free to discuss
        issues on our `issue tracker <https://github.com/MITRECND/yaraprocessor/issues>`_ and make pull requests!
        
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Natural Language :: English
Classifier: License :: OSI Approved :: BSD License
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Security
Classifier: Topic :: System :: Monitoring
