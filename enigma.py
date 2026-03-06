import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# 1. Initialisation robuste
def init_session():
    def generate_derangement(n):
        indices = list(range(n))
        while True:
            random.shuffle(indices)
            if all(indices[i] != i for i in range(n)): return indices
    
    if 'r1_base' not in st.session_state:
        st.session_state.r1_base = generate_derangement(26)
        st.session_state.r2_base = generate_derangement(26)
        st.session_state.r3_base = generate_derangement(26)
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.pressed_key = None
        st.session_state.text_in, st.session_state.text_out = "", ""

init_session()

st.set_page_config(page_title="Enigma : Correction Finale", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- Logique de Calcul du Chemin Physique ---
def get_clean_path(key_char, o1, o2, o3):
    # La lettre pressée est à une position physique i sur la ligne 1
    # Exemple: Si off1=1 (B en première case), 'A' est à la position 25
    idx0 = (alphabet.index(key_char) + o1) % 26
    
    # Le signal traverse le rotor 1 (fil physique de idx0 vers r1[idx0])
    idx1 = st.session_state.r1_base[idx0]
    
    # Entre le rotor 1 et 2, il y a un décalage de position relative
    idx2 = st.session_state.r2_base[(idx1 + (o2 - o1)) % 26]
    
    # Entre le rotor 2 et 3
    idx3 = st.session_state.r3_base[(idx2 + (o3 - o2)) % 26]
    
    return [idx0, idx1, idx2, idx3]

st.title("📟 Enigma : Correction du Flux Électrique")

delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)

col_log, col_kbd = st.columns([1, 1])

with col_log:
    # Utilisation de .get() pour éviter l'AttributeError de l'image
    t_in = st.session_state.get('text_in', "")
    t_out = st.session_state.get('text_out', "")
    
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}`-`{alphabet[st.session_state.off2]}`-`{alphabet[st.session_state.off3]}`")
    st.info(f"**Texte Clair :** `{t_in if t_in else ' '}`")
    st.success(f"**Chiffré :** `{t_out if t_out else ' '}`")

    if st.button("🔄 Nouveau Câblage & Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
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
                path = get_clean_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                # La sortie est la lettre à la position path[3] sur la ligne fixe (offset 0)
                st.session_state.text_out += alphabet[path[3]]

# --- DESSIN DU GRAPHIQUE ---
def draw_enigma():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_clean_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        y_t, y_b = levels[stage] - 0.15, levels[stage+1] + 0.15
        for i in range(26):
            active = (len(path) > 0 and path[stage] == i)
            # Le fil relie physiquement la position i à la position w[i]
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_t, y_t-0.1, y_b+0.1, y_b],
                mode='lines', line=dict(color="red" if active else "#eee", width=4 if active else 1),
                opacity=1.0 if active else 0.2, showlegend=False
            ))

    for l_idx, y_val in enumerate(levels):
        o = offs[l_idx]
        for i in range(26):
            # Une case est active si son index physique est dans le path
            is_active_pos = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color="red" if is_active_pos else "#ccc", width=2 if is_active_pos else 1)),
                text=alphabet[(i - o) % 26],
                textfont=dict(size=9, color="red" if is_active_pos else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 25.5]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    return fig

st.plotly_chart(draw_enigma(), use_container_width=True)

# --- GESTION DU DÉLAI ET ROTATION ---
if st.session_state.pressed_key:
    if delay > 0:
        time.sleep(delay)
    
    # Rotation cascade
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
            
    st.session_state.pressed_key = None 
    st.rerun()
