#!/usr/bin/env python

from cogent.app.util import CommandLineApplication,\
    CommandLineAppResult, ResultPath
from cogent.app.parameters import Parameter, FlagParameter, ValuedParameter,\
    MixedParameter,Parameters, _find_synonym, is_not_None

__author__ = "Shandy Wikman"
__copyright__ = "Copyright 2007-2008, The Cogent Project"
__contributors__ = ["Shandy Wikman"]
__license__ = "GPL"
__version__ = "1.2"
__maintainer__ = "Shandy Wikman"
__email__ = "ens01svn@cs.umu.se"
__status__ = "Development"

class Covet(CommandLineApplication):
    """Application controller for Covet

    Generate new models, by training them on example sequences.

    where options are:
     -a <alignfile>  : make starting model from alignment
     -A <filename>   : save alignments to filename.1, etc., for animation
     -b <backupfile> : each iteration, back up curr model to <backupfile>
     -f              : use flat text save formats, portable but clumsy
     -G <GOP>        : gap-open prob 0 < gop < 1 for random alignment generation
     -h              : print short help and version info
     -i <cm file>    : take start model from <cm file>
     -m              : do maximum likelihood model construction (slow!)
     -p <prior file> : use prior in <file>; default is Laplace plus-one
     -s <seed>       : set random() seed
     -X <GEX>        : gap-extend prob 0 < gex < 1 for random alignment generation

    """

    _parameters = {
        '-a':ValuedParameter(Prefix='-',Name='a',Delimiter=' '),
        '-A':ValuedParameter(Prefix='-',Name='A',Delimiter=' '),
        '-b':ValuedParameter(Prefix='-',Name='b',Delimiter=' '),
        '-f':FlagParameter(Prefix='-',Name='f'),
        '-G':ValuedParameter(Prefix='-',Name='G',Delimiter=' '),
        '-i':ValuedParameter(Prefix='-',Name='i',Delimiter=' '),
        '-m':FlagParameter(Prefix='-',Name='m'),
        '-p':ValuedParameter(Prefix='-',Name='p',Delimiter=' '),
        '-s':ValuedParameter(Prefix='-',Name='s',Delimiter=' '),
        '-X':ValuedParameter(Prefix='-',Name='X',Delimiter=' ')}
    
    _command = 'covet'
    _input_handlar = '_input_as_string'


    def _input_as_string(self,filename):
        """Returns 'modelname' and 'filename' to redirect input to stdin"""
        return ' '.join([filename+'.cm',super(Covet,self)._input_as_string(filename)])

    def _input_as_lines(self,data):
        """Returns 'temp_filename to redirect input to stdin"""
        filename = self._input_filename = self.getTmpFilename(self.WorkingDir)
        data_file = open(filename,'w')
        data_to_file = '\n'.join([str(d).strip('\n') for d in data])
        data_file.write(data_to_file)
        data_file.write('\n') #must end with new line
        data_file.close()
        return ' '.join([filename+'.cm',filename])

  
    def _get_result_paths(self,data):
        """Specifies the paths of output files generated by the application
        
        data: the data the instance of the application is called on
        
        CMfinder produces it's output in two files .align and .motif
        it also prints an output to sdtout.

        """
        result={}
        if not isinstance(data,list):
            inputPath=data
        else:
            inputPath=''.join([self._input_filename])
       
        result['cm'] =\
              ResultPath(Path=(inputPath+'.cm'))
        
        if self._input_filename is not None:
            result['_input_filename'] = ResultPath(self._input_filename)

        return result


class Coves(CommandLineApplication):
    """Application controller for Coves

    Computes the score of each whole sequence individually, and prints the scores.
    You might use it to detect sequences which, according to the model, don't belong
    to the same structural consensus; sequences which don't fit the model get negative
    scores.


    where options are:
    -a          : show all pairs, not just Watson-Crick
    -g <gcfrac> : set expected background GC composition (default 0.5)
    -m          : mountain representation of structural alignment
    -s          : secondary structure string representation of
                  structural alignment
    """

    _parameters = {
        '-a':FlagParameter(Prefix='-',Name='a'),
        '-g':ValuedParameter(Prefix='-',Name='g',Delimiter=' '),
        '-m':FlagParameter(Prefix='-',Name='m'),
        '-s':FlagParameter(Prefix='-',Name='s',Value=True)}

    _command = 'coves'
    _input_handler = '_input_as_string'


    def _input_as_string(self,filename):
        """Returns 'modelname' and 'filename' to redirect input to stdin"""
        return ' '.join([filename+'.cm',super(Coves,self)._input_as_string(filename)])

class Covee(CommandLineApplication):
    """Application controller for Covee

    emits a consensus structure prediction for the family.

    where options are:
     -a        : annotate all pairs, not just canonical ones
     -b        : emit single most probable sequence
     -l        : print as mountain landscape
     -s <seed> : set seed for random()
    EXPERIMENTAL OPTIONS:
     -L        : calculate expected length distributions for states


    """

    _parameters = {
        '-a':FlagParameter(Prefix='-',Name='a'),
        '-b':FlagParameter(Prefix='-',Name='b',Value=True),
        '-l':FlagParameter(Prefix='-',Name='l'),
        '-s':ValuedParameter(Prefix='-',Name='s',Delimiter=' '),
        '-L':FlagParameter(Prefix='-',Name='L')}


    _command = 'covee'
    _input_handler = '_input_as_string'
    
    def _input_as_string(self,filename):
        """Returns 'modelname' and 'filename' to redirect input to stdin"""
        return ' '.join([filename+'.cm',super(Covee,self)._input_as_string(filename)])

    def _input_as_lines(self,data):
        """Returns 'temp_filename to redirect input to stdin"""
        return ''.join([data+'.cm',super(Covee,self)._input_as_lines(data)])


class Covea(CommandLineApplication):
    """Application controller for Covea


    here supported options are:
     -a             : annotate all base pairs, not just canonical ones
     -h             : print short help and version info
     -o <outfile>   : write alignment to <outfile> in SELEX format
     -s <scorefile> : save individual alignment scores to <scorefile>

     Experimental options:
     -S             : use small-memory variant of alignment algorithm

    """

    _parameters = {
        '-a':FlagParameter(Prefix='-',Name='a'),
        '-o':ValuedParameter(Prefix='-',Name='o',Delimiter=' '),
        '-s':ValuedParameter(Prefix='-',Name='s',Delimiter=' '),
        '-S':FlagParameter(Prefix='-',Name='S')}
        
    _command = 'covea'
    _input_handler = '_input_as_string'

    def _input_as_string(self,filename):
        """Returns 'modelname' and 'filename' to redirect input to stdin"""
        return ' '.join([filename+'.cm',super(Covea,self)._input_as_string(filename)])

    def _input_as_lines(self,data):
        """Returns 'temp_filename to redirect input to stdin"""
        return ''.join([data+'.cm',super(Covea,self)._input_as_lines(data)])
