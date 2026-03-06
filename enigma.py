import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# 1. Initialisation stable
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

st.set_page_config(page_title="Enigma : Analyse Temporelle", layout="wide")

# --- Interface de contrôle ---
st.title("📟 Enigma : Observation du Signal")

# Ajout du curseur de délai
delay = st.sidebar.slider("Délai d'observation (secondes)", 0, 10, 2) 
st.sidebar.info("Le chemin reste visible pendant ce délai avant que le rotor ne tourne pour la lettre suivante.")

col_log, col_kbd = st.columns([1, 1])

# --- Logique de Chiffrement ---
def get_path_indices(key_char, off1, off2, off3):
    idx_in = list(string.ascii_uppercase).index(key_char)
    def step(input_idx, wiring, offset):
        contact_in = (input_idx + offset) % 26
        contact_out = wiring[contact_in]
        return (contact_out - offset) % 26
    
    i1 = step(idx_in, st.session_state.r1_base, off1)
    i2 = step(i1, st.session_state.r2_base, off2)
    i3 = step(i2, st.session_state.r3_base, off3)
    return [idx_in, i1, i2, i3]

with col_log:
    st.write(f"**Positions :** `{string.ascii_uppercase[st.session_state.off1]}` | `{string.ascii_uppercase[st.session_state.off2]}` | `{string.ascii_uppercase[st.session_state.off3]}`")
    area_in = st.empty()
    area_out = st.empty()
    area_in.code(st.session_state.text_in if st.session_state.text_in else " ")
    area_out.code(st.session_state.text_out if st.session_state.text_out else " ")

# --- CLAVIER ---
with col_kbd:
    rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["W", "X", "C", "V", "B", "N"]]
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                # A. On définit la touche pressée pour l'affichage immédiat
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                
                # B. Calcul du résultat avec les positions ACTUELLES
                p = get_path_indices(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += string.ascii_uppercase[p[3]]
                
                # C. Mise à jour visuelle immédiate du texte
                area_in.code(st.session_state.text_in)
                area_out.code(st.session_state.text_out)
                
                # D. On force le rafraîchissement pour montrer le chemin AVANT le délai
                st.rerun()

# --- GESTION DU DÉLAI ET ROTATION ---
if st.session_state.pressed_key:
    # On affiche le schéma (voir fonction plus bas)
    # Puis on attend
    if delay > 0:
        time.sleep(delay)
    
    # E. APRÈS le délai, on fait tourner le rotor et on efface le chemin
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
    
    st.session_state.pressed_key = None # Efface le chemin
    st.rerun()

# --- FONCTION DE DESSIN ---
def plot_enigma():
    alphabet = list(string.ascii_uppercase)
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offsets = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_path_indices(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        off = offsets[stage+1]
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        for i in range(26):
            # Un fil est actif si sa position physique d'entrée correspond au (chemin + offset)
            is_active = (len(path) > 0 and (path[stage] + off) % 26 == i)
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            fig.add_trace(go.Scatter(
                x=[i - 0.18, i - 0.18, w[i] + 0.18, w[i] + 0.18], y=[y_top, h_y, h_y, y_bot],
                mode='lines', line=dict(color="red" if is_active else "gray", width=5 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False, hoverinfo='skip'
            ))

    for l_idx, y_val in enumerate(levels):
        off = offsets[l_idx]
        for i in range(26):
            active = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color="red" if active else "#999", width=2 if active else 1)),
                text=alphabet[(i - off) % 26], textfont=dict(size=9, color="red" if active else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    return fig

st.plotly_chart(plot_enigma(), use_container_width=True)
