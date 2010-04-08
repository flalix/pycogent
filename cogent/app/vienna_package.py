#!/usr/bin/env python

from cogent.app.util import CommandLineApplication,\
    CommandLineAppResult, ResultPath
from cogent.app.parameters import Parameter, FlagParameter, ValuedParameter,\
    MixedParameter,Parameters, _find_synonym, is_not_None
from cogent.struct.rna2d import ViennaStructure
from cogent.core.alignment import DataError
from cogent.parse.rnaalifold import MinimalRnaalifoldParser
from random import choice

__author__ = "Rob Knight"
__copyright__ = "Copyright 2007-2009, The Cogent Project"
__credits__ = ["Jeremy Widmann", "Rob Knight"]
__license__ = "GPL"
__version__ = "1.5.0.dev"
__maintainer__ = "Sandra Smit"
__email__ = "Sandra.Smit@colorado.edu"
__status__ = "Production"

class RNAfold(CommandLineApplication):
    """Application controller for RNAfold (in the Vienna RNA package)

    Manual on:
    http://www.tbi.univie.ac.at/~ivo/RNA/RNAfold.html
    http://bioweb.pasteur.fr/docs/man/man/RNAfold.1.html

    Parameters with default values:
        -T: 37 (temperature)
        -d: 1 (only unpaired bases in dangling ends)
        -S: 1.07 (scale)

    Input is always written to a file which is used as the application's input.
    StdErr is suppressed by default, but can be overruled in an instance.
    """
    _parameters = {
    '-p':MixedParameter(Prefix='-',Name='p',Delimiter='',Value=False),
    '-C':FlagParameter(Prefix='-',Name='C'),
    '-T':ValuedParameter(Prefix='-',Name='T',Value=37,Delimiter=' '),
    '-4':FlagParameter(Prefix='-',Name=4),
    '-d':MixedParameter(Prefix='-',Name='d',Delimiter='',Value=1),
    '-noLP':FlagParameter(Prefix='-',Name='noLP'),
    '-noGU':FlagParameter(Prefix='-',Name='noGU'),
    '-noCloseGU':FlagParameter(Prefix='-',Name='noCloseGU'),
    '-e':ValuedParameter(Prefix='-',Name='e',Delimiter=' '),
    '-P':ValuedParameter(Prefix='-',Name='P',Delimiter=' '),
    '-nsp':ValuedParameter(Prefix='-',Name='nsp',Delimiter=' '),
    '-S':ValuedParameter(Prefix='-',Name='S',Value=1.07,Delimiter=' ')}
    _synonyms = {'Temperature':'-T','Temp':'-T','Scale':'-S'}
    _command = 'RNAfold'
    _input_handler = '_input_as_lines'
    _suppress_stderr = True 

    def _input_as_path(self,filename):
        """Returns '>"filename"' to redirect input to stdin"""
        return ''.join(\
            ['<', str(super(RNAfold,self)._input_as_path(filename))])
    
    def _input_as_lines(self,data):
        """Returns '>"temp_filename" to redirect input to stdin"""
        return ''.join(['<',str(super(RNAfold,self)._input_as_lines(data))])

    def _get_result_paths(self,data):
        """Specifies the paths of output files generated by the application
        
        data: the data the instance of the application is called on

        You always get back: StdOut,StdErr, and ExitStatus
        RNAfold can produce two additional output files:
            a secondary structure structure graph. Default name: rna.ps
            a dot plot of the base pairing matrix. Default name: dp.ps
        The default names are used for unnamed sequences. Files are created
            in the current working directory.
        You can make a sequence named by inserting a line '>name' above it in
            your input file (or list of sequences). The ss and dp files for 
            named sequences will be written to name_ss.ps and name_dp.ps
        """
        result = {}
        name_counter = 0
        seq_counter = 0
        if not isinstance(data,list):
            #means data is file
            data = open(data).readlines()
        for item in data:
            if item.startswith('>'):
                name_counter += 1
                name = item.strip('>\n')
                result[(name+'_ss')] =\
                    ResultPath(Path=(self.WorkingDir+name+'_ss.ps'))
                result[(name+'_dp')] =\
                    ResultPath(Path=(self.WorkingDir+name+'_dp.ps'),\
                    IsWritten=self.Parameters['-p'].isOn())
            else:
                seq_counter += 1
        
        result['SS'] = ResultPath(Path=self.WorkingDir+'rna.ps',\
            IsWritten=seq_counter - name_counter > 0) #Secondary Structure
        result['DP'] = ResultPath(Path=self.WorkingDir+'dot.ps',
            IsWritten=(self.Parameters['-p'].isOn() and\
            seq_counter - name_counter > 0)) #DotPlot
        return result

