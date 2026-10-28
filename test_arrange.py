#!/usr/bin/env python3
"""
===============================================================================
FolderWatchNArrange - Test Suite
Author: lalitaalaalitah
Website: https://www.lalitaalaalitah.com
GitHub: https://github.com/lalitaalaalitah
===============================================================================
"""

import os
import time
import json
import tempfile
import unittest
from pathlib import Path

from folder_watch_n_arrange import ArrangeEngine, get_current_mounts, __version__


class TestFolderWatchNArrange(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.test_dir.name)
        self.cfg_file = self.tmp / "rules.json"
        self.hist_file = self.tmp / "history.json"
        self.src_dir = self.tmp / "source"
        self.dest_dir = self.tmp / "dest"
        self.src_dir.mkdir()
        self.dest_dir.mkdir()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_version_string(self):
        self.assertTrue(isinstance(__version__, str))
        self.assertEqual(__version__, "1.1.0")

    def test_copy_action_and_history_dedup(self):
        sample_file = self.src_dir / "PHOTO_001.JPG"
        sample_file.write_text("dummy photo content")
        past = time.time() - 5
        os.utime(sample_file, (past, past))

        rules = [
            {
                "name": "Copy Photos",
                "sources": [str(self.src_dir)],
                "extensions": [".jpg"],
                "action": "copy",
                "destination": str(self.dest_dir / "Photos" / "{year}"),
                "on_conflict": "rename",
            }
        ]
        with open(self.cfg_file, "w") as f:
            json.dump(rules, f)

        engine = ArrangeEngine(config_path=self.cfg_file, history_path=self.hist_file)
        processed = engine.run_cycle(rules, dry_run=False)
        self.assertEqual(processed, 1)

        dest_files = list((self.dest_dir / "Photos").rglob("*.JPG"))
        self.assertEqual(len(dest_files), 1)
        self.assertTrue(sample_file.exists())

        processed_again = engine.run_cycle(rules, dry_run=False)
        self.assertEqual(processed_again, 0)

    def test_move_action(self):
        sample_doc = self.src_dir / "test.pdf"
        sample_doc.write_text("pdf document")
        past = time.time() - 5
        os.utime(sample_doc, (past, past))

        rules = [
            {
                "name": "Move PDFs",
                "sources": [str(self.src_dir)],
                "extensions": [".pdf"],
                "action": "move",
                "destination": str(self.dest_dir / "Documents"),
                "on_conflict": "rename",
            }
        ]

        engine = ArrangeEngine(config_path=self.cfg_file, history_path=self.hist_file)
        processed = engine.run_cycle(rules, dry_run=False)
        self.assertEqual(processed, 1)

        self.assertFalse(sample_doc.exists())
        self.assertTrue((self.dest_dir / "Documents" / "test.pdf").is_file())

    def test_conflict_rename(self):
        doc1 = self.src_dir / "file.txt"
        doc1.write_text("first version")
        past = time.time() - 5
        os.utime(doc1, (past, past))

        existing_dest = self.dest_dir / "Notes" / "file.txt"
        existing_dest.parent.mkdir(parents=True)
        existing_dest.write_text("existing version")

        rules = [
            {
                "name": "Move Notes",
                "sources": [str(self.src_dir)],
                "extensions": [".txt"],
                "action": "move",
                "destination": str(self.dest_dir / "Notes"),
                "on_conflict": "rename",
            }
        ]

        engine = ArrangeEngine(config_path=self.cfg_file, history_path=self.hist_file)
        processed = engine.run_cycle(rules, dry_run=False)
        self.assertEqual(processed, 1)

        self.assertTrue(existing_dest.is_file())
        renamed_dest = self.dest_dir / "Notes" / "file_1.txt"
        self.assertTrue(renamed_dest.is_file())

    def test_mount_detection(self):
        mounts = get_current_mounts()
        self.assertIsInstance(mounts, set)


if __name__ == "__main__":
    unittest.main()
