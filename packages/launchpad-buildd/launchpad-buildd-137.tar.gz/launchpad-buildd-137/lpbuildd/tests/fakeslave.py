# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type
__all__ = [
    'FakeMethod',
    'FakeSlave',
    ]

import os


class FakeMethod:
    """Catch any function or method call, and record the fact.

    Use this for easy stubbing.  The call operator can return a fixed
    value, or raise a fixed exception object.

    This is useful when unit-testing code that does things you don't
    want to integration-test, e.g. because it wants to talk to remote
    systems.
    """

    def __init__(self, result=None, failure=None):
        """Set up a fake function or method.

        :param result: Value to return.
        :param failure: Exception to raise.
        """
        self.result = result
        self.failure = failure

        # A log of arguments for each call to this method.
        self.calls = []

    def __call__(self, *args, **kwargs):
        """Catch an invocation to the method.

        Increment `call_count`, and adds the arguments to `calls`.

        Accepts any and all parameters.  Raises the failure passed to
        the constructor, if any; otherwise, returns the result value
        passed to the constructor.
        """
        self.calls.append((args, kwargs))

        if self.failure is None:
            return self.result
        else:
            # pylint thinks this raises None, which is clearly not
            # possible.  That's why this test disables pylint message
            # E0702.
            raise self.failure

    @property
    def call_count(self):
        return len(self.calls)

    def extract_args(self):
        """Return just the calls' positional-arguments tuples."""
        return [args for args, kwargs in self.calls]

    def extract_kwargs(self):
        """Return just the calls' keyword-arguments dicts."""
        return [kwargs for args, kwargs in self.calls]


class FakeConfig:
    def get(self, section, key):
        return key


class FakeSlave:
    def __init__(self, tempdir):
        self._cachepath = tempdir
        self._config = FakeConfig()
        self.waitingfiles = {}
        for fake_method in (
            "storeFile", "addWaitingFile", "emptyLog", "log",
            "chrootFail", "buildFail", "builderFail", "depFail",
            ):
            setattr(self, fake_method, FakeMethod())

    def cachePath(self, file):
        return os.path.join(self._cachepath, file)

    def anyMethod(self, *args, **kwargs):
        pass

    def wasCalled(self, name):
        return getattr(self, name).call_count > 0

    def getArch(self):
        return 'i386'
