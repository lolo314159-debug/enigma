import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# 1. Initialisation du moteur Enigma
if 'r1_base' not in st.session_state:
    def generate_derangement(n):
        indices = list(range(n))
        while True:
            random.shuffle(indices)
            if all(indices[i] != i for i in range(n)): return indices
    
    # Câblages internes fixes
    st.session_state.r1_base = generate_derangement(26)
    st.session_state.r2_base = generate_derangement(26)
    st.session_state.r3_base = generate_derangement(26)
    
    # Offsets (positions) des 3 rotors
    st.session_state.off1 = 0
    st.session_state.off2 = 0
    st.session_state.off3 = 0
    
    st.session_state.pressed_key = None
    st.session_state.text_in = ""
    st.session_state.text_out = ""

st.set_page_config(page_title="Enigma : Cascade des 3 Rotors", layout="wide")

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

st.title("📟 Enigma : Mécanique des 3 Rotors en Cascade")

# Sidebar pour le délai d'observation
delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)
st.sidebar.write(f"Positions : {string.ascii_uppercase[st.session_state.off1]}{string.ascii_uppercase[st.session_state.off2]}{string.ascii_uppercase[st.session_state.off3]}")

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Positions Actuelles :** R1:`{string.ascii_uppercase[st.session_state.off1]}` | R2:`{string.ascii_uppercase[st.session_state.off2]}` | R3:`{string.ascii_uppercase[st.session_state.off3]}`")
    st.code(f"Texte Clair   : {st.session_state.text_in if st.session_state.text_in else '-'}")
    st.code(f"Texte Chiffré : {st.session_state.text_out if st.session_state.text_out else '-'}")

    if st.button("⏪ Réinitialiser Positions & Texte", use_container_width=True):
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
                # Calcul avec les positions AVANT rotation
                p = get_path_indices(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += string.ascii_uppercase[p[3]]

# --- DESSIN DES ROTORS ---
def plot_enigma():
    alphabet = list(string.ascii_uppercase)
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    
    # Offsets visuels pour chaque ligne d'alphabet
    # Ligne 0 (Clavier) : Fixe
    # Ligne 1 (Entrée R1) : off1
    # Ligne 2 (Entrée R2) : off2
    # Ligne 3 (Entrée R3) : off3
    disp_offsets = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_path_indices(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        # Décalage interne du rotor pour le dessin des fils
        off = disp_offsets[stage+1] 
        
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        for i in range(26):
            is_active = (len(path) > 0 and (path[stage] + off) % 26 == i)
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            fig.add_trace(go.Scatter(
                x=[i - 0.18, i - 0.18, w[i] + 0.18, w[i] + 0.18], y=[y_top, h_y, h_y, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#f0f0f0", width=4 if is_active else 1),
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

# --- GESTION DU DÉLAI ET CASCADE DES ROTORS ---
if st.session_state.pressed_key:
    if delay > 0:
        time.sleep(delay)
    
    # 1. Le Rotor 1 avance toujours
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    
    # 2. Si le Rotor 1 a fait un tour complet, le Rotor 2 avance
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        
        # 3. Si le Rotor 2 a fait un tour complet, le Rotor 3 avance
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    
    # Effacement du chemin et rafraîchissement
    st.session_state.pressed_key = None 
    st.rerun()
