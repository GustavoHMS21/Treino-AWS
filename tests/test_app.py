import unittest

from streamlit.testing.v1 import AppTest

import database as db
from tests.helpers import TempDatabase

PAGES = ["Dashboard", "Flashcards", "Caderno de erros", "Guia de estudo", "Histórico e revisão"]


def button(at, label):
    return next(b for b in at.button if b.label.startswith(label))


class AppSmokeTest(TempDatabase):
    def run_app(self):
        at = AppTest.from_file("../app.py", default_timeout=30).run()
        self.assertFalse(at.exception, at.exception)
        return at

    def test_every_page_renders(self):
        at = self.run_app()
        for page in PAGES:
            at.sidebar.radio[0].set_value(page).run()
            self.assertFalse(at.exception, (page, at.exception))

    def test_exam_wrong_answer_note_and_reinforcement(self):
        at = self.run_app()
        button(at, "Iniciar diário").click().run()
        self.assertEqual(at.title[0].value, "Diário · 20 questões")
        button(at, "Enviar simulado").click().run()  # nada respondido: 20 erros
        self.assertEqual(at.title[0].value, "Resultado")
        at.text_input[0].set_value("cenário de teste")
        at.text_input[2].set_value("pista certa")
        button(at, "Salvar no caderno").click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(len(db.notes()), 1)
        button(at, "Voltar ao dashboard").click().run()
        self.assertEqual(len(db.reinforcement_ids()), 20)
        button(at, "Reforço · 20 questões").click().run()
        self.assertEqual(at.title[0].value, f"{db.REINFORCEMENT} · 20 questões")

    def test_flashcard_session(self):
        at = self.run_app()
        at.sidebar.radio[0].set_value("Flashcards").run()
        at.selectbox[0].set_value("Planos de suporte").run()
        button(at, "Começar sessão").click().run()
        button(at, "Mostrar resposta").click().run()
        button(at, "✅ Sabia").click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(len(db.flashcard_progress()), 1)


if __name__ == "__main__":
    unittest.main()
