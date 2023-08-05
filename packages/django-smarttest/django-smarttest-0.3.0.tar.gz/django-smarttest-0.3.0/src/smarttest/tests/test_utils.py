from mock import sentinel, patch, call

from django.test import SimpleTestCase

from smarttest.utils import load_all_modules


class LoadAllModulesTest(SimpleTestCase):

    """
    :py:meth:`smarttest.utils.load_all_modules`
    """

    @patch('os.walk')
    @patch('importlib.import_module')
    def test_should_import_all_modules(self, import_module, walk):

        walk.return_value = [
            ('module', [], ['file1.py', 'file2.py']),
            ('module/submodule', [], ['file3.py', 'file4.py']),
        ]

        load_all_modules(sentinel.directory)

        import_module.assert_has_calls([
            call('module.file1'),
            call('module.file2'),
            call('module.submodule.file3'),
            call('module.submodule.file4'),
        ])

    @patch('os.walk')
    @patch('importlib.import_module')
    def test_should_not_import_modules_from_ignored_dirs(self, import_module, walk):

        ignore_dirs = ['migrations']
        walk.return_value = [
            ('module', [], ['file1.py', 'file2.py']),
            ('module/migrations', [], ['file3.py', 'file4.py']),
        ]

        load_all_modules(sentinel.directory, ignore_dirs=ignore_dirs)

        import_module.assert_has_calls([
            call('module.file1'),
            call('module.file2'),
        ])

    @patch('os.walk')
    @patch('importlib.import_module')
    def test_should_not_import_not_py_files(self, import_module, walk):

        walk.return_value = [
            ('module', [], ['file1.py', 'file2.py']),
            ('module/submodule', [], ['file3.py', 'file4.txt']),
        ]

        load_all_modules(sentinel.directory)

        import_module.assert_has_calls([
            call('module.file1'),
            call('module.file2'),
            call('module.submodule.file3'),
        ])

    @patch('os.walk')
    @patch('importlib.import_module')
    @patch('smarttest.utils.log')
    def test_should_ignore_not_importing_modules(self, log, import_module, walk):

        import_module.side_effect = ImportError
        walk.return_value = [
            ('module', [], ['file1.py', 'file2.py']),
            ('module/submodule', [], ['file3.py', 'file4.txt']),
        ]

        load_all_modules(sentinel.directory)

        self.assertTrue(log.warning.called)
