import streamlit as st
import json
import random
import pandas as pd
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Quiz di Ripasso",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Carica le domande
@st.cache_data
def carica_domande():
    try:
        with open('domande.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ File 'domande.json' non trovato!")
        return []
    except json.JSONDecodeError:
        st.error("❌ Errore nel formato del file JSON!")
        return []

def inizializza_session_state():
    """Inizializza tutte le variabili di sessione"""
    session_vars = {
        'quiz_iniziato': False,
        'domande_quiz': [],
        'risposte_utente': [],
        'indice_corrente': 0,
        'punteggio': 0,
        'quiz_terminato': False,
        'mostra_revisione': False,
        'tempo_inizio': None
    }
    
    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

def inizia_quiz():
    """Inizia un nuovo quiz"""
    tutte_domande = carica_domande()
    if len(tutte_domande) < 10:
        st.error("❌ Servono almeno 10 domande nel file JSON!")
        return False
    
    st.session_state.domande_quiz = random.sample(tutte_domande, 10)
    st.session_state.risposte_utente = [None] * 10
    st.session_state.indice_corrente = 0
    st.session_state.punteggio = 0
    st.session_state.quiz_terminato = False
    st.session_state.quiz_iniziato = True
    st.session_state.mostra_revisione = False
    st.session_state.tempo_inizio = datetime.now()
    return True

def calcola_punteggio():
    """Calcola il punteggio finale"""
    st.session_state.punteggio = 0
    for i, domanda in enumerate(st.session_state.domande_quiz):
        risposta_utente = st.session_state.risposte_utente[i]
        if risposta_utente and risposta_utente in domanda['correct']:
            st.session_state.punteggio += 10

def mostra_progresso():
    """Mostra la barra di progresso"""
    progresso = (st.session_state.indice_corrente + 1) / 10
    st.progress(progresso)
    st.caption(f"Domanda {st.session_state.indice_corrente + 1} di 10")

def mostra_domanda():
    """Mostra la domanda corrente"""
    domanda = st.session_state.domande_quiz[st.session_state.indice_corrente]
    
    # Header con numero domanda
    st.subheader(f"📝 Domanda {st.session_state.indice_corrente + 1}")
    
    # Domanda
    st.markdown(f"**{domanda['question']}**")
    st.divider()
    
    # Opzioni di risposta
    opzioni = domanda['options']
    lettere = list(opzioni.keys())
    
    # Radio button per le risposte
    risposta_selezionata = st.radio(
        "Seleziona la tua risposta:",
        options=lettere,
        format_func=lambda x: f"**{x}**: {opzioni[x]}",
        key=f"domanda_{st.session_state.indice_corrente}",
        index=lettere.index(st.session_state.risposte_utente[st.session_state.indice_corrente]) 
        if st.session_state.risposte_utente[st.session_state.indice_corrente] in lettere else 0
    )
    
    # Salva automaticamente la risposta
    if risposta_selezionata:
        st.session_state.risposte_utente[st.session_state.indice_corrente] = risposta_selezionata
        st.success("✅ Risposta salvata")
    
    # Pulsanti di navigazione
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Precedente", disabled=st.session_state.indice_corrente == 0):
            st.session_state.indice_corrente -= 1
            st.rerun()
    
    with col2:
        if st.button("⏹️ Termina Quiz", type="secondary"):
            st.session_state.quiz_terminato = True
            calcola_punteggio()
            st.rerun()
    
    with col3:
        if st.button("Prossima ➡️", disabled=st.session_state.indice_corrente == 9):
            st.session_state.indice_corrente += 1
            st.rerun()
    
    # Mostra progresso
    mostra_progresso()

def mostra_risultati():
    """Mostra i risultati del quiz"""
    punteggio = st.session_state.punteggio
    superato = punteggio >= 60
    
    # Header risultati
    if superato:
        st.balloons()
        st.success("🎉 **Congratulazioni! Hai superato il quiz!**")
    else:
        st.error("😔 **Quiz non superato. Riprova!**")
    
    # Punteggio
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Punteggio", f"{punteggio}/100")
    with col2:
        st.metric("Esito", "✅ Superato" if superato else "❌ Non superato")
    
    # Statistiche
    st.divider()
    st.subheader("📊 Statistiche")
    
    domande_corrette = punteggio // 10
    domande_errate = 10 - domande_corrette
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Domande corrette", domande_corrette)
    with col2:
        st.metric("Domande errate", domande_errate)
    with col3:
        st.metric("Percentuale", f"{punteggio}%")
    
    # Pulsanti azione
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Nuovo Quiz", type="primary"):
            inizia_quiz()
            st.rerun()
    
    with col2:
        if st.button("📖 Revisione Dettagliata"):
            st.session_state.mostra_revisione = True
            st.rerun()
    
    with col3:
        if st.button("🏠 Menu Principale"):
            st.session_state.quiz_iniziato = False
            st.session_state.quiz_terminato = False
            st.rerun()

def mostra_revisione_dettagliata():
    """Mostra la revisione dettagliata di tutte le domande"""
    st.header("📖 Revisione Dettagliata")
    
    for i, domanda in enumerate(st.session_state.domande_quiz):
        with st.expander(f"Domanda {i+1}: {domanda['question'][:70]}...", expanded=False):
            risposta_utente = st.session_state.risposte_utente[i]
            risposta_corretta = domanda['correct'][0]
            opzioni = domanda['options']
            
            # Controlla se la risposta è corretta
            corretta = risposta_utente == risposta_corretta
            
            # La tua risposta
            col1, col2 = st.columns([1, 3])
            with col1:
                if risposta_utente:
                    if corretta:
                        st.success("✅ La tua risposta")
                    else:
                        st.error("❌ La tua risposta")
                else:
                    st.warning("⏭️ Nessuna risposta")
            
            with col2:
                if risposta_utente:
                    st.write(f"**{risposta_utente}**: {opzioni[risposta_utente]}")
                else:
                    st.write("Nessuna risposta data")
            
            # Risposta corretta
            if not corretta or not risposta_utente:
                st.info(f"**Risposta corretta: {risposta_corretta}**: {opzioni[risposta_corretta]}")
            
            st.divider()
    
    # Pulsanti per tornare indietro
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("↩️ Torna ai Risultati"):
            st.session_state.mostra_revisione = False
            st.rerun()
    with col2:
        if st.button("🔄 Nuovo Quiz"):
            inizia_quiz()
            st.rerun()

def mostra_homepage():
    """Mostra la homepage dell'app"""
    st.title("🧠 Quiz di Ripasso")
    st.markdown("---")
    
    st.markdown("""
    ### Benvenuto nel Quiz Interattivo!
    
    **Come funziona:**
    - 🔄 10 domande casuali dal database
    - ✅ Risposta corretta: **10 punti**
    - 🎯 Obiettivo: **almeno 60/100 punti**
    - 📱 Ottimizzato per mobile
    - 💾 Salvataggio automatico delle risposte
    """)
    
    # Statistiche domande disponibili
    tutte_domande = carica_domande()
    if tutte_domande:
        st.info(f"📚 **Domande disponibili nel database: {len(tutte_domande)}**")
    
    st.divider()
    
    # Pulsante per iniziare
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Inizia il Quiz", type="primary", use_container_width=True):
            if inizia_quiz():
                st.rerun()

# App principale
def main():
    # Inizializza session state
    inizializza_session_state()
    
    # Gestione dei diversi stati dell'app
    if not st.session_state.quiz_iniziato:
        mostra_homepage()
    
    elif st.session_state.quiz_iniziato and not st.session_state.quiz_terminato:
        mostra_domanda()
    
    elif st.session_state.quiz_terminato and not st.session_state.mostra_revisione:
        mostra_risultati()
    
    elif st.session_state.mostra_revisione:
        mostra_revisione_dettagliata()

if __name__ == "__main__":
    main()