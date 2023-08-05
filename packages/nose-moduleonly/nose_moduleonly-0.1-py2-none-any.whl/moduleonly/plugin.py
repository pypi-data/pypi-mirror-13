import os

from nose.plugins import Plugin


class ModuleOnly(Plugin):
    """
    Prints only the test module instead of the full test name.
    Use with --collect-only to get a list of test modules.
    """

    name = 'moduleonly'

    def options(self, parser, env=os.environ):
        super(ModuleOnly, self).options(parser, env=env)
        parser.add_option('--module-only', action="store_true",
                          help=ModuleOnly.__doc__)

    def configure(self, options, conf):
        super(ModuleOnly, self).configure(options, conf)
        if options.module_only:
            self.enabled = True

    def describeTest(self, test):
        r = test.test.__class__.__module__
        if r == 'nose.failure':
            # Fallback, because 'nose.failure' isn't very helpful.
            # instead give e.g. 'Failure: ImportError (No module named foo.bar)'
            return str(test.test)
        return r