def get_constrained_fold(sequence, constraint_string, params=None):
    """Returns secondary structure from RNAfold with constraints.
    
        - sequence: RNA sequence object or string.
        - constraint_string: RNAfold folding constraint string.
        - params: dict of additional RNAfold parameters.
    """
    #Check that sequence and constraint string exist.
    if not sequence:
        raise ValueError, 'No sequence found!'
    elif not constraint_string:
        raise ValueError, 'No constraint string found!'
    
    sequence = str(sequence) 
    #Check that sequence and constraint_string are equal length.
    if len(sequence) != len(constraint_string):
        raise ValueError, 'Sequence and constraint string are not same length!'
    app = RNAfold(params=params)
    #Turn on constrained folding.
    app.Parameters['-C'].on()
    
    res = app([sequence,constraint_string])
    #Parse out seq, struct string and energy.
    seq, struct, energy = MinimalRnaalifoldParser(res['StdOut'].readlines())[0]
    #Clean up after application.
    res.cleanUp()
    
    return seq, struct, energy
    

class RNAsubopt(CommandLineApplication):
    """Application controller for RNAsubopt (in the Vienna RNA package)

    Manual on:
    http://www.tbi.univie.ac.at/~ivo/RNA/RNAsubopt.html
    http://bioweb.pasteur.fr/docs/man/man/RNAsubopt.1.html

    Parameters with default values:
        -e: 1 (range)
        -T: 37 (temperature)
        -d: 2 (dangling ends as in partition function folding)

    Input is always written to a file which is used as the application's input.
    StdErr is suppressed by default, but can be overwritten in an instance.
    """
    _parameters = {
    '-p':ValuedParameter(Prefix='-',Name='p',Delimiter=' '),
    '-C':FlagParameter(Prefix='-',Name='C'),
    '-e':ValuedParameter(Prefix='-',Name='e',Delimiter=' ',Value=1),
    '-ep':ValuedParameter(Prefix='-',Name='ep',Delimiter=' '),
    '-s':FlagParameter(Prefix='-',Name='s'),
    '-lodos':FlagParameter(Prefix='-',Name='lodos'),
    '-T':ValuedParameter(Prefix='-',Name='T',Value=37,Delimiter=' '),
    '-4':FlagParameter(Prefix='-',Name=4),
    '-d':MixedParameter(Prefix='-',Name='d',Delimiter='',Value=2),
    '-noGU':FlagParameter(Prefix='-',Name='noGU'),
    '-noCloseGU':FlagParameter(Prefix='-',Name='noCloseGU'),
    '-P':ValuedParameter(Prefix='-',Name='P',Delimiter=' '),
    '-logML':FlagParameter(Prefix='-',Name='logML'),
    '-nsp':ValuedParameter(Prefix='-',Name='nsp',Delimiter=' '),
    '-noLP':FlagParameter(Prefix='-',Name='noLP')}
    _synonyms = {'Temperature':'-T','Temp':'-T','EnergyRange':'-e','Sort':'-s'}
    _command = 'RNAsubopt'
    _input_handler = '_input_as_lines'
    _suppress_stderr = True
        
    def _input_as_path(self,filename):
        """Returns '>"filename"' to redirect input to stdin
        
        Includes quotes to handle file names containing spaces.
        """
        return ''.join(\
            ['<',str(super(RNAsubopt,self)._input_as_path(filename))])
    
    def _input_as_lines(self,data):
        """Returns '>temp_filename to redirect input to stdin
        
        Includes quotes to handle file names containing spaces.
        """
        return ''.join(['<',str(super(RNAsubopt,self)._input_as_lines(data))])
    
    
