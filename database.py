import json
import random
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "simulator.db"
CLOUDCERTPREP_DIR = ROOT / "question_bank" / "cloudcertprep" / "clf-c02"
CLOUDCERTPREP_PT_DIR = ROOT / "question_bank" / "cloudcertprep" / "clf-c02-pt"
CLOUDCERTPREP_URL = "https://github.com/nastaso/cloudcertprep"
DOMAINS = ["Conceitos de Nuvem", "Segurança e Conformidade", "Tecnologia e Serviços", "Cobrança, Preços e Suporte"]
WEIGHTS = {DOMAINS[0]: .24, DOMAINS[1]: .30, DOMAINS[2]: .34, DOMAINS[3]: .12}

def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS questions (
          id INTEGER PRIMARY KEY, domain TEXT NOT NULL, topic TEXT NOT NULL,
          prompt TEXT NOT NULL, choices TEXT NOT NULL, correct TEXT NOT NULL,
          explanation TEXT NOT NULL, reference_url TEXT NOT NULL, reference_title TEXT NOT NULL,
          multi INTEGER NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1,
          source_name TEXT NOT NULL DEFAULT 'Autoral', source_key TEXT
        );
        CREATE TABLE IF NOT EXISTS attempts (
          id INTEGER PRIMARY KEY, kind TEXT NOT NULL, started_at TEXT NOT NULL, submitted_at TEXT,
          duration_seconds INTEGER, total INTEGER NOT NULL, correct_count INTEGER, score REAL
        );
        CREATE TABLE IF NOT EXISTS answers (
          id INTEGER PRIMARY KEY, attempt_id INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
          question_id INTEGER NOT NULL REFERENCES questions(id), selected TEXT NOT NULL,
          was_correct INTEGER NOT NULL, answered_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_answers_question ON answers(question_id);
        CREATE INDEX IF NOT EXISTS idx_questions_domain ON questions(domain);
        """)
        # Compatibilidade com bancos já criados antes de a origem ser registrada.
        existing = {r[1] for r in c.execute("PRAGMA table_info(questions)")}
        if "source_name" not in existing:
            c.execute("ALTER TABLE questions ADD COLUMN source_name TEXT NOT NULL DEFAULT 'Autoral'")
        if "source_key" not in existing:
            c.execute("ALTER TABLE questions ADD COLUMN source_key TEXT")
        # Texto original em inglês das questões traduzidas (vazio nas autorais).
        for column in ("prompt_en", "choices_en", "explanation_en"):
            if column not in existing:
                c.execute(f"ALTER TABLE questions ADD COLUMN {column} TEXT")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_questions_source_key ON questions(source_key) WHERE source_key IS NOT NULL")
    from seed_questions import seed
    seed()
    import_cloudcertprep()
    apply_translations()

def import_cloudcertprep():
    """Importa o banco CLF-C02 distribuído sob MIT e preserva sua procedência."""
    files = [
        ("domain1.json", DOMAINS[0]),
        ("domain2.json", DOMAINS[1]),
        ("domain3.json", DOMAINS[2]),
        ("domain4.json", DOMAINS[3]),
    ]
    if not all((CLOUDCERTPREP_DIR / file).exists() for file, _ in files):
        return
    with connect() as c:
        for filename, domain in files:
            entries = json.loads((CLOUDCERTPREP_DIR / filename).read_text(encoding="utf-8"))
            for entry in entries:
                source_key = f"cloudcertprep:clf-c02:{entry['id']}"
                if c.execute("SELECT 1 FROM questions WHERE source_key=?", (source_key,)).fetchone():
                    continue
                answer = entry["answer"] if isinstance(entry["answer"], list) else [entry["answer"]]
                services = ", ".join(entry.get("services", []))
                topic = services or f"Objetivo CLF-C02 {entry.get('taskStatement', 'geral')}"
                c.execute("""INSERT INTO questions(
                    domain,topic,prompt,choices,correct,explanation,reference_url,reference_title,multi,source_name,source_key
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""", (
                    domain, topic, entry["question"], json.dumps(entry["options"]), json.dumps(answer),
                    entry["explanation"], CLOUDCERTPREP_URL, "CloudCertPrep — fonte MIT",
                    int(entry.get("isMultiAnswer", False)), "CloudCertPrep (MIT)", source_key,
                ))

def apply_translations():
    """Troca o texto das questões importadas pela tradução em português.

    O original vai para as colunas *_en. Só atualiza questões ainda não
    traduzidas, então roda rápido e funciona em bancos já existentes sem
    perder o histórico de respostas (ligado ao id da questão)."""
    if not CLOUDCERTPREP_PT_DIR.exists():
        return
    with connect() as c:
        pending = {r["source_key"] for r in c.execute(
            "SELECT source_key FROM questions WHERE source_key LIKE 'cloudcertprep:%' AND prompt_en IS NULL")}
        if not pending:
            return
        for path in sorted(CLOUDCERTPREP_PT_DIR.glob("domain*.json")):
            for entry in json.loads(path.read_text(encoding="utf-8")):
                source_key = f"cloudcertprep:clf-c02:{entry['id']}"
                if source_key not in pending:
                    continue
                c.execute("""UPDATE questions SET prompt_en=prompt, choices_en=choices, explanation_en=explanation,
                    prompt=?, choices=?, explanation=? WHERE source_key=? AND prompt_en IS NULL""", (
                    entry["question"], json.dumps(entry["options"], ensure_ascii=False), entry["explanation"], source_key,
                ))

def _rows_to_questions(rows):
    questions = []
    for row in rows:
        question = dict(row)
        question["choices"] = json.loads(question["choices"])
        question["correct"] = json.loads(question["correct"])
        if question.get("choices_en"):
            question["choices_en"] = json.loads(question["choices_en"])
        # `selected` só existe nas consultas de revisão. É armazenado como JSON
        # para permitir respostas múltiplas, portanto precisa ser desserializado.
        if "selected" in question:
            question["selected"] = json.loads(question["selected"])
        questions.append(question)
    return questions

def choose_questions(count):
    """Allocate by official weights, then favor weak / not-recent material."""
    with connect() as c:
        qs = _rows_to_questions(c.execute("SELECT * FROM questions WHERE active=1").fetchall())
        history = c.execute("""SELECT a.question_id, a.was_correct, q.domain, q.topic, a.answered_at
            FROM answers a JOIN questions q ON q.id=a.question_id ORDER BY a.id DESC""").fetchall()
    recent = {r["question_id"] for r in history[:min(100, len(history))]}
    performance = defaultdict(lambda: [0, 0])
    for r in history:
        key = (r["domain"], r["topic"])
        performance[key][0] += r["was_correct"]; performance[key][1] += 1
    buckets = defaultdict(list)
    for q in qs: buckets[q["domain"]].append(q)
    raw = {d: count * WEIGHTS[d] for d in DOMAINS}
    allocation = {d: int(raw[d]) for d in DOMAINS}
    for d in sorted(DOMAINS, key=lambda x: raw[x]-allocation[x], reverse=True)[:count-sum(allocation.values())]: allocation[d] += 1
    selected = []
    for domain, needed in allocation.items():
        pool = buckets[domain][:]
        def priority(q):
            good, total = performance[(q["domain"], q["topic"])]
            accuracy = good / total if total else .65
            weak_bonus = (1 - accuracy) * 5 if total else 1
            fresh_bonus = -8 if q["id"] in recent else 0
            return weak_bonus + fresh_bonus + random.random()
        pool.sort(key=priority, reverse=True)
        # if a small seed is exhausted, it cycles only after all available items get a chance
        selected.extend(pool[:needed] if len(pool) >= needed else [pool[i % len(pool)] for i in range(needed)])
    random.shuffle(selected)
    return selected

def create_attempt(kind, total):
    with connect() as c:
        cur = c.execute("INSERT INTO attempts(kind,started_at,total) VALUES(?,?,?)", (kind, now(), total))
        return cur.lastrowid

def submit_attempt(attempt_id, responses, duration):
    with connect() as c:
        questions = _rows_to_questions(c.execute("SELECT * FROM questions WHERE id IN (%s)" % ",".join("?"*len(responses)), list(responses)).fetchall())
        by_id = {q["id"]: q for q in questions}; correct_count = 0
        for qid, selected in responses.items():
            selected = sorted(selected); ok = selected == sorted(by_id[qid]["correct"]); correct_count += ok
            c.execute("INSERT INTO answers(attempt_id,question_id,selected,was_correct,answered_at) VALUES(?,?,?,?,?)", (attempt_id, qid, json.dumps(selected), int(ok), now()))
        total = len(responses); score = round(100 * correct_count / total, 1) if total else 0
        c.execute("UPDATE attempts SET submitted_at=?,duration_seconds=?,correct_count=?,score=? WHERE id=?", (now(), int(duration), correct_count, score, attempt_id))
    return correct_count, score

def now(): return datetime.now(timezone.utc).isoformat()

def summary():
    with connect() as c:
        attempts = c.execute("SELECT * FROM attempts WHERE submitted_at IS NOT NULL ORDER BY id DESC").fetchall()
        domain = c.execute("""SELECT q.domain, COUNT(*) total, SUM(a.was_correct) correct
          FROM answers a JOIN questions q ON q.id=a.question_id GROUP BY q.domain""").fetchall()
        errors = c.execute("""SELECT q.id,q.prompt,q.domain,q.topic,q.choices,q.correct,q.explanation,q.reference_url,q.reference_title,q.source_name,
          q.prompt_en,q.choices_en,q.explanation_en,a.selected,a.answered_at FROM answers a JOIN questions q ON q.id=a.question_id
          WHERE a.was_correct=0 ORDER BY a.id DESC LIMIT 50""").fetchall()
    streak=0
    for a in attempts:
        if a["score"] >= 80: streak += 1
        else: break
    return attempts, domain, _rows_to_questions(errors), streak

def attempt_detail(attempt_id):
    with connect() as c:
        attempt = c.execute("SELECT * FROM attempts WHERE id=?", (attempt_id,)).fetchone()
        rows = c.execute("""SELECT q.*,a.selected,a.was_correct FROM answers a JOIN questions q ON q.id=a.question_id
         WHERE a.attempt_id=? ORDER BY a.id""", (attempt_id,)).fetchall()
    return attempt, _rows_to_questions(rows)
