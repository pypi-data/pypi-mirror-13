import os

from PyHardLinkBackup.backup_app.models import BackupRun, BackupEntry
from PyHardLinkBackup.phlb.config import phlb_config
from PyHardLinkBackup.tests.base import BaseTestCase, \
    BaseWithSourceFilesTestCase, BaseCreatedOneBackupsTestCase, \
    BaseCreatedTwoBackupsTestCase
from PyHardLinkBackup.tests.utils import UnittestFileSystemHelper


class TestUnittestSetup(BaseTestCase):
    def test_ini_created(self):
        self.assertTrue(os.path.isfile(self.ini_path))

    def test_unittests_settings_active(self):
        self.assertEqual(phlb_config.database_name, ":memory:")
        self.assertEqual(phlb_config.sub_dir_formatter, "%Y-%m-%d-%H%M%S.%f")



class TestBaseBackup(BaseWithSourceFilesTestCase):
    def test_created_source_files(self):
        """
        Check if the test source files are created
        """
        fs_helper = UnittestFileSystemHelper()
        tree_list = fs_helper.pformat_tree(self.source_path, with_timestamps=True)
        # print("\n".join(tree_list))
        # pprint.pprint(tree_list,indent=0, width=200)
        self.assertEqual(tree_list, [
            self.source_path,
            'root_file_A.txt                F 19730710:001151 - The root file A content.',
            'root_file_B.txt                F 19730710:001151 - The root file B content.',
            'sub dir A                      D 19730710:001151',
            'sub dir A/dir_A_file_A.txt     F 19730710:001151 - File A in sub dir A.',
            'sub dir A/dir_A_file_B.txt     F 19730710:001151 - File B in sub dir A.',
            'sub dir B                      D 19730710:001151',
            'sub dir B/sub_file.txt         F 19730710:001151 - File in sub dir B.'
        ])


class TestBaseCreatedOneBackupsTestCase(BaseCreatedOneBackupsTestCase):
    #def test_database_entries(self):
    #    self.assertEqual(BackupRun.objects.all().count(), 1)

    def test_first_backup_run(self):
        self.assert_click_exception(self.first_backup_result)
        print(self.first_backup_result.output)
        
        self.assertIn("PyHardLinkBackup", self.first_backup_result.output)
        self.assertIn("scanned 5 files", self.first_backup_result.output)
        self.assertIn("106 Bytes in 5 files to backup.", self.first_backup_result.output)

        self.assertIn("Backup done:", self.first_backup_result.output)
        self.assertIn("Source file sizes: 106 Bytes", self.first_backup_result.output)
        self.assertIn("new content to saved: 5 files (106 Bytes 100.0%)", self.first_backup_result.output)
        self.assertIn("stint space via hardlinks: 0 files (0 Bytes 0.0%)", self.first_backup_result.output)

        self.assertEqual(os.listdir(self.backup_path), ["source unittests files"])
        self.assert_backup_fs_count(1)

        self.assertIn(self.first_run_path, self.first_backup_result.output)

        self.assert_first_backup()

    def test_database_entries(self):
        """
        Check models.BackupEntry
         * assert all entries exist in filesystem
         * assert entry count

        Here we have 5 files in one backup run
        """
        self.assert_database_backup_entries(count=5)


class TestBaseCreatedTwoBackupsTestCase(BaseCreatedTwoBackupsTestCase):

    def test_first_backup_run(self):
        self.assert_first_backup()

    def test_second_backup_run(self):
        self.assert_click_exception(self.second_backup_result)
        print(self.second_backup_result.output)
      
        self.assertIn("106 Bytes in 5 files to backup.", self.second_backup_result.output)
        self.assertIn("new content to saved: 0 files (0 Bytes 0.0%)", self.second_backup_result.output)
        self.assertIn("stint space via hardlinks: 5 files (106 Bytes 100.0%)", self.second_backup_result.output)

        self.assertEqual(os.listdir(self.backup_path), ["source unittests files"])
        self.assert_backup_fs_count(2)

        self.assertIn(self.second_run_path, self.second_backup_result.output)

        self.assert_second_backup()

    def test_database_entries(self):
        """
        Check models.BackupEntry
         * assert all entries exist in filesystem
         * assert entry count

        Here we have 5 files in two backup runs
        """
        self.assert_database_backup_entries(count=10)