class RNAplot(CommandLineApplication):
    """Application controller for RNAplot (in the Vienna RNA package)

    Manual on:
    http://www.tbi.univie.ac.at/~ivo/RNA/RNAplot.html

    Input is always written to a file which is used as the application's input.
    StdErr is suppressed by default, but can be overwritten in an instance.
    """
    _parameters = {
        #-t 0|1 Choose  the  layout  algorithm.  Simple  radial  layout if 0, or
        #       naview if 1.  Default is 1.
        '-t':ValuedParameter(Prefix='-',Name='t',Delimiter=' '),\
        
        #-o ps|gml|xrna|svg
        #       Specify output format. Available formats are:  PostScript  (ps),
        #       Graph  Meta  Language (gml), Scalable Vector Graphics (svg), and
        #       XRNA save file (xrna). Output filenames will end in ".ps" ".gml"
        #      ".svg" ".ss", respectively. Default is ps.
        '-o':ValuedParameter(Prefix='-',Name='o',Delimiter=' '),\
        
        #--pre string --post string
        #       Add annotation macros to postscript file, and add the postscript
        #       code in "string" just before (--pre) or after (--post) the  code
        #       to  draw  the  structure. This is an easy way to add annotation,
        #       e.g to mark position 15 with circle use --post "15 cmark"
        '--pre':ValuedParameter(Prefix='--',Name='pre',Delimiter=' '),\
        '--post':ValuedParameter(Prefix='--',Name='post',Delimiter=' '),\
        }

    _command = 'RNAplot'
    _input_handler = '_input_as_lines'
    _suppress_stderr = True

    FILETYPE_TO_EXTENSION = {'ps':'.ps',\
                                  'gml':'.gml',\
                                  'svg':'.svg',\
                                  'xrna':'.ss'
                                  }
    def getHelp(self):
        """Method that points to the RNAplot documentation."""
        
        help_str = \
        """
        See RNAplot documentation at:
        http://www.tbi.univie.ac.at/~ivo/RNA/RNAplot.html
        """
        return help_str
        
    def _get_tmp_seqname(self):
        """Returns a temporary name for sequence.
            - Useful since RNAplot names plot files according to sequence
                name when available.  Will use the 'rna' prefix if no
                sequence name is supplied.
            - Note only takes first 12 characters as the name.  So this function
                will only use make a name 9 long with 'tmp' as a prefix.
        """
        chars = "abcdefghigklmnopqrstuvwxyz"
        picks = chars + chars.upper() + "0123456790"
        return 'tmp'+''.join([choice(picks) for i in range(9)])
    
    def _input_as_path(self,filename):
        """Returns '>"filename"' to redirect input to stdin
        
        Includes quotes to handle file names containing spaces.
        """
        return ''.join(\
            ['<',str(super(RNAplot,self)._input_as_path(filename))])
    
    def _input_as_lines(self,data):
        """Returns '>temp_filename to redirect input to stdin
        
        Includes quotes to handle file names containing spaces.
        """
        return ''.join(['<',str(super(RNAplot,self)._input_as_lines(data))])
    
    def _get_outfile_extension(self):
        """Returns file extension of RNAplot.
        """
        if not self.Parameters['-o'].isOn():
            return '.ps'
        else:
            filetype = self._absolute(str(self.Parameters['-o'].Value))
            return FILETYPE_TO_EXTENSION[filetype]
    
    def _get_result_paths(self,data):
        """Specifies the paths of output files generated by the application
        
        data: the data the instance of the application is called on

        You always get back: StdOut,StdErr, and ExitStatus
        RNAplot can produce one output files:
            a secondary structure structure graph.
        The default names are used for unnamed sequences. Files are created
            in the current working directory.
        You can make a sequence named by inserting a line '>name' above it in
            your input file (or list of sequences). The ss files for 
            named sequences will be written to name_ss.ps.
        """
        result = {}
        name_counter = 0
        seq_counter = 0
        if not isinstance(data,list):
            #means data is file
            data = open(data).readlines()
        res_extension = self._get_outfile_extension()
        for item in data:
            if item.startswith('>'):
                name_counter += 1
                name = item.strip('>\n')
                result[(name+'_ss')] =\
                    ResultPath(Path=(self.WorkingDir+name+'_ss'+res_extension))
            else:
                seq_counter += 1
        if (seq_counter/2 - name_counter > 0):
            result['SS'] = ResultPath(Path=self.WorkingDir+'rna'+res_extension,\
                IsWritten=True) #Secondary Structure
        return result
    
def plot_from_seq_and_struct(seq, struct,seqname=None, params=None):
    """Returns plot of structure given seq and struct.
    
        - seq: sequence corresponding to struct.
            - Can be anything that behaves as a string same length as struct.
        - struct: Vienna structure corresponding to seq.  Must be a valid
            Vienna structure.
    """
    seq = str(seq)
    #Construct ViennaStructure.  Object will handle errors in struct string.
    struct = ViennaStructure(struct)
    if len(seq) != len(struct):
        raise DataError, 'Sequence and structure are not same length!'
    app = RNAplot(WorkingDir='/tmp',\
        params=params)
    if seqname is None:
        seqname = app._get_tmp_seqname()
    res = app(['>'+seqname,seq,struct])
    plot = res[seqname+'_ss'].read()
    res.cleanUp()
    return plot

