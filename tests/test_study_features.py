import unittest
from datetime import datetime, timedelta, timezone

import database as db
from tests.helpers import TempDatabase


def answer(question, right):
    """Responde a uma questão num simulado de uma questão só."""
    wrong = next(k for k in question["choices"] if k not in question["correct"])
    aid = db.create_attempt("Diário", 1)
    db.submit_attempt(aid, {question["id"]: question["correct"] if right else [wrong]}, 10)


def days_until(due_at):
    return round((datetime.fromisoformat(due_at) - datetime.now(timezone.utc)) / timedelta(days=1))


class ReinforcementTest(TempDatabase):
    def test_only_questions_still_wrong(self):
        a, b = db.choose_questions(2)
        answer(a, False); answer(b, False)
        answer(b, True)  # corrigida depois: sai do reforço
        self.assertEqual(db.reinforcement_ids(), [a["id"]])
        self.assertEqual([q["id"] for q in db.choose_reinforcement(20)], [a["id"]])

    def test_reinforcement_ignored_by_streak_and_readiness(self):
        q = db.choose_questions(1)[0]
        aid = db.create_attempt(db.REINFORCEMENT, 1)
        db.submit_attempt(aid, {q["id"]: q["correct"]}, 10)
        attempts, _, _, streak = db.summary()
        self.assertEqual(streak, 0)
        self.assertEqual(db.readiness(attempts), (0, 0))


class FlashcardTest(TempDatabase):
    def test_leitner_intervals(self):
        for expected in db.REVIEW_INTERVALS + [db.REVIEW_INTERVALS[-1]]:
            db.review_flashcard("g::s", True)
            self.assertEqual(days_until(db.flashcard_progress()["g::s"]["due_at"]), expected)
        db.review_flashcard("g::s", False)
        progress = db.flashcard_progress()["g::s"]
        self.assertEqual(progress["box"], 0)
        self.assertEqual(days_until(progress["due_at"]), 1)


class NotebookTest(TempDatabase):
    def test_save_review_and_delete(self):
        q = db.choose_questions(1)[0]
        db.save_note(q["id"], " cenário ", "marquei X", "era Y")
        note = db.get_note(q["id"])
        self.assertEqual(note["cue"], "cenário")
        self.assertEqual(days_until(note["due_at"]), 1)
        self.assertFalse(db.is_due(note["due_at"]))
        db.review_note(q["id"], True)
        self.assertEqual(days_until(db.get_note(q["id"])["due_at"]), 3)
        # Editar o texto não reinicia o agendamento.
        db.save_note(q["id"], "cenário", "marquei X", "era Y, pista Z")
        self.assertEqual(db.get_note(q["id"])["box"], 1)
        self.assertEqual(db.notes()[0]["prompt"], q["prompt"])
        db.delete_note(q["id"])
        self.assertIsNone(db.get_note(q["id"]))


if __name__ == "__main__":
    unittest.main()
