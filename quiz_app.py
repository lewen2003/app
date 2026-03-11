import streamlit as st
import random
import json
import os

# ============================================================
# CARICAMENTO DOMANDE DA JSON
# ============================================================

@st.cache_data
def carica_domande():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "domande.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# CONFIGURAZIONE STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Quiz Match Analysis",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    .quiz-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1a2a4a, #0d3b6e);
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #1e4080;
    }
    .quiz-header h1 { color: #4fc3f7; font-size: 2rem; margin: 0; }
    .quiz-header p { color: #90caf9; margin: 6px 0 0 0; }
    .question-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .question-number {
        color: #4fc3f7;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .question-text { color: #e6edf3; font-size: 1.05rem; line-height: 1.6; }
    .score-box {
        text-align: center;
        background: linear-gradient(135deg, #1a2a4a, #0d3b6e);
        border-radius: 12px;
        padding: 30px;
        border: 1px solid #1e4080;
        margin: 20px 0;
    }
    .score-number { font-size: 4rem; font-weight: 800; color: #4fc3f7; }
    .score-label { color: #90caf9; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# STATO SESSIONE
# ============================================================

def init_state():
    defaults = {
        "quiz_started": False,
        "quiz_done": False,
        "current_q": 0,
        "score": 0,
        "answers": {},
        "shuffled_questions": None,
        "answer_submitted": False,
        "selected_answer": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# FUNZIONI
# ============================================================

def start_quiz(domande, num_questions, shuffle_options):
    questions = domande.copy()
    random.shuffle(questions)
    questions = questions[:num_questions]

    if shuffle_options:
        for q in questions:
            correct_text = q["opzioni"][q["risposta_corretta"]]
            shuffled = q["opzioni"].copy()
            random.shuffle(shuffled)
            q["opzioni"] = shuffled
            q["risposta_corretta"] = shuffled.index(correct_text)

    st.session_state.shuffled_questions = questions
    st.session_state.quiz_started = True
    st.session_state.quiz_done = False
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.answer_submitted = False
    st.session_state.selected_answer = None

def submit_answer():
    if st.session_state.selected_answer is None:
        return
    q = st.session_state.shuffled_questions[st.session_state.current_q]
    sel = st.session_state.selected_answer
    correct = q["risposta_corretta"]
    is_correct = (sel == correct)
    if is_correct:
        st.session_state.score += 1
    st.session_state.answers[st.session_state.current_q] = {
        "selected": sel,
        "correct": correct,
        "is_correct": is_correct
    }
    st.session_state.answer_submitted = True

def next_question():
    total = len(st.session_state.shuffled_questions)
    if st.session_state.current_q + 1 >= total:
        st.session_state.quiz_done = True
    else:
        st.session_state.current_q += 1
        st.session_state.answer_submitted = False
        st.session_state.selected_answer = None

def restart_quiz():
    for k in ["quiz_started", "quiz_done", "current_q", "score", "answers",
              "shuffled_questions", "answer_submitted", "selected_answer"]:
        if k in st.session_state:
            del st.session_state[k]

# ============================================================
# CARICA DOMANDE
# ============================================================

try:
    DOMANDE = carica_domande()
except FileNotFoundError:
    st.error("⚠️ File `domande.json` non trovato. Assicurati che sia nella stessa cartella di `quiz_match_analysis.py`.")
    st.stop()

# ============================================================
# SCHERMATA INIZIALE
# ============================================================

if not st.session_state.quiz_started:
    st.markdown("""
    <div class="quiz-header">
        <h1>🏆 Quiz Match Analysis</h1>
        <p>Esercitati per l'esame di Scienze Motorie</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Domande disponibili:** {len(DOMANDE)}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        num_q = st.slider(
            "Quante domande vuoi fare?",
            min_value=5,
            max_value=len(DOMANDE),
            value=min(20, len(DOMANDE)),
            step=5
        )
    with col2:
        shuffle = st.checkbox("Mescola le opzioni di risposta", value=True)

    st.markdown("")
    if st.button("▶ Inizia il Quiz", use_container_width=True, type="primary"):
        start_quiz(DOMANDE, num_q, shuffle)
        st.rerun()

# ============================================================
# SCHERMATA QUIZ
# ============================================================

elif st.session_state.quiz_started and not st.session_state.quiz_done:
    questions = st.session_state.shuffled_questions
    idx = st.session_state.current_q
    total = len(questions)
    q = questions[idx]

    answered_so_far = idx + (1 if st.session_state.answer_submitted else 0)

    st.markdown(f"""
    <div class="quiz-header">
        <h1>🏆 Quiz Match Analysis</h1>
        <p>Domanda {idx + 1} di {total} &nbsp;|&nbsp; Punteggio: {st.session_state.score}/{answered_so_far}</p>
    </div>
    """, unsafe_allow_html=True)

    st.progress(answered_so_far / total)

    st.markdown(f"""
    <div class="question-box">
        <div class="question-number">Domanda {idx + 1}</div>
        <div class="question-text">{q['domanda']}</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.answer_submitted:
        choice = st.radio(
            "Seleziona la risposta:",
            options=list(range(len(q["opzioni"]))),
            format_func=lambda i: q["opzioni"][i],
            key=f"radio_{idx}",
            index=None
        )
        st.session_state.selected_answer = choice

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("✅ Conferma risposta", use_container_width=True, type="primary",
                         disabled=(st.session_state.selected_answer is None)):
                submit_answer()
                st.rerun()
        with col2:
            if st.button("🔄 Ricomincia", use_container_width=True):
                restart_quiz()
                st.rerun()

    else:
        ans = st.session_state.answers[idx]
        for i, opt in enumerate(q["opzioni"]):
            if i == ans["correct"] and i == ans["selected"]:
                st.success(f"✅ {opt} ← La tua risposta (corretta!)")
            elif i == ans["correct"]:
                st.success(f"✅ {opt} ← Risposta corretta")
            elif i == ans["selected"]:
                st.error(f"❌ {opt} ← La tua risposta")
            else:
                st.markdown(f"◻️ {opt}")

        st.markdown("")
        col1, col2 = st.columns([3, 1])
        with col1:
            label = "➡ Prossima domanda" if idx + 1 < total else "📊 Vedi risultati"
            if st.button(label, use_container_width=True, type="primary"):
                next_question()
                st.rerun()
        with col2:
            if st.button("🔄 Ricomincia", use_container_width=True):
                restart_quiz()
                st.rerun()

# ============================================================
# SCHERMATA RISULTATI FINALI
# ============================================================

elif st.session_state.quiz_done:
    questions = st.session_state.shuffled_questions
    total = len(questions)
    score = st.session_state.score
    perc = round(score / total * 100)

    if perc >= 90:
        emoji, msg = "🏆", "Eccellente! Sei pronto per l'esame!"
    elif perc >= 75:
        emoji, msg = "🎯", "Ottimo risultato! Continua così."
    elif perc >= 60:
        emoji, msg = "📚", "Buon lavoro! Qualche ripasso e sarai pronto."
    else:
        emoji, msg = "💪", "Continua a studiare, puoi migliorare!"

    st.markdown("""
    <div class="quiz-header">
        <h1>📊 Risultati Finali</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
        <div class="score-number">{emoji} {score}/{total}</div>
        <div class="score-label">{perc}% — {msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Riepilogo risposte")

    for i, q in enumerate(questions):
        ans = st.session_state.answers.get(i, {})
        is_correct = ans.get("is_correct", False)
        icon = "✅" if is_correct else "❌"
        short_q = q['domanda'][:80] + ("..." if len(q['domanda']) > 80 else "")

        with st.expander(f"{icon} Domanda {i+1}: {short_q}"):
            st.markdown(f"**{q['domanda']}**")
            st.markdown("")
            for j, opt in enumerate(q["opzioni"]):
                if j == ans.get("correct") and j == ans.get("selected"):
                    st.success(f"✅ {opt} ← La tua risposta (corretta!)")
                elif j == ans.get("correct"):
                    st.success(f"✅ {opt} ← Risposta corretta")
                elif j == ans.get("selected"):
                    st.error(f"❌ {opt} ← La tua risposta")
                else:
                    st.markdown(f"◻️ {opt}")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Ricomincia quiz", use_container_width=True, type="primary"):
            restart_quiz()
            st.rerun()
    with col2:
        if st.button("⚙️ Nuova configurazione", use_container_width=True):
            restart_quiz()
            st.rerun()
