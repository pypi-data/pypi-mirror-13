"""Lemapp, the lemonodor Google-alike app framework."""

import logging
import pkg_resources
import sys

import gflags

__version__ = pkg_resources.get_distribution('lemapp').version
FLAGS = gflags.FLAGS

gflags.DEFINE_string(
    'logging_level',
    'INFO',
    'The logging level to use.')
gflags.DEFINE_string(
    'logging_filename',
    None,
    'Filename to write log output to.')


def error(msg, *args):
    """Writes an error message to stderr after flushing stdout."""
    sys.stdout.flush()
    sys.stderr.write('Error: ')
    sys.stderr.write(msg % args)
    sys.stderr.write('\n')


def print_usage():
    """Prints executable usage info.

    Prints the script's module-level documentation string as usage
    info, with any embedded '%%s' replaced by sys.argv[0], then prints
    flag info.
    """
    usage_doc = sys.modules['__main__'].__doc__
    if not usage_doc:
        usage_doc = '\nUsage: %s [flags]' % (sys.argv[0],)
    else:
        usage_doc = usage_doc.replace('%s', sys.argv[0])
    usage_doc += '\nFlags:\n%s' % (FLAGS,)
    print usage_doc


class AppError(Exception):
    """An exception that signals an application error.

    When this exception is raised, the exception's message is written
    to stderr. No stack trace is printed. A call to sys.exit(1) is
    then used to terminate the application.
    """
    pass


class UsageError(Exception):
    """An exception that signals a command-line usage error by the
    user.

    When this exception is raised, the exception's message is written
    to stderr and then print_usage is called. No stack trace is
    printed. A call to sys.exit(2) is then used to terminate the
    application.
    """
    pass


LOGGING_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def get_logging_level_by_name(name):
    return LOGGING_LEVELS[name]


LOGGING_FORMAT = ('%(threadName)s:%(asctime)s:%(levelname)s:%(module)s:'
                  '%(lineno)d %(message)s')


class App(object):
    """The base application object."""
    def __init__(self, main=None):
        """ Args:
        main: The main function.  Defaults to sys.modules['__main__'].name.
        """
        if not main:
            main = sys.modules['__main__'].main
        self.main = main
        assert main

    def configure_logging(self):
        logging.basicConfig(
            filename=FLAGS.logging_filename,
            format=LOGGING_FORMAT)
        log_specs = FLAGS.logging_level.split(',')
        for log_spec in log_specs:
            if ':' in log_spec:
                module, level_name = log_spec.split(':')
                level = get_logging_level_by_name(level_name)
                logging.getLogger(module).setLevel(level)
            else:
                logging.getLogger().setLevel(log_spec)

    def configure(self):
        self.configure_logging()

    def run(self, argv=None):
        """Runs the main function after parsing command-line flags.

        Also configures logging and sets up profiling if requested with
        --profile.
        """
        if not argv:
            argv = sys.argv
        try:
            FLAGS.UseGnuGetOpt()
            argv = FLAGS(argv)
        except gflags.FlagsError, e:
            error('%s', e)
            print_usage()
            sys.exit(2)

        self.configure()

        try:
            self.main(argv)
        except AppError as e:
            error(str(e))
            sys.exit(1)
        except UsageError as e:
            error(str(e))
            print_usage()
            sys.exit(2)
