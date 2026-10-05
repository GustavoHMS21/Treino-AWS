import time
import streamlit as st
import pandas as pd
from database import DOMAINS, init_db, choose_questions, create_attempt, submit_attempt, summary, attempt_detail

st.set_page_config(page_title="Simulador AWS CLF-C02", page_icon="☁️", layout="wide")
init_db()

def pct(v): return f"{v:.0f}%" if v is not None else "—"
def duration_text(seconds):
    seconds=int(seconds or 0); return f"{seconds//60}min {seconds%60:02d}s"

def dashboard():
    attempts, domain_rows, errors, streak = summary()
    st.title("☁️ Simulador AWS Cloud Practitioner")
    st.caption("CLF-C02 · questões autorais para estudo · dados salvos apenas neste computador")
    scores=[a['score'] for a in attempts]
    overall = sum(a['correct_count'] for a in attempts) / sum(a['total'] for a in attempts) * 100 if attempts else 0
    a,b,c,d=st.columns(4); a.metric("Desempenho geral", pct(overall), "Meta: 80%")
    b.metric("Simulados concluídos", len(attempts)); c.metric("Sequência ≥80%", streak); d.metric("Questões para revisar", len(errors))
    st.progress(min(overall/100,1.0), text=f"Meta visual: {pct(overall)} de 80%")
    st.subheader("Novo simulado")
    x,y=st.columns(2)
    if x.button("Iniciar diário · 20 questões", use_container_width=True): start("Diário",20,0)
    if y.button("Iniciar completo · 65 questões · 90 min", use_container_width=True): start("Completo",65,90*60)
    if attempts:
        st.subheader("Evolução")
        chart=pd.DataFrame([{'Tentativa':f"#{a['id']}", 'Nota':a['score']} for a in reversed(attempts[:20])]).set_index('Tentativa')
        st.line_chart(chart, y='Nota', y_min=0, y_max=100)
    st.subheader("Por domínio")
    stats={r['domain']: (100*r['correct']/r['total'] if r['total'] else 0, r['total']) for r in domain_rows}
    for domain in DOMAINS:
        value,total=stats.get(domain,(0,0)); st.write(f"**{domain}** · {pct(value)} · {total} respondida(s)"); st.progress(value/100)

def start(kind,count,limit):
    questions=choose_questions(count); aid=create_attempt(kind,count)
    st.session_state.exam={'id':aid,'kind':kind,'questions':questions,'start':time.time(),'limit':limit}
    st.rerun()

def exam():
    e=st.session_state.exam; elapsed=int(time.time()-e['start']); remaining=max(e['limit']-elapsed,0)
    st.title(f"{e['kind']} · {len(e['questions'])} questões")
    if e['limit']:
        st.warning(f"Tempo restante: **{remaining//60:02d}:{remaining%60:02d}**")
        if remaining==0: st.error("O tempo acabou. Envie o simulado para corrigir.")
    responses={}
    with st.form('exam_form'):
        for n,q in enumerate(e['questions'],1):
            st.markdown(f"### {n}. {q['prompt']}")
            opts=list(q['choices'].keys()); fmt=lambda k:f"{k}. {q['choices'][k]}"
            if q['multi']:
                responses[q['id']]=st.multiselect("Selecione todas as respostas corretas",opts,format_func=fmt,key=f"q{q['id']}")
            else:
                picked=st.radio("Selecione uma resposta",[None]+opts,format_func=lambda k:"Selecione..." if k is None else fmt(k),key=f"q{q['id']}",label_visibility='collapsed')
                responses[q['id']]=[] if picked is None else [picked]
        submitted=st.form_submit_button("Enviar simulado e ver correção",type='primary',disabled=e['limit'] and remaining==0 and False)
    if submitted:
        correct,score=submit_attempt(e['id'],responses,int(time.time()-e['start']))
        st.session_state.result=e['id']; del st.session_state.exam; st.rerun()

def result(aid):
    attempt, rows=attempt_detail(aid); st.title("Resultado")
    st.metric("Nota",pct(attempt['score']),f"{attempt['correct_count']} de {attempt['total']} corretas · {duration_text(attempt['duration_seconds'])}")
    st.progress(attempt['score']/100, text="Meta atingida!" if attempt['score']>=80 else "Meta de 80%: continue praticando.")
    st.subheader("Correção e revisão")
    for i,q in enumerate(rows,1):
        with st.expander(f"{('✓' if q['was_correct'] else '✗')} Questão {i} · {q['domain']} · {q['topic']}"):
            st.write(q['prompt']); st.write("Sua resposta:", ", ".join(q['selected']) or "Não respondida"); st.write("Correta:", ", ".join(q['correct']))
            st.info(q['explanation']); st.markdown(f"Referência oficial: [{q['reference_title']}]({q['reference_url']})")
    if st.button("Voltar ao dashboard"): del st.session_state.result; st.rerun()

def history():
    attempts,_,errors,_=summary(); st.title("Histórico e erros")
    if not attempts: st.info("Conclua o primeiro simulado para ver seu histórico."); return
    data=[{'ID':a['id'],'Tipo':a['kind'],'Data (UTC)':a['submitted_at'][:10],'Nota':f"{a['score']:.1f}%",'Acertos':f"{a['correct_count']}/{a['total']}",'Duração':duration_text(a['duration_seconds'])} for a in attempts]
    st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
    st.subheader("Últimos erros")
    if not errors: st.success("Nenhum erro registrado ainda.")
    for r in errors:
        with st.expander(f"{r['domain']} · {r['topic']} · {r['answered_at'][:10]}"):
            st.write(r['prompt']); st.info(r['explanation']); st.markdown(f"[Abrir referência oficial: {r['reference_title']}]({r['reference_url']})")

with st.sidebar:
    st.header("Navegação")
    page=st.radio("",["Dashboard","Histórico e revisão"])
    st.caption("As questões iniciais são autorais; o banco pode crescer sem mudar a estrutura.")
if 'exam' in st.session_state: exam()
elif 'result' in st.session_state: result(st.session_state.result)
elif page=='Dashboard': dashboard()
else: history()
