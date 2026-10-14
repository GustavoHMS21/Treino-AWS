import random
import time
import streamlit as st
import pandas as pd
from database import (DOMAINS, REINFORCEMENT, READY_EXAMS, init_db, choose_questions, choose_reinforcement, reinforcement_ids,
                      create_attempt, submit_attempt, summary, attempt_detail, readiness, flashcard_progress, review_flashcard,
                      get_note, save_note, delete_note, review_note, notes, is_due)
from study_content import GROUPS, STUDY_SOURCES, all_cards

st.set_page_config(page_title="Simulador AWS CLF-C02", page_icon="☁️", layout="wide")
init_db()

PAGES = ["Dashboard", "Flashcards", "Caderno de erros", "Guia de estudo", "Histórico e revisão"]
SECONDS_PER_QUESTION = 90  # ritmo da prova real: 90 min para 65 questões, arredondado para cima
SESSION_SIZE = 20

def pct(v): return f"{v:.0f}%" if v is not None else "—"
def duration_text(seconds):
    seconds=int(seconds or 0); return f"{seconds//60}min {seconds%60:02d}s"
def go(page): st.session_state.page = page

def option_text(question, keys):
    """Apresenta letra e conteúdo, inclusive em questões de múltipla escolha."""
    if not keys:
        return "Não respondida"
    choices = question.get("choices", {}) if isinstance(question, dict) else {}
    if not isinstance(choices, dict):
        choices = {}
    return " · ".join(f"{key}. {choices.get(key, 'Alternativa indisponível')}" for key in keys)

def has_original(q): return bool(q.get("prompt_en"))

def in_english(q, english):
    """Versão da questão no idioma pedido. Questões autorais só existem em português."""
    if not (english and has_original(q)):
        return q
    return {**q, "prompt": q["prompt_en"], "choices": q["choices_en"], "explanation": q["explanation_en"]}

def view(q): return in_english(q, st.session_state.get("english", False))

def other_language(q, key, with_explanation=False):
    """Botão que abre a mesma questão no outro idioma, para tirar dúvida de tradução."""
    if not has_original(q):
        return
    english = st.session_state.get("english", False)
    alt = in_english(q, not english)
    with st.popover("🇧🇷 Ver em português" if english else "🇺🇸 Ver original em inglês", key=key):
        st.markdown(f"**{alt['prompt']}**")
        for letter, text in alt["choices"].items():
            st.markdown(f"{letter}. {text}")
        if with_explanation:
            st.caption(alt["explanation"])

def note_editor(question_id, key):
    """Formulário do caderno de erros: as três perguntas que fixam o motivo do erro."""
    note = get_note(question_id) or {}
    with st.form(f"note_{key}"):
        st.markdown("**📓 Caderno de erros**" + (" · anotação salva" if note else ""))
        cue = st.text_input("O que a questão pedia (palavra-chave do cenário)", note.get("cue", ""),
                            placeholder="Ex.: detectar atividade suspeita na conta")
        mistake = st.text_input("O que marquei e por que estava errado", note.get("mistake", ""),
                                placeholder="Ex.: Inspector, mas ele procura vulnerabilidades, não ameaças")
        clue = st.text_input("Qual era o certo e qual pista apontava para ele", note.get("clue", ""),
                             placeholder="Ex.: GuardDuty; 'atividade suspeita' = ameaça")
        if st.form_submit_button("Salvar no caderno"):
            if cue.strip() and clue.strip():
                save_note(question_id, cue, mistake, clue); st.success("Salvo. A primeira revisão fica para amanhã.")
            else:
                st.warning("Preencha pelo menos o cenário e a pista da resposta certa.")

def review(q, key):
    """Bloco de correção usado no resultado e no histórico."""
    shown = view(q)
    st.write(shown['prompt'])
    st.error(f"Sua resposta: {option_text(shown, q['selected'])}")
    st.success(f"Resposta correta: {option_text(shown, q['correct'])}")
    st.info(f"Por que esta é a resposta correta: {shown['explanation']}")
    other_language(q, key, with_explanation=True)
    st.markdown(f"Fonte: [{q['reference_title']}]({q['reference_url']}) · Origem: {q['source_name']}")
    if not q.get('was_correct', 0):
        note_editor(q['id'], key)

