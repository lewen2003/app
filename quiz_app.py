import streamlit as st
import random
import json
import os

# ============================================================
# CONFIGURAZIONE QUIZ DISPONIBILI
# ============================================================

QUIZ_CONFIG = {
    "match_analysis": {
        "titolo": "Match Analysis",
        "emoji": "🏆",
        "descrizione": "Concetti, metodologie e strumenti della Match Analysis nello sport",
        "file": "domande.json",
    },
    "sport_integrazione": {
        "titolo": "Sport e Integrazione",
        "emoji": "🌍",
        "descrizione": "Cittadinanza, intercultura, valori e dinamiche di gruppo nello sport",
        "file": "sport_integrazione.json",
    },
    "metodi_tecniche": {
        "titolo": "Metodi e Tecniche dell'Attività Sportiva",
        "emoji": "⚽",
        "descrizione": "Calcio, Rugby, Basket, Atletica, Attività Adattata, Allenamento Giovanile e Fragilità",
        "file": "metodi_tecniche.json",
    },
}

# ============================================================
# CARICAMENTO DOMANDE
# ============================================================

def carica_domande(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================

st.set_page_config(
    page_title="Quiz Scienze Motorie",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; }

    /* Header */
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

    /* Card menu */
    .quiz-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 14px;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .quiz-card:hover { border-color: #4fc3f7; }
    .quiz-card h3 { color: #4fc3f7; margin: 0 0 6px 0; font-size: 1.15rem; }
    .quiz-card p { color: #8b949e; margin: 0; font-size: 0.9rem; }

    /* Domanda */
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

    /* Score finale */
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

    .stButton > button { border-radius: 8px; font-weight: 600; padding: 10px 24px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# STATO SESSIONE
# ============================================================

def init_state():
    defaults = {
        "schermata": "menu",       # menu | quiz | risultati
        "quiz_key": None,
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

def avvia_quiz(quiz_key, num_questions, shuffle_options):
    cfg = QUIZ_CONFIG[quiz_key]
    questions = carica_domande(cfg["file"]).copy()
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
    st.session_state.quiz_key = quiz_key
    st.session_state.schermata = "quiz"
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
    if sel == correct:
        st.session_state.score += 1
    st.session_state.answers[st.session_state.current_q] = {
        "selected": sel, "correct": correct, "is_correct": sel == correct,
    }
    st.session_state.answer_submitted = True

def next_question():
    total = len(st.session_state.shuffled_questions)
    if st.session_state.current_q + 1 >= total:
        st.session_state.schermata = "risultati"
    else:
        st.session_state.current_q += 1
        st.session_state.answer_submitted = False
        st.session_state.selected_answer = None

def torna_menu():
    for k in ["schermata","quiz_key","current_q","score","answers",
              "shuffled_questions","answer_submitted","selected_answer"]:
        del st.session_state[k]
    init_state()

# ============================================================
# SCHERMATA MENU
# ============================================================

if st.session_state.schermata == "menu":
    st.markdown("""
    <div class="quiz-header">
        <h1>🎓 Quiz Scienze Motorie</h1>
        <p>Seleziona la materia su cui vuoi esercitarti</p>
    </div>
    """, unsafe_allow_html=True)

    for key, cfg in QUIZ_CONFIG.items():
        domande = carica_domande(cfg["file"])
        st.markdown(f"""
        <div class="quiz-card">
            <h3>{cfg['emoji']} {cfg['titolo']}</h3>
            <p>{cfg['descrizione']}<br><small style="color:#4fc3f7">{len(domande)} domande disponibili</small></p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"⚙️ Configura {cfg['titolo']}"):
            col1, col2 = st.columns(2)
            with col1:
                num = st.slider(
                    "Numero domande", min_value=5,
                    max_value=len(domande),
                    value=min(20, len(domande)),
                    step=5, key=f"num_{key}"
                )
            with col2:
                shuf = st.checkbox("Mescola opzioni", value=True, key=f"shuf_{key}")
            if st.button(f"▶ Inizia — {cfg['titolo']}", key=f"btn_{key}",
                         use_container_width=True, type="primary"):
                avvia_quiz(key, num, shuf)
                st.rerun()

# ============================================================
# SCHERMATA QUIZ
# ============================================================

elif st.session_state.schermata == "quiz":
    cfg = QUIZ_CONFIG[st.session_state.quiz_key]
    questions = st.session_state.shuffled_questions
    idx = st.session_state.current_q
    total = len(questions)
    q = questions[idx]
    answered_so_far = idx + (1 if st.session_state.answer_submitted else 0)

    st.markdown(f"""
    <div class="quiz-header">
        <h1>{cfg['emoji']} {cfg['titolo']}</h1>
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
        choice = st.radio("Seleziona la risposta:",
                          options=list(range(len(q["opzioni"]))),
                          format_func=lambda i: q["opzioni"][i],
                          key=f"radio_{idx}", index=None)
        st.session_state.selected_answer = choice

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("✅ Conferma risposta", use_container_width=True, type="primary",
                         disabled=(st.session_state.selected_answer is None)):
                submit_answer()
                st.rerun()
        with col2:
            if st.button("🏠 Menu", use_container_width=True):
                torna_menu()
                st.rerun()
    else:
        ans = st.session_state.answers[idx]
        for i, opt in enumerate(q["opzioni"]):
            if i == ans["correct"] and i == ans["selected"]:
                st.success(f"✅ {opt}  ← La tua risposta (corretta!)")
            elif i == ans["correct"]:
                st.success(f"✅ {opt}  ← Risposta corretta")
            elif i == ans["selected"]:
                st.error(f"❌ {opt}  ← La tua risposta")
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
            if st.button("🏠 Menu", use_container_width=True):
                torna_menu()
                st.rerun()

# ============================================================
# SCHERMATA RISULTATI
# ============================================================

elif st.session_state.schermata == "risultati":
    cfg = QUIZ_CONFIG[st.session_state.quiz_key]
    questions = st.session_state.shuffled_questions
    total = len(questions)
    score = st.session_state.score
    perc = round(score / total * 100)

    if perc >= 90:   emoji, msg = "🏆", "Eccellente! Sei pronto per l'esame!"
    elif perc >= 75: emoji, msg = "🎯", "Ottimo risultato! Continua così."
    elif perc >= 60: emoji, msg = "📚", "Buon lavoro! Qualche ripasso e sarai pronto."
    else:            emoji, msg = "💪", "Continua a studiare, puoi migliorare!"

    st.markdown(f"""
    <div class="quiz-header">
        <h1>📊 Risultati — {cfg['titolo']}</h1>
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
        icon = "✅" if ans.get("is_correct") else "❌"
        with st.expander(f"{icon} Domanda {i + 1}: {q['domanda'][:75]}..."):
            st.markdown(f"**{q['domanda']}**")
            st.markdown("")
            for j, opt in enumerate(q["opzioni"]):
                if j == ans.get("correct") and j == ans.get("selected"):
                    st.success(f"✅ {opt}  ← La tua risposta (corretta!)")
                elif j == ans.get("correct"):
                    st.success(f"✅ {opt}  ← Risposta corretta")
                elif j == ans.get("selected"):
                    st.error(f"❌ {opt}  ← La tua risposta")
                else:
                    st.markdown(f"◻️ {opt}")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Rifai questo quiz", use_container_width=True, type="primary"):
            key = st.session_state.quiz_key
            domande = carica_domande(QUIZ_CONFIG[key]["file"])
            avvia_quiz(key, min(20, len(domande)), True)
            st.rerun()
    with col2:
        if st.button("🏠 Torna al Menu", use_container_width=True):
            torna_menu()
            st.rerun()
