import json
import unittest

from database import CLOUDCERTPREP_DIR, CLOUDCERTPREP_PT_DIR
from study_content import GROUPS, all_cards


class TranslationTest(unittest.TestCase):
    def test_translation_matches_original(self):
        for original in sorted(CLOUDCERTPREP_DIR.glob("domain*.json")):
            en = {e["id"]: e for e in json.loads(original.read_text(encoding="utf-8"))}
            pt = {e["id"]: e for e in json.loads((CLOUDCERTPREP_PT_DIR / original.name).read_text(encoding="utf-8"))}
            self.assertEqual(en.keys(), pt.keys(), original.name)
            for qid, entry in en.items():
                with self.subTest(file=original.name, id=qid):
                    self.assertEqual(entry["options"].keys(), pt[qid]["options"].keys())
                    self.assertTrue(pt[qid]["question"].strip())
                    self.assertTrue(pt[qid]["explanation"].strip())


class StudyContentTest(unittest.TestCase):
    def test_card_ids_are_unique(self):
        ids = [c["id"] for c in all_cards()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_rows_are_complete(self):
        for group, tip, rows in GROUPS:
            self.assertTrue(tip, group)
            for service, use, _ in rows:
                self.assertTrue(service and use, (group, service))


if __name__ == "__main__":
    unittest.main()