def due_flashcards():
    progress = flashcard_progress()
    return [c for c in all_cards() if c['id'] not in progress or is_due(progress[c['id']]['due_at'])]

def dashboard():
    attempts, domain_rows, errors, streak = summary()
    exams=[a for a in attempts if a['kind']!=REINFORCEMENT]
    st.title("☁️ Simulador AWS Cloud Practitioner")
    st.caption("CLF-C02 · questões autorais para estudo · dados salvos apenas neste computador")
    overall = sum(a['correct_count'] for a in exams) / sum(a['total'] for a in exams) * 100 if exams else 0
    ready, full = readiness(attempts)
    a,b,c,d=st.columns(4); a.metric("Desempenho geral", pct(overall), "Meta: 80%")
    b.metric("Simulados concluídos", len(attempts)); c.metric("Sequência ≥80%", streak)
    d.metric("Prontidão", f"{ready} de {READY_EXAMS}", help=f"Simulados completos com 80% ou mais entre os {READY_EXAMS} últimos. Com {READY_EXAMS} de {READY_EXAMS}, você está pronto para agendar a prova.")
    if ready==READY_EXAMS: st.success(f"Seus {READY_EXAMS} últimos simulados completos ficaram em 80% ou mais: você está pronto para agendar a prova.")
    st.progress(min(overall/100,1.0), text=f"Meta visual: {pct(overall)} de 80%")

    st.subheader("Plano de hoje")
    cards=len(due_flashcards()); notes_due=sum(is_due(n['due_at']) for n in notes()); pending=len(reinforcement_ids())
    x,y,z=st.columns(3)
    x.metric("Flashcards para revisar", cards); x.button("Abrir flashcards", on_click=go, args=("Flashcards",), width="stretch", disabled=not cards)
    y.metric("Anotações para revisar", notes_due); y.button("Abrir caderno de erros", on_click=go, args=("Caderno de erros",), width="stretch", disabled=not notes_due)
    z.metric("Erros ainda não corrigidos", pending)
    n=min(pending,SESSION_SIZE)
    if z.button(f"Reforço · {n} questões · {n*SECONDS_PER_QUESTION//60} min" if n else "Reforço · sem erros pendentes", width="stretch", disabled=not n):
        start(REINFORCEMENT,n,n*SECONDS_PER_QUESTION,choose_reinforcement(n))
    st.caption("Rotina sugerida: um simulado diário revisando todos os erros, os flashcards e as anotações que vencerem, e um simulado completo por semana.")

    st.subheader("Novo simulado")
    x,y=st.columns(2)
    if x.button("Iniciar diário · 20 questões · 30 min", width="stretch"): start("Diário",20,30*60)
    if y.button("Iniciar completo · 65 questões · 90 min", width="stretch"): start("Completo",65,90*60)
    if exams:
        st.subheader("Evolução")
        chart=pd.DataFrame([{'Tentativa':f"#{a['id']}", 'Nota':a['score']} for a in reversed(exams[:20])]).set_index('Tentativa')
        # `st.line_chart` não aceita y_min/y_max em todas as versões do Streamlit.
        # As linhas auxiliares mantêm a escala percentual comparável em 0–100.
        chart["Meta (80%)"] = 80
        chart["Limite inferior"] = 0
        chart["Limite superior"] = 100
        st.line_chart(chart)
    st.subheader("Por domínio")
    stats={r['domain']: (100*r['correct']/r['total'] if r['total'] else 0, r['total']) for r in domain_rows}
    for domain in DOMAINS:
        value,total=stats.get(domain,(0,0)); st.write(f"**{domain}** · {pct(value)} · {total} respondida(s)"); st.progress(value/100)

def start(kind,count,limit,questions=None):
    questions=questions or choose_questions(count); aid=create_attempt(kind,len(questions))
    st.session_state.exam={'id':aid,'kind':kind,'questions':questions,'start':time.time(),'limit':limit}
    st.rerun()

@st.fragment(run_every=1)
def countdown(started, limit):
    """Relógio que atualiza sozinho a cada segundo sem recarregar as questões."""
    remaining=max(limit-int(time.time()-started),0)
    if remaining: st.warning(f"Tempo restante: **{remaining//60:02d}:{remaining%60:02d}**")
    else: st.error("O tempo acabou. Envie o simulado para corrigir.")

