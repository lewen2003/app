import streamlit as st
import json
import random
import pandas as pd
from datetime import datetime, timedelta
import time

# Configurazione pagina
st.set_page_config(
    page_title="Quiz di Ripasso - 40 Domande",
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
        'tempo_inizio': None,
        'tempo_rimanente': 30 * 60,  # 30 minuti in secondi
        'timer_scaduto': False
    }
    
    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

def inizia_quiz():
    """Inizia un nuovo quiz"""
    tutte_domande = carica_domande()
    if len(tutte_domande) < 40:
        st.error("❌ Servono almeno 40 domande nel file JSON!")
        return False
    
    st.session_state.domande_quiz = random.sample(tutte_domande, 40)
    st.session_state.risposte_utente = [None] * 40
    st.session_state.indice_corrente = 0
    st.session_state.punteggio = 0
    st.session_state.quiz_terminato = False
    st.session_state.quiz_iniziato = True
    st.session_state.mostra_revisione = False
    st.session_state.tempo_inizio = datetime.now()
    st.session_state.tempo_rimanente = 30 * 60  # 30 minuti
    st.session_state.timer_scaduto = False
    return True

def aggiorna_timer():
    """Aggiorna il timer rimanente"""
    if st.session_state.quiz_iniziato and not st.session_state.quiz_terminato:
        tempo_trascorso = (datetime.now() - st.session_state.tempo_inizio).total_seconds()
        st.session_state.tempo_rimanente = max(0, 30 * 60 - tempo_trascorso)
        
        if st.session_state.tempo_rimanente <= 0 and not st.session_state.timer_scaduto:
            st.session_state.timer_scaduto = True
            st.session_state.quiz_terminato = True
            calcola_punteggio()
            st.rerun()

def formatta_tempo(secondi):
    """Formatta il tempo in MM:SS"""
    minuti = int(secondi // 60)
    secondi = int(secondi % 60)
    return f"{minuti:02d}:{secondi:02d}"

def calcola_punteggio():
    """Calcola il punteggio finale"""
    st.session_state.punteggio = 0
    for i, domanda in enumerate(st.session_state.domande_quiz):
        risposta_utente = st.session_state.risposte_utente[i]
        if risposta_utente and risposta_utente in domanda['correct']:
            st.session_state.punteggio += 10

def mostra_progresso():
    """Mostra la barra di progresso"""
    progresso = (st.session_state.indice_corrente + 1) / 40
    st.progress(progresso)
    st.caption(f"Domanda {st.session_state.indice_corrente + 1} di 40")

def mostra_timer():
    """Mostra il timer"""
    tempo_rimanente = st.session_state.tempo_rimanente
    minuti_rimanenti = tempo_rimanente / 60
    
    # Cambia colore in base al tempo rimanente
    if minuti_rimanenti <= 5:
        colore = "red"
        icona = "🔴"
    elif minuti_rimanenti <= 10:
        colore = "orange"
        icona = "🟠"
    else:
        colore = "green"
        icona = "🟢"
    
    st.markdown(
        f"<div style='text-align: center; padding: 10px; border: 2px solid {colore}; border-radius: 10px; background-color: #f8f9fa;'>"
        f"<h3 style='color: {colore}; margin: 0;'>{icona} Tempo rimanente: {formatta_tempo(tempo_rimanente)}</h3>"
        f"</div>",
        unsafe_allow_html=True
    )

def mostra_domanda():
    """Mostra la domanda corrente"""
    # Aggiorna il timer
    aggiorna_timer()
    
    # Se il timer è scaduto, mostra i risultati
    if st.session_state.timer_scaduto:
        st.session_state.quiz_terminato = True
        calcola_punteggio()
        st.rerun()
        return
    
    domanda = st.session_state.domande_quiz[st.session_state.indice_corrente]
    
    # Header con numero domanda e timer
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"📝 Domanda {st.session_state.indice_corrente + 1}")
    with col2:
        mostra_timer()
    
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
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⬅️ Precedente", disabled=st.session_state.indice_corrente == 0):
            st.session_state.indice_corrente -= 1
            st.rerun()
    
    with col2:
        if st.button("Prossima ➡️", disabled=st.session_state.indice_corrente == 39):
            st.session_state.indice_corrente += 1
            st.rerun()
    
    with col3:
        if st.button("⏹️ Termina Quiz", type="secondary"):
            st.session_state.quiz_terminato = True
            calcola_punteggio()
            st.rerun()
    
    with col4:
        # Pulsante per saltare alla domanda specifica
        domanda_target = st.number_input(
            "Vai a:",
            min_value=1,
            max_value=40,
            value=st.session_state.indice_corrente + 1,
            key="salto_domanda"
        )
        if st.button("Vai") and domanda_target != st.session_state.indice_corrente + 1:
            st.session_state.indice_corrente = domanda_target - 1
            st.rerun()
    
    # Mostra progresso
    mostra_progresso()

