Copyright (c) 2013 Ronny Andersson

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

Download-URL: https://pypi.python.org/pypi/zignal
Description: # zignal
        
        This is a python audio signal processing library.
        
        
        ## Basic example
        
            import zignal
            
            x = zignal.Sinetone(fs=44100, f0=997, duration=0.01, gaindb=-20)
            print(x)
            x.plot()
        
        See the examples folder for more examples.
        
        ## Requirements
        
        This library relies on numpy, scipy and matplotlib. At the moment it is
        recommended to install these using the systems default package manager.
        On debian/ubuntu, do a 
        
            sudo apt-get install python-numpy python-scipy python-matplotlib python-pyaudio
        
        to install the requirements.
        
        ## Design goals
        
        1.  Readability over efficiency. This is a python library for development and
            understanding of audio signal processing.
        2.  The initial goal is to write the functionality in pure python, with the
            use of numpy, scipy and matplotlib. See rule 1. If efficiency becomes an
            issue a c/c++ library might be implemented but the pure python code must
            remain the default choice.
        3.  Design for non real-time processing. Functionality to do real-time
            processing can be added if it does not break rule 1.
        4.  Self documentation. The code should aim to be well documented, in the
            source code itself.
        
Keywords: audio,sound,card,soundcard,pyaudio,portaudio,playback,recording,digital,signal,processing,DSP,signalprocessing,fourier,FFT,filter,filtering,parametric,eq,equaliser,equalizer,biquad,mls,mlssa,maximum,length,sequence,maximumlengthsequence,pseudo,random,pseudorandom,measure,measurement,impulse,response,impulseresponse,frequency,frequencyresponse,magnitude,magnituderesponse
Platform: any
Classifier: Development Status :: 3 - Alpha
Classifier: Environment :: Console
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Education
Classifier: Intended Audience :: Science/Research
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Education
Classifier: Topic :: Multimedia :: Sound/Audio :: Analysis
Classifier: Topic :: Multimedia :: Sound/Audio :: Capture/Recording
Classifier: Topic :: Multimedia :: Sound/Audio :: Editors
Classifier: Topic :: Multimedia :: Sound/Audio :: Sound Synthesis
Classifier: Topic :: Scientific/Engineering :: Mathematics
Classifier: Topic :: Software Development :: Quality Assurance
Classifier: Topic :: Software Development :: Testing
