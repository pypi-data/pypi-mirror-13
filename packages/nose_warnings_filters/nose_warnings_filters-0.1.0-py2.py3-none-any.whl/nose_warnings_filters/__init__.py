
"""
Nose plugin to add warnings filters (turn them into error) using nose.cfg file.
"""


__version__ = '0.1.0'




from nose.plugins import Plugin
import warnings
import sys
import logging

log = logging.getLogger()


def import_item(name):
    """Import and return ``bar`` given the string ``foo.bar``.

    Calling ``bar = import_item("foo.bar")`` is the functional equivalent of
    executing the code ``from foo import bar``.

    Parameters
    ----------
    name : string
      The fully qualified name of the module/package being imported.

    Returns
    -------
    mod : module object
       The module that was imported.
    """
    if sys.version_info < (3,):
        if not isinstance(name, bytes):
            name =  name.encode()
    parts = name.rsplit('.', 1)
    if len(parts) == 2:
        # called with 'foo.bar....'
        package, obj = parts
        module = __import__(package, fromlist=[obj])
        try:
            pak = getattr(module, obj)
        except AttributeError:
            raise ImportError('No module named %s' % obj)
        return pak
    else:
        # called with un-dotted string
        return __import__(parts[0])


if sys.version_info < (3,):
    def from_builtins(k):
        return __builtins__[k]
else:
    import builtins
    def from_builtins(k):
        return getattr(builtins,k)


class InvalidConfig(Exception):pass

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
        invalid_config = False
        if not getattr(options, 'warningfilters', None):
            return
        for opt in options.warningfilters.split('\n'):
            values = [s.strip() for s in opt.split('|')]
            # if message empty match all messages.
            if '.' in values[2]:
                try:
                    values[2] = import_item(values[2])
                except ImportError:
                    log.warning('The following config value seem to be wrong: %s'%opt, exc_info=True)
                    invalid_config = True
                    continue
            else:
                values[2] = from_builtins(values[2])

            try:
                warnings.filterwarnings(*values)
            except AssertionError:
                log.warning('The following configuration option seem to use an error: %s' % opt, exc_info=True)
                invalid_config = True

        if invalid_config:
            raise InvalidConfig('One or more configuration option where wrong, aborting.')


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



        

