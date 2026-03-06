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
    alphabet = list(string.ascii_uppercase)
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    # Offsets utilisés pour l'affichage (AVANT rotation si une touche est pressée)
    disp_offsets = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_path_indices(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        off = disp_offsets[stage+1]
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        for i in range(26):
            # Le fil est actif si sa position d'entrée correspond au chemin
            is_active = (len(path) > 0 and (path[stage] + off) % 26 == i)
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            fig.add_trace(go.Scatter(
                x=[i - 0.18, i - 0.18, w[i] + 0.18, w[i] + 0.18], y=[y_top, h_y, h_y, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#f0f0f0", width=5 if is_active else 1),
                opacity=1.0 if is_active else 0.4, showlegend=False, hoverinfo='skip'
            ))

    for l_idx, y_val in enumerate(levels):
        off = disp_offsets[l_idx]
        for i in range(26):
            active = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', 
                            line=dict(color="red" if active else "#ccc", width=2 if active else 1)),
                text=alphabet[(i - off) % 26], 
                textfont=dict(size=9, color="red" if active else "black", family="Arial Black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.5]))
    return fig

# Affichage du graphique immédiat
st.plotly_chart(plot_enigma(), use_container_width=True)

# --- SÉQUENCE POST-AFFICHAGE ---
if st.session_state.pressed_key:
    # 1. Le chemin est affiché, on attend le délai choisi
    if delay > 0:
        time.sleep(delay)
    
    # 2. SEULEMENT APRÈS le délai, on effectue la rotation mécanique
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
    
    # 3. On efface la touche pressée (ce qui enlèvera le rouge au prochain rerun)
    st.session_state.pressed_key = None 
    st.rerun()
