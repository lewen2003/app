import streamlit as st
import json
import random
import pandas as pd
from datetime import datetime, timedelta
import time

# Configurazione pagina
st.set_page_config(
    page_title="Quiz di Ripasso - Multi Materia",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Funzioni per caricare i diversi set di domande
@st.cache_data
def carica_domande_endocrinologia():
    try:
        with open('domande.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ File 'domande.json' non trovato!")
        return []
    except json.JSONDecodeError:
        st.error("❌ Errore nel formato del file JSON 'domande.json'!")
        return []

@st.cache_data
def carica_domande_medicina():
    try:
        with open('DomandeMED.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ File 'DomandeMED.json' non trovato!")
        return []
    except json.JSONDecodeError:
        st.error("❌ Errore nel formato del file JSON 'DomandeMED.json'!")
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
        'tempo_rimanente': 30 * 60,
        'timer_scaduto': False,
        'tipo_quiz': None  # 'endocrinologia', 'medicina', 'misto'
    }
    
    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

def inizia_quiz(tipo_quiz):
    """Inizia un nuovo quiz del tipo specificato"""
    st.session_state.tipo_quiz = tipo_quiz
    
    if tipo_quiz == "endocrinologia":
        domande_totali = carica_domande_endocrinologia()
        num_domande = 40
    elif tipo_quiz == "medicina":
        domande_totali = carica_domande_medicina()
        num_domande = 40
    else:  # misto
        domande_endo = carica_domande_endocrinologia()
        domande_med = carica_domande_medicina()
        num_domande = 40
        
        # Prendi 20 domande da ciascuna materia
        if len(domande_endo) >= 20 and len(domande_med) >= 20:
            domande_endo_selezionate = random.sample(domande_endo, 20)
            domande_med_selezionate = random.sample(domande_med, 20)
            domande_totali = domande_endo_selezionate + domande_med_selezionate
            random.shuffle(domande_totali)
        else:
            st.error("❌ Non ci sono abbastanza domande per creare un quiz misto!")
            return False
    
    # Verifica che ci siano abbastanza domande
    if len(domande_totali) < num_domande:
        st.error(f"❌ Servono almeno {num_domande} domande per il quiz di {tipo_quiz}, ma ne hai solo {len(domande_totali)}!")
        return False
    
    st.session_state.domande_quiz = random.sample(domande_totali, num_domande)
    st.session_state.risposte_utente = [None] * num_domande
    st.session_state.indice_corrente = 0
    st.session_state.punteggio = 0
    st.session_state.quiz_terminato = False
    st.session_state.quiz_iniziato = True
    st.session_state.mostra_revisione = False
    st.session_state.tempo_inizio = datetime.now()
    st.session_state.tempo_rimanente = 30 * 60
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
    num_domande = len(st.session_state.domande_quiz)
    progresso = (st.session_state.indice_corrente + 1) / num_domande
    st.progress(progresso)
    st.caption(f"Domanda {st.session_state.indice_corrente + 1} di {num_domande}")

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
    num_domande = len(st.session_state.domande_quiz)
    
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
        if st.button("Prossima ➡️", disabled=st.session_state.indice_corrente == num_domande - 1):
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
            max_value=num_domande,
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
    punteggio_massimo = len(st.session_state.domande_quiz) * 10
    soglia_minima = punteggio_massimo * 0.6  # 60%
    superato = punteggio >= soglia_minima
    
    # Titolo in base al tipo di quiz
    titolo_quiz = {
        "endocrinologia": "Endocrinologia",
        "medicina": "Medicina", 
        "misto": "Misto (Endocrinologia + Medicina)"
    }
    
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
        st.metric("Punteggio", f"{punteggio}/{punteggio_massimo}")
    with col2:
        st.metric("Soglia minima", f"{int(soglia_minima)}/{punteggio_massimo}")
    with col3:
        st.metric("Esito", "✅ Superato" if superato else "❌ Non superato")
    
    # Statistiche
    st.divider()
    st.subheader("📊 Statistiche")
    
    domande_corrette = punteggio // 10
    domande_errate = len(st.session_state.domande_quiz) - domande_corrette
    percentuale = (punteggio / punteggio_massimo) * 100
    
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
            st.session_state.quiz_iniziato = False
            st.session_state.quiz_terminato = False
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
        if st.button("🏠 Menu Principale", use_container_width=True):
            st.session_state.quiz_iniziato = False
            st.session_state.quiz_terminato = False
            st.rerun()

def mostra_homepage():
    """Mostra la homepage dell'app con selezione del tipo di quiz"""
    st.title("🧠 Quiz di Ripasso - Multi Materia")
    st.markdown("---")
    
    st.markdown("""
    ### Scegli il tipo di quiz:
    
    **Opzioni disponibili:**
    - 🧬 **Endocrinologia**: 40 domande di endocrinologia
    - 🩺 **Medicina**: 40 domande di medicina generale  
    - 🔀 **Quiz Misto**: 20 domande di endocrinologia + 20 di medicina
    
    **Regole comuni:**
    - ⏰ **30 minuti** di tempo a disposizione
    - ✅ Risposta corretta: **10 punti**
    - 🎯 Obiettivo: **almeno 60% del punteggio totale**
    - 📱 Ottimizzato per mobile
    - 💾 Salvataggio automatico delle risposte
    """)
    
    # Carica e mostra statistiche per entrambi i database
    domande_endo = carica_domande_endocrinologia()
    domande_med = carica_domande_medicina()
    
    # Container per statistiche
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"🧬 **Endocrinologia:** {len(domande_endo)} domande")
            if len(domande_endo) >= 40:
                st.success("✅ Quiz disponibile")
            else:
                st.error(f"❌ Servono {40 - len(domande_endo)} domande in più")
        
        with col2:
            st.info(f"🩺 **Medicina:** {len(domande_med)} domande")
            if len(domande_med) >= 40:
                st.success("✅ Quiz disponibile")
            else:
                st.error(f"❌ Servono {40 - len(domande_med)} domande in più")
        
        # Statistiche quiz misto
        st.info(f"🔀 **Quiz Misto:** richiede 20 domande da ciascuna materia")
        if len(domande_endo) >= 20 and len(domande_med) >= 20:
            st.success("✅ Quiz disponibile")
        else:
            endo_mancanti = max(0, 20 - len(domande_endo))
            med_mancanti = max(0, 20 - len(domande_med))
            st.error(f"❌ Servono {endo_mancanti} domande di endocrinologia e {med_mancanti} di medicina")
    
    st.divider()
    
    # Pulsanti per selezionare il tipo di quiz
    st.subheader("🎯 Seleziona il tuo quiz:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(domande_endo) >= 40:
            if st.button("🧬\nQuiz Endocrinologia\n(40 domande)", 
                        type="primary", use_container_width=True, key="endo"):
                if inizia_quiz("endocrinologia"):
                    st.rerun()
        else:
            st.button("🧬\nQuiz Endocrinologia\n(40 domande)", 
                     disabled=True, 
                     help=f"Servono almeno 40 domande, disponibili: {len(domande_endo)}",
                     use_container_width=True, key="endo_disabled")
    
    with col2:
        if len(domande_med) >= 40:
            if st.button("🩺\nQuiz Medicina\n(40 domande)", 
                        type="primary", use_container_width=True, key="med"):
                if inizia_quiz("medicina"):
                    st.rerun()
        else:
            st.button("🩺\nQuiz Medicina\n(40 domande)", 
                     disabled=True, 
                     help=f"Servono almeno 40 domande, disponibili: {len(domande_med)}",
                     use_container_width=True, key="med_disabled")
    
    with col3:
        if len(domande_endo) >= 20 and len(domande_med) >= 20:
            if st.button("🔀\nQuiz Misto\n(20+20 domande)", 
                        type="primary", use_container_width=True, key="misto"):
                if inizia_quiz("misto"):
                    st.rerun()
        else:
            st.button("🔀\nQuiz Misto\n(20+20 domande)", 
                     disabled=True, 
                     help=f"Servono 20 domande per materia (Endo: {len(domande_endo)}, Med: {len(domande_med)})",
                     use_container_width=True, key="misto_disabled")

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