def mostra_risultati():
    """Mostra i risultati del quiz"""
    punteggio = st.session_state.punteggio
    superato = punteggio >= 240  # 240/400 = 60%
    
    # Header risultati
    if st.session_state.timer_scaduto:
        st.error("⏰ **Tempo scaduto!**")
    elif superato:
        st.balloons()
        st.success("🎉 **Congratulazioni! Hai superato il quiz!**")
    else:
        st.error("😔 **Quiz non superato. Riprova!**")
    
    # Punteggio
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Punteggio", f"{punteggio}/400")
    with col2:
        st.metric("Soglia minima", "240/400")
    with col3:
        st.metric("Esito", "✅ Superato" if superato else "❌ Non superato")
    
    # Statistiche
    st.divider()
    st.subheader("📊 Statistiche")
    
    domande_corrette = punteggio // 10
    domande_errate = 40 - domande_corrette
    percentuale = (punteggio / 400) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Domande corrette", domande_corrette)
    with col2:
        st.metric("Domande errate", domande_errate)
    with col3:
        st.metric("Percentuale", f"{percentuale:.1f}%")
    with col4:
        st.metric("Tempo utilizzato", 
                 formatta_tempo(30*60 - st.session_state.tempo_rimanente) if not st.session_state.timer_scaduto else "30:00")
    
    # Grafico a barre
    dati = {
        'Tipo': ['Corrette', 'Errate'],
        'Numero': [domande_corrette, domande_errate]
    }
    df = pd.DataFrame(dati)
    st.bar_chart(df.set_index('Tipo'))
    
    # Pulsanti azione
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Nuovo Quiz", type="primary", use_container_width=True):
            inizia_quiz()
            st.rerun()
    
    with col2:
        if st.button("📖 Revisione Dettagliata", use_container_width=True):
            st.session_state.mostra_revisione = True
            st.rerun()
    
    with col3:
        if st.button("🏠 Menu Principale", use_container_width=True):
            st.session_state.quiz_iniziato = False
            st.session_state.quiz_terminato = False
            st.rerun()

def mostra_revisione_dettagliata():
    """Mostra la revisione dettagliata di tutte le domande"""
    st.header("📖 Revisione Dettagliata")
    
    # Filtro per tipo di domanda
    col1, col2 = st.columns([1, 3])
    with col1:
        filtro = st.selectbox(
            "Filtra domande:",
            ["Tutte", "Corrette", "Errate", "Non risposte"]
        )
    
    domande_filtrate = []
    for i, domanda in enumerate(st.session_state.domande_quiz):
        risposta_utente = st.session_state.risposte_utente[i]
        risposta_corretta = domanda['correct'][0]
        corretta = risposta_utente == risposta_corretta
        
        if filtro == "Tutte":
            domande_filtrate.append((i, domanda, risposta_utente, corretta))
        elif filtro == "Corrette" and corretta:
            domande_filtrate.append((i, domanda, risposta_utente, corretta))
        elif filtro == "Errate" and risposta_utente and not corretta:
            domande_filtrate.append((i, domanda, risposta_utente, corretta))
        elif filtro == "Non risposte" and not risposta_utente:
            domande_filtrate.append((i, domanda, risposta_utente, corretta))
    
    st.write(f"**{len(domande_filtrate)} domande {filtro.lower()}**")
    
    for i, domanda, risposta_utente, corretta in domande_filtrate:
        with st.expander(f"Domanda {i+1}: {domanda['question'][:70]}...", expanded=False):
            risposta_corretta = domanda['correct'][0]
            opzioni = domanda['options']
            
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
        if st.button("↩️ Torna ai Risultati", use_container_width=True):
            st.session_state.mostra_revisione = False
            st.rerun()
    with col2:
        if st.button("🔄 Nuovo Quiz", use_container_width=True):
            inizia_quiz()
            st.rerun()

def mostra_homepage():
    """Mostra la homepage dell'app"""
    st.title("🧠 Quiz di Ripasso - 40 Domande")
    st.markdown("---")
    
    st.markdown("""
    ### Benvenuto nel Quiz Avanzato!
    
    **Nuove regole:**
    - 🔄 **40 domande** casuali dal database
    - ⏰ **30 minuti** di tempo a disposizione
    - ✅ Risposta corretta: **10 punti**
    - 🎯 Obiettivo: **almeno 240/400 punti** (60%)
    - 📱 Ottimizzato per mobile
    - 💾 Salvataggio automatico delle risposte
    
    **Suggerimenti:**
    - Gestisci bene il tuo tempo!
    - Usa il pulsante "Vai a" per navigare rapidamente
    - Controlla il timer in alto a destra
    """)
    
    # Statistiche domande disponibili
    tutte_domande = carica_domande()
    if tutte_domande:
        st.info(f"📚 **Domande disponibili nel database: {len(tutte_domande)}**")
        
        if len(tutte_domande) < 40:
            st.warning(f"⚠️ **Attenzione:** Servono almeno 40 domande, ma ne hai solo {len(tutte_domande)}")
        else:
            st.success(f"✅ **Pronto:** {len(tutte_domande)} domande disponibili")
    
    st.divider()
    
    # Pulsante per iniziare
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Inizia il Quiz (40 domande - 30 minuti)", type="primary", use_container_width=True):
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