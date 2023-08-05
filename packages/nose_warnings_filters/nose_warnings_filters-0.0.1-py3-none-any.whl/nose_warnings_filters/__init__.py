
"""
Nose plugin to add warnings filters (turn them into error) using nose.cfg file.
"""


__version__ = '0.0.1'


from nose.plugins import Plugin
import warnings
import builtins

class WarningFilter(Plugin):
    def options(self, parser, env):
        """
        Add options to command line.
        """
        super(WarningFilter, self).options(parser, env)
        parser.add_option("--warningfilters",
                          default=None,
                          help="Treat warnings that occur WITHIN tests as errors.")

    def configure(self, options, conf):
        """
        Configure plugin.
        """
        for opt in options.warningfilters.split( '\n'):
            vs = [s.strip() for s in opt.split('|')]
            vs[2] = getattr(builtins, vs[2])
            warnings.filterwarnings(*vs)

        super(WarningFilter, self).configure(options, conf)


    def prepareTestRunner(self, runner):
        """
        Treat warnings as errors.
        """
        return WarningFilterRunner(runner)



class WarningFilterRunner(object):

    def __init__(self, runner):
        self.runner=runner
        
    def run(self, test):
        return self.runner.run(test)



        