def exam():
    e=st.session_state.exam
    st.title(f"{e['kind']} · {len(e['questions'])} questões")
    english=st.session_state.get("english", False)
    st.caption(f"Idioma: {'inglês' if english else 'português'}. " + ("As questões autorais só existem em português e aparecem assim mesmo." if english else "Use o botão de cada questão para ver o original em inglês."))
    if e['limit']: countdown(e['start'], e['limit'])
    responses={}
    with st.form('exam_form'):
        for n,original in enumerate(e['questions'],1):
            q=view(original)
            st.markdown(f"### {n}. {q['prompt']}")
            other_language(original, f"alt_exam_{q['id']}")
            opts=list(q['choices'].keys()); fmt=lambda k,q=q:f"{k}. {q['choices'][k]}"
            if q['multi']:
                responses[q['id']]=st.multiselect("Selecione todas as respostas corretas",opts,format_func=fmt,key=f"q{q['id']}")
            else:
                picked=st.radio("Selecione uma resposta",[None]+opts,format_func=lambda k:"Selecione..." if k is None else fmt(k),key=f"q{q['id']}",label_visibility='collapsed')
                responses[q['id']]=[] if picked is None else [picked]
        submitted=st.form_submit_button("Enviar simulado e ver correção",type='primary')
    if submitted:
        submit_attempt(e['id'],responses,int(time.time()-e['start']))
        st.session_state.result=e['id']; del st.session_state.exam; st.rerun()

def result(aid):
    attempt, rows=attempt_detail(aid); st.title("Resultado")
    st.metric("Nota",pct(attempt['score']),f"{attempt['correct_count']} de {attempt['total']} corretas · {duration_text(attempt['duration_seconds'])}")
    st.progress(attempt['score']/100, text="Meta atingida!" if attempt['score']>=80 else "Meta de 80%: continue praticando.")
    st.subheader("Correção e revisão")
    st.caption("Em cada erro, entenda por que cada alternativa errada está errada e anote no caderno de erros.")
    for i,q in enumerate(rows,1):
        with st.expander(f"{('✓' if q['was_correct'] else '✗')} Questão {i} · {q['domain']} · {q['topic']}"):
            review(q, f"alt_result_{i}")
    if st.button("Voltar ao dashboard"): del st.session_state.result; st.rerun()

