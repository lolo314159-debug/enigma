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

st.set_page_config(page_title="Enigma : Correction Ligne 1", layout="wide")

# --- Logique de Chiffrement ---
def get_path_indices(key_char, o1, o2, o3):
    alphabet_list = list(string.ascii_uppercase)
    idx_in = alphabet_list.index(key_char)
    def step(input_idx, wiring, offset):
        contact_in = (input_idx + offset) % 26
        contact_out = wiring[contact_in]
        return (contact_out - offset) % 26
    i1 = step(idx_in, st.session_state.r1_base, o1)
    i2 = step(i1, st.session_state.r2_base, o2)
    i3 = step(i2, st.session_state.r3_base, o3)
    return [idx_in, i1, i2, i3]

st.title("📟 Enigma : Rotation de la Ligne 1")

delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Positions :** R1:`{string.ascii_uppercase[st.session_state.off1]}` | R2:`{string.ascii_uppercase[st.session_state.off2]}` | R3:`{string.ascii_uppercase[st.session_state.off3]}`")
    st.code(f"Clair   : {st.session_state.text_in if st.session_state.text_in else '-'}")
    st.code(f"Chiffré : {st.session_state.text_out if st.session_state.text_out else '-'}")

    if st.button("⏪ Réinitialiser", use_container_width=True):
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
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_path_indices(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += string.ascii_uppercase[p[3]]

# --- DESSIN ---
def plot_enigma():
    alphabet = list(string.ascii_uppercase)
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    
    # CORRECTION ICI : 
    # Ligne 1 (Index 0) est liée au Rotor 1 (off1)
    # Ligne 2 (Index 1) est liée au Rotor 2 (off2)
    # Ligne 3 (Index 2) est liée au Rotor 3 (off3)
    # Ligne 4 (Index 3) est fixe (0)
    disp_offsets = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_path_indices(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        # Décalage pour le tracé des fils (lié à l'offset de la ligne du haut du stage)
        off = disp_offsets[stage] 
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        for i in range(26):
            is_active = (len(path) > 0 and (path[stage] + off) % 26 == i)
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            fig.add_trace(go.Scatter(
                x=[i - 0.18, i - 0.18, w[i] + 0.18, w[i] + 0.18], y=[y_top, h_y, h_y, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.3, showlegend=False, hoverinfo='skip'
            ))

    for l_idx, y_val in enumerate(levels):
        off = disp_offsets[l_idx]
        for i in range(26):
            active = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', 
                            line=dict(color="red" if active else "#ddd", width=2 if active else 1)),
                text=alphabet[(i - off) % 26], 
                textfont=dict(size=9, color="red" if active else "black", family="Arial Black"),
                showlegend=False
            ))

    fig.update_layout(height=550, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.5]))
    return fig

st.plotly_chart(plot_enigma(), use_container_width=True)

# --- SÉQUENCE POST-AFFICHAGE ---
if st.session_state.pressed_key:
    if delay > 0:
        time.sleep(delay)
    
    # Logique de cascade
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    
    st.session_state.pressed_key = None 
    st.rerun()
