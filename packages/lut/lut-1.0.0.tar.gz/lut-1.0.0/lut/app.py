import lut
import optparse
import os
import sys

optparse.OptionParser.format_epilog = lambda self, formatter: self.epilog

class App(object):
    '''
    Interface for commandline.
    '''

    def __init__(self):
        self.cli = None
        
    @staticmethod
    def main(argv):
        app = App()
        rcode = app.parsecli(argv)
        if rcode:
            return rcode

        return app.run()

    def parsecli(self, argv):
        desc = """Python interpolation lookup table."""
        examples = """
Examples:

Lookup single value.

    $ lut -t lut.json -r 2,100 1.23

Lookup many values.

    $ lut -t lut.json  1,2,3

Lookup many values in file.

    $ lut -t lut.json -r 2,100 values.txt
"""
        usage = "Usage: %prog [options] value | file"
        parser = optparse.OptionParser(description=desc, 
                                       epilog=examples,
                                       usage=usage)

        parser.add_option('-m', '--method', help='Table interp method overrides file (none, cosine, linear).', default='')
        parser.add_option('-r', '--range', help='Table min/max range overrides file.', default='')
        parser.add_option('-s', '--size', help='Table size overrides file.', default='')
        parser.add_option('-t', '--table', help='Input table JSON file.', default='')

        opts, args = parser.parse_args(argv)
        opts = vars(opts)
  
        for k in 'table '.split():
            if not opts[k]:
                parser.error('missing --%s' % (k))

        if opts['method'] == 'none':
            opts['method'] = None
        
        if opts['range']:
            opts['range'] = map(float, opts['range'].split(','))
        
        if opts['size']:
            opts['size'] = int(opts['size'])
    
        if not args[1:]:
            parser.error('missing value or file to lookup')
        else:            
            arg = args[-1]
            if os.path.exists(arg):
                opts['file'] = arg
            else:
                opts['file'] = None
                opts['value'] = float(arg) 
    
        self.cli = opts
        
        return 0

    def run(self):
        t = lut.load(self.cli['table'])
        do_build = False
        
        if self.cli['method'] in [None, 'linear', 'cosine']:
            t.method = self.cli['method']
            do_build = True
        if self.cli['range']:
            t.range = self.cli['range']
            do_build = True
        if self.cli['size']:
            t.size = self.cli['size']
            do_build = True

        if do_build:
            t.build()
            
        if self.cli['file']:
            values = []
            with open(self.cli['file']) as f:
                strings = f.read().replace('\n', ' ').replace(',', ' ').split()
                values = [float(s) for s in strings if s] 
            
            result = t.get(values)
        else:    
            result = t.get(self.cli['value'])
            
        sys.stdout.write(str(result) + '\n')
        
        return 0

def main():
    sys.exit(App.main(sys.argv))

if '__main__' == __name__: main()