def flashcards():
    st.title("🃏 Flashcards")
    st.caption("Leia o cenário, diga em voz alta qual é o serviço e só então revele a resposta. Quem acerta volta em 1, 3, 7, 14 e 30 dias; quem erra volta amanhã.")
    fc=st.session_state.get("fc")
    if not fc:
        cards=all_cards(); progress=flashcard_progress(); due={c['id'] for c in due_flashcards()}
        groups=["Todos os grupos"]+[g for g,_,_ in GROUPS]
        group=st.selectbox("Grupo", groups)
        pool=[c for c in cards if group=="Todos os grupos" or c['group']==group]
        learned=sum(progress.get(c['id'],{}).get('box',0)>=2 for c in pool)
        m1,m2,m3=st.columns(3)
        m1.metric("Para revisar agora", sum(c['id'] in due and c['id'] in progress for c in pool))
        m2.metric("Novos", sum(c['id'] not in progress for c in pool)); m3.metric("Fixados (revisão de 7+ dias)", learned)
        queue=[c['id'] for c in pool if c['id'] in due]
        # Cards vencidos primeiro, depois novos; dentro de cada parte, em ordem aleatória.
        queue=sorted(queue, key=lambda i: (i not in progress, random.random()))[:SESSION_SIZE]
        if st.button(f"Começar sessão · {len(queue)} cards", type="primary", disabled=not queue):
            st.session_state.fc={'queue':queue,'show':False,'done':0,'missed':[]}; st.rerun()
        if not queue: st.success("Nada para revisar neste grupo hoje. Volte amanhã ou escolha outro grupo.")
        cards_tsv="\n".join(f"{c['use']}\t{c['service']} — {c['contrast']}".replace("\n"," ") for c in cards)
        st.download_button("Exportar todos os cards para o Anki (.txt)", cards_tsv.encode("utf-8"), "aws-flashcards.txt", "text/plain",
                           help="No Anki: Arquivo › Importar, separador Tab. Frente = cenário; verso = serviço.")
        return
    by_id={c['id']:c for c in all_cards()}
    if not fc['queue']:
        st.success(f"Sessão concluída: {fc['done']} card(s) revisado(s)." + (f" Para reforçar: {', '.join(fc['missed'])}." if fc['missed'] else ""))
        if st.button("Voltar"): del st.session_state.fc; st.rerun()
        return
    card=by_id[fc['queue'][0]]
    st.progress(fc['done']/(fc['done']+len(fc['queue'])), text=f"{fc['done']} feito(s) · {len(fc['queue'])} restante(s)")
    st.caption(card['group'])
    st.markdown(f"### {card['use']}")
    st.markdown("**Qual serviço ou conceito é esse?**")
    if not fc['show']:
        if st.button("Mostrar resposta", type="primary"): fc['show']=True; st.rerun()
    else:
        st.success(f"**{card['service']}**")
        if card['contrast']: st.info(f"Não confundir: {card['contrast']}")
        x,y=st.columns(2)
        if x.button("✅ Sabia", width="stretch"):
            # Um card errado na sessão volta para a fila, mas o acerto depois disso não o promove:
            # ele continua agendado para amanhã.
            if card['service'] not in fc['missed']: review_flashcard(card['id'], True)
            fc['queue'].pop(0); fc['done']+=1; fc['show']=False; st.rerun()
        if y.button("❌ Não sabia", width="stretch"):
            review_flashcard(card['id'], False)
            if card['service'] not in fc['missed']: fc['missed'].append(card['service'])
            fc['queue'].append(fc['queue'].pop(0)); fc['show']=False; st.rerun()
    if st.button("Encerrar sessão"): del st.session_state.fc; st.rerun()

def notebook():
    st.title("📓 Caderno de erros")
    all_notes=notes(); due=[n for n in all_notes if is_due(n['due_at'])]
    if not all_notes:
        st.info("Ainda não há anotações. Ao revisar um erro no resultado ou no histórico, preencha o formulário do caderno de erros embaixo da correção.")
        return
    a,b=st.columns(2); a.metric("Anotações", len(all_notes)); b.metric("Para revisar hoje", len(due))
    tab_due,tab_all=st.tabs([f"Revisar hoje ({len(due)})", f"Todas ({len(all_notes)})"])
    with tab_due:
        if not due: st.success("Nenhuma anotação vence hoje.")
        for n in due:
            with st.container(border=True):
                st.markdown(f"**Cenário:** {n['cue']}")
                st.caption("Antes de abrir: qual era a resposta certa e qual pista apontava para ela?")
                with st.expander("Ver minha anotação"):
                    if n['mistake']: st.error(f"Errei porque: {n['mistake']}")
                    st.success(f"Certo: {n['clue']}")
                    q=view(n); st.caption(f"Questão: {q['prompt']}"); st.caption(f"Resposta correta: {option_text(q, n['correct'])}")
                x,y=st.columns(2)
                if x.button("✅ Lembrei", key=f"ok_{n['question_id']}", width="stretch"): review_note(n['question_id'], True); st.rerun()
                if y.button("❌ Esqueci", key=f"no_{n['question_id']}", width="stretch"): review_note(n['question_id'], False); st.rerun()
    with tab_all:
        for n in all_notes:
            with st.expander(f"{n['domain']} · {n['cue']}"):
                q=view(n); st.write(q['prompt'])
                st.success(f"Resposta correta: {option_text(q, n['correct'])}")
                st.info(q['explanation'])
                st.caption(f"Próxima revisão: {n['due_at'][:10]}")
                note_editor(n['question_id'], f"nb_{n['question_id']}")
                if st.button("Excluir anotação", key=f"del_{n['question_id']}"): delete_note(n['question_id']); st.rerun()
    tsv="\n".join(f"{n['cue']}\t{n['clue']}" + (f" (errei: {n['mistake']})" if n['mistake'] else "") for n in all_notes)
    st.download_button("Exportar caderno para o Anki (.txt)", tsv.replace("\r","").encode("utf-8"), "caderno-de-erros.txt", "text/plain",
                       help="No Anki: Arquivo › Importar, separador Tab.")

