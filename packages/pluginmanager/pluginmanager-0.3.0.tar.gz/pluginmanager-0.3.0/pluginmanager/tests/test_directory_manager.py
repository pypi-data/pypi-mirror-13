import unittest
from .compat import tempfile
from pluginmanager.directory_manager import DirectoryManager


class TestDirectoryManager(unittest.TestCase):
    def setUp(self):
        """
        create the directory manager as well as
        a temp directory and a nested temporary directory inside
        of the temp directory
        """
        self.directory_manager = DirectoryManager()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.nested_dir = tempfile.TemporaryDirectory(dir=self.temp_dir.name)

    def tearDown(self):
        """
        clean up the two created temporary directories
        """
        self.nested_dir.cleanup()
        self.temp_dir.cleanup()

    def test_add_directory(self):
        """
        Add the dir `self.temp_dir` and then check to make sure
        it is in the `plugin_directories`
        """
        self.directory_manager.add_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name,
                      self.directory_manager.plugin_directories)

    def test_set_directory(self):
        """
        Add in the `temp_dir` and then set the `nested_dir`.
        Assert that the `nested_dir` is in the `plugin_directories`
        and assert that the `temp_dir` is not.
        """
        self.directory_manager.add_directories(self.temp_dir.name)
        self.directory_manager.set_directories(self.nested_dir.name)
        self.assertIn(self.nested_dir.name,
                      self.directory_manager.plugin_directories)

        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

    def test_set_directories_except_blacklisted(self):
        """
        add `temp_dir` to the blacklisted dirs and then try
        to set it. Assert that `temp_dir` is not in the plugin directories.

        Then, change `except_blacklisted` to false and set the blacklisted dir.
        Assert that it is in the plugin directories.
        """
        self.directory_manager.add_blacklisted_directories(self.temp_dir.name)
        self.directory_manager.set_directories(self.temp_dir.name)
        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

        self.directory_manager.set_directories(self.temp_dir.name,
                                               except_blacklisted=False)

        self.assertIn(self.temp_dir.name,
                      self.directory_manager.plugin_directories)

    def test_add_directories_except_blacklisted(self):
        """
        add `temp_dir` to the blacklisted dirs and then try
        to add it. Assert that `temp_dir` is not in the plugin directories.

        Then, change `except_blacklisted` to false and add in the blacklisted
        dir.

        Assert that it is in the plugin directories.
        """
        self.directory_manager.add_blacklisted_directories(self.temp_dir.name)
        self.directory_manager.add_directories(self.temp_dir.name)
        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

        self.directory_manager.add_directories(self.temp_dir.name,
                                               except_blacklisted=False)

        self.assertIn(self.temp_dir.name,
                      self.directory_manager.plugin_directories)

    def test_add_site_packages(self):
        self.directory_manager.add_site_packages_paths()
        self.assertEqual(len(self.directory_manager.plugin_directories), 1)

    def test_remove_directories(self):
        """
        Add in and then remove a directory. Assert that the directory has
        been removed.
        """
        self.directory_manager.add_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name,
                      self.directory_manager.plugin_directories)

        self.directory_manager.remove_directories(self.temp_dir.name)
        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

    def test_collect_directories_with_recursion(self):
        """
        collect directories from `temp_dir`, which has a nested
        directory in it. Make sure the nested dir is collected,
        the return type is a `set` and that only those two dirs
        are returned.
        """
        dir_manager = self.directory_manager
        directories = dir_manager.collect_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name, directories)
        self.assertIn(self.nested_dir.name, directories)
        self.assertEqual(len(directories), 2)
        self.assertTrue(isinstance(directories, set))

    def test_set_blacklisted_directories(self):
        """
        Need to check that the `remove_from_stored_directories` arg is working.
        Add the temp dir to the plugin directories first before setting the
        blacklisted dirs to be equal to `temp_dir`. Check to see if
        `blacklisted_directories` contains `temp_dir` and then check to see
        that temp_dir is not in `plugin_directories`.
        """
        self.directory_manager.add_directories(self.temp_dir.name)
        self.directory_manager.set_blacklisted_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name,
                      self.directory_manager.blacklisted_directories)

        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

        self.directory_manager.blacklisted_directories = set()
        self.directory_manager.add_directories(self.temp_dir.name)
        self.directory_manager.set_blacklisted_directories(self.temp_dir.name,
                                                           False)

        self.assertIn(self.temp_dir.name,
                      self.directory_manager.plugin_directories)

    def test_add_blacklisted_directories(self):
        """
        Need to check that the `remove_from_stored_directories` arg is working.
        Add the temp dir to the plugin directories first before adding the
        `temp_dir` to blacklisted directories. Check to see if
        `blacklisted_directories` contains `temp_dir` and then check to see
        that temp_dir is not in `plugin_directories`.
        """
        self.directory_manager.add_directories(self.temp_dir.name)
        self.directory_manager.add_blacklisted_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name,
                      self.directory_manager.blacklisted_directories)

        self.assertNotIn(self.temp_dir.name,
                         self.directory_manager.plugin_directories)

        self.directory_manager.blacklisted_directories = set()
        self.directory_manager.add_directories(self.temp_dir.name)
        self.directory_manager.add_blacklisted_directories(self.temp_dir.name,
                                                           False)

    def test_get_blacklisted_directories(self):
        """
        check to make sure that blacklisted dirs are a set
        """
        black_dirs = self.directory_manager.get_blacklisted_directories()
        self.assertTrue(isinstance(black_dirs, set))
        self.assertEqual(len(black_dirs), 0)

    def test_collect_directories_not_recursive(self):
        """
        collect directories from `temp_dir`, which has a nested
        directory in it. Make sure the nested dir is NOT collected,
        the return type is a `set` and that only one directory is
        returned.
        """
        self.directory_manager.recursive = False
        dir_manager = self.directory_manager
        directories = dir_manager.collect_directories(self.temp_dir.name)
        self.assertIn(self.temp_dir.name, directories)
        self.assertEqual(len(directories), 1)
        self.assertTrue(isinstance(directories, set))

    def test_collect_directories_with_blacklisted_dir(self):
        """
        add in the `nested_dir` to the blacklisted directories.
        Collect the directories with recursion on and make sure that
        the `nested_dir` is not collected.
        """
        dir_manager = self.directory_manager
        dir_manager.add_blacklisted_directories(self.nested_dir.name)
        directories = dir_manager.collect_directories(self.temp_dir.name)
        self.assertNotIn(self.nested_dir.name, directories)
        self.assertIn(self.temp_dir.name, directories)


if __name__ == '__main__':
    unittest.main()
