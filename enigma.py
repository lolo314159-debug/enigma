import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# 1. Initialisation
if 'r1_base' not in st.session_state:
    def generate_derangement(n):
        indices = list(range(n))
        while True:
            random.shuffle(indices)
            if all(indices[i] != i for i in range(n)): return indices
    st.session_state.r1_base = generate_derangement(26)
    st.session_state.r2_base = generate_derangement(26)
    st.session_state.r3_base = generate_derangement(26)
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.pressed_key = None
    st.session_state.text_in, st.session_state.text_out = "", ""

st.set_page_config(page_title="Enigma : Flux Pré-Rotation", layout="wide")

# --- Logique de Chiffrement (Étapes du chemin) ---
def get_path_indices(key_char, off1, off2, off3):
    alphabet_list = list(string.ascii_uppercase)
    idx_in = alphabet_list.index(key_char)
    
    def step(input_idx, wiring, offset):
        contact_in = (input_idx + offset) % 26
        contact_out = wiring[contact_in]
        return (contact_out - offset) % 26
    
    i1 = step(idx_in, st.session_state.r1_base, off1)
    i2 = step(i1, st.session_state.r2_base, off2)
    i3 = step(i2, st.session_state.r3_base, off3)
    return [idx_in, i1, i2, i3]

st.title("📟 Enigma : Visualisation du signal avant rotation")

# Sidebar pour le délai
delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)
st.sidebar.caption("Le rotor tournera et le chemin s'effacera après ce délai.")

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Position actuelle (R1) :** `{string.ascii_uppercase[st.session_state.off1]}`")
    st.code(f"Entrée : {st.session_state.text_in if st.session_state.text_in else '-'}")
    st.code(f"Sortie : {st.session_state.text_out if st.session_state.text_out else '-'}")

    if st.button("⏪ Réinitialiser Tout", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out, st.session_state.pressed_key = "", "", None
        st.rerun()

with col_kbd:
    rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["W", "X", "C", "V", "B", "N"]]
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            # Le clic ne fait que stocker la touche. Le dessin et le délai suivent.
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                # On calcule le résultat avec les offsets de MAINTENANT
                p = get_path_indices(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += string.ascii_uppercase[p[3]]

# --- DESSIN DU GRAPHIQUE (ÉTAT ACTUEL) ---
def plot_enigma():