def guide():
    st.title("📚 Guia de estudo")
    tab_tables,tab_method,tab_sources=st.tabs(["Tabelas de comparação","Como estudar","Fontes oficiais"])
    with tab_tables:
        st.caption("A prova pergunta qual serviço resolve um cenário, e os erros quase sempre vêm de serviços parecidos. Estas tabelas juntam os grupos que mais confundem.")
        hide=st.toggle("Modo teste: esconder os nomes", help="Leia a coluna 'Quando usar' e tente lembrar o serviço. Melhor ainda: monte a tabela à mão antes de conferir.")
        for group,tip,rows in GROUPS:
            with st.expander(f"{group} · {len(rows)} itens"):
                st.info(tip)
                table=pd.DataFrame([{'Serviço':'❓' if hide else s,'Quando usar':u,'Não confundir com':c} for s,u,c in rows])
                st.dataframe(table, width="stretch", hide_index=True)
    with tab_method:
        attempts=summary()[0]; ready,full=readiness(attempts)
        st.markdown(f"""
**1. Caderno de erros.** É o que mais funciona. Para cada erro, anote o que a questão pedia, o que você marcou e por que estava errado, e qual pista apontava para a resposta certa. O formulário fica embaixo de cada correção.

**2. Comparar serviços parecidos.** Use as tabelas desta página. Monte cada tabela à mão, de memória, e só depois confira: o esforço de lembrar é o que fixa.

**3. Lembrar em vez de reler.** Feche o material e explique em voz alta o que um serviço faz e quando usar. Onde você travar é o que precisa estudar. Os flashcards seguem essa ideia.

**4. Revisão espaçada.** Flashcards e anotações voltam em 1, 3, 7, 14 e 30 dias; quem você esquece volta para amanhã. Abra o **Plano de hoje** no dashboard todos os dias.

**5. Rotina com o simulador.**
- Dias normais: um simulado diário (20 questões) e revisão de **todos** os erros, inclusive por que cada alternativa errada está errada.
- Quando houver erros pendentes: o simulado de **Reforço**, só com questões que você errou e ainda não acertou.
- Uma vez por semana: o simulado completo (65 questões, 90 minutos), para treinar ritmo.
- Pronto para agendar: os {READY_EXAMS} últimos simulados completos com 80% ou mais. Agora: **{ready} de {READY_EXAMS}** ({full} completo(s) feito(s)).
""")
    with tab_sources:
        for title,url,why in STUDY_SOURCES:
            st.markdown(f"- [{title}]({url}): {why}")

def history():
    attempts,_,errors,_=summary(); st.title("Histórico e erros")
    if not attempts: st.info("Conclua o primeiro simulado para ver seu histórico."); return
    data=[{'ID':a['id'],'Tipo':a['kind'],'Data (UTC)':a['submitted_at'][:10],'Nota':f"{a['score']:.1f}%",'Acertos':f"{a['correct_count']}/{a['total']}",'Duração':duration_text(a['duration_seconds'])} for a in attempts]
    st.dataframe(pd.DataFrame(data),width="stretch",hide_index=True)
    st.subheader("Últimos erros")
    if not errors: st.success("Nenhum erro registrado ainda.")
    for i,r in enumerate(errors):
        with st.expander(f"{r['domain']} · {r['topic']} · {r['answered_at'][:10]}"):
            review(r, f"alt_history_{i}")

with st.sidebar:
    st.header("Navegação")
    page=st.radio("Página",PAGES,key="page",label_visibility="collapsed")
    st.toggle("Questões em inglês", key="english", help="A prova CLF-C02 pode ser feita em português. Use o inglês quando quiser treinar no idioma original.")
    st.caption("As questões iniciais são autorais; o banco pode crescer sem mudar a estrutura.")
if 'exam' in st.session_state: exam()
elif 'result' in st.session_state: result(st.session_state.result)
elif page=='Dashboard': dashboard()
elif page=='Flashcards': flashcards()
elif page=='Caderno de erros': notebook()
elif page=='Guia de estudo': guide()
else: history()
