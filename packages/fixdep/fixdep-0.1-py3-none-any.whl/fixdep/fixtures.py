from mock import patch
try:
    from pytest import fixture as pytestfixture
except ImportError:
    def pytestfixture(fun):
        return fun


class TestCase(object):

    _object_cls = None

    @pytestfixture
    def fixtures(self):
        pass


class BaseFixtures(object):

    def __init__(self, parent):
        self.parent = parent
        self._instance_cache = {}

    def setUp(self):
        self._test_cache = {}
        self._patchers = []
        self._test_cache = {}

    def tearDown(self):
        for patch in self._patchers:
            patch.stop()

    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()

    def pobject(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()

    def pdict(self, *args, **kwargs):
        patcher = patch.dict(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()


class FixtureContext(object):

    def __init__(self, parent=None, fixtures='Fixtures'):
        self.parent = parent
        self._fixtures = fixtures

    def __enter__(self):
        return self._fixtures_setup()

    def __exit__(self, type, value, traceback):
        self._fixtures_teardown()

    def _fixtures_setup(self):
        if type(self._fixtures) is str:
            self.fixtures = getattr(self.parent, self._fixtures)(self.parent)
        else:
            self.fixtures = self._fixtures(self.parent)
        self.fixtures.setUp()
        return self.fixtures

    def _fixtures_teardown(self):
        self.fixtures.tearDown()


class WithFixtures(object):

    def __init__(self, *args, **kwargs):
        self.fixtures = FixtureContext(*args, **kwargs)

    def __call__(self, func):
        def wrapper(objself, *args, **kwargs):
            self.fixtures.parent = objself
            with self.fixtures as fixtures:
                kwargs['fixtures'] = fixtures
                return func(objself, *args, **kwargs)
        return wrapper
