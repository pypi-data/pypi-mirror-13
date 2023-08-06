import io
import subprocess
import signal
import codecs

from collections import namedtuple

from . import config, catch_sigterm


# package-wide default encoding
# used for any format that does not explicitly override it
DEFAULTENCODING = 'utf-8'

# package-wide safe fallback encoding
# to be used if decoding input as utf-8 fails
FALLBACKENCODING = 'latin-1' \
                   if config.input_decoding == 'lenient' else \
                   'utf-8'

# vcf gets read in and written as utf-8
# handling of decoding errors during reading is determined by config setting
vcf_defaultencoding = 'utf-8' # see the official format specs
vcf_handle_decoding_errors = 'backslashreplace' \
                             if config.input_decoding == 'lenient' else \
                             'strict'


def get_custom_std (stream, encoding=DEFAULTENCODING, errors=None):
    current_encoding = stream.encoding
    if encoding is None:
        encoding = current_encoding
    elif encoding != current_encoding:
        # see if the normalized names match
        encoding = codecs.lookup(encoding).name
        current_encoding = codecs.lookup(current_encoding).name
    if errors is None:
        errors = stream.errors
    ret_stream = stream
    if encoding != current_encoding or errors != stream.errors:
        try:
            ret_stream = CustomStd(stream, encoding, errors)
        except:
            pass
    return ret_stream


class CustomStd (io.TextIOWrapper):
    def __init__(self, stream, encoding, errors):
        self._super = super(CustomStd, self)
        self.original = stream
        self._super.__init__(stream.buffer,
                             encoding=encoding,
                             errors=errors,
                             newline=stream.newlines,
                             line_buffering=True)

    def write (self, data):
        self.original.flush()       
        self._super.write(data)

    def close (self):
        self._super.flush()


# just an idea:
# def get_safe_stdout (encoding=DEFAULTENCODING):
#     if encoding == sys.stdout.encoding:
#         return sys.stdout
#     else:
#         return SafeStdoutWriter()
#
#
# class SafeStdoutWriter (object):
#     def write (self, data):
#         encoding = sys.stdout.encoding
#         data = str(data.encode(encoding, 'backslashreplace'), encoding)
#         sys.stdout.write(data)

    
ApplicationReturnValue = namedtuple('ApplicationReturnValue', ['call', 'results', 'errors'])


class ExternalApplicationCall (object):
    """General interface for running wrapped applications as subprocesses."""

    def __init__ (self, command=None, subcommand=None, args=None,
                  stdin = None, stdout = None, stderr = None,
                  input = None):
        # argument validation
        if command is None:
            if subcommand is not None:
                raise MiModDLibraryError('The subcommand argument requires the command argument to be specified.')
            elif args is None:
                raise MiModDLibraryError('The command or the args argument must be provided.')
        if input is not None and stdin is not subprocess.PIPE:
            raise MiModDLibraryError('Cannot send data to a process without piping its stdin')        

        # construct args list for Popen object
        if command is None:
            self.call_args = args
        else:
            self.call_args = [command]
            if subcommand is not None:
                self.call_args.append(subcommand)
            self.call_args += args

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        if input is None:
            self.bytes_input = None
        else:
            self.bytes_input = input.encode(DEFAULTENCODING)
        self.Popen = None
        self._run_info = []
        self.run_info = None
        
    def start (self):
        self.Popen = subprocess.Popen(self.call_args,
                                      stdin=self.stdin,
                                      stdout=self.stdout,
                                      stderr=self.stderr)
    
    def communicate (self):
        self._run_info += self.Popen.communicate(self.bytes_input)

    def finalize (self):
        _results, _errors = self._run_info
        if _results is not None:
            try:
                results = _results.decode(DEFAULTENCODING)
            except UnicodeDecodeError:
                results = _results.decode(FALLBACKENCODING)
        else:
            results = _results
        if _errors is not None:
            try:
                errors = _errors.decode(DEFAULTENCODING)
            except UnicodeDecodeError:
                errors = _errors.decode(FALLBACKENCODING)
        else:
            errors = _errors

        self.run_info = ApplicationReturnValue(' '.join(self.call_args),
                                               results,
                                               errors)
        return self.Popen.returncode
    
    def run (self):
        # catch SIGTERM so that we can also terminate the subprocess
        signal.signal(signal.SIGTERM, catch_sigterm)
        try:
            self.start()
            self.communicate()
        except:
            # terminate the subprocess
            try:
                self.Popen.terminate()
            except:
                pass
            raise
        return self.finalize()
