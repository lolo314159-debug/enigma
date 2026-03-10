import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# --- 1. INITIALISATION ---
def generate_derangement():
    indices = list(range(26))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(26)): return indices

if 'r1_base' not in st.session_state:
    st.session_state.r1_base = generate_derangement()
    st.session_state.r2_base = generate_derangement()
    st.session_state.r3_base = generate_derangement()
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.text_in, st.session_state.text_out = "", ""
    st.session_state.pressed_key = None

st.set_page_config(page_title="Enigma : Clavier et Trajet OK", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (7 POINTS POUR UN CHEMIN SANS SAUT) ---
def get_enigma_path(key_char, o1, o2, o3):
    idx0 = (alphabet.index(key_char) + o1) % 26 # Entrée R1
    out1 = st.session_state.r1_base[idx0]        # Sortie physique R1
    idx1 = (out1 + (o2 - o1)) % 26               # Nouvelle entrée R2 (pont horizontal)
    out2 = st.session_state.r2_base[idx1]        # Sortie physique R2
    idx2 = (out2 + (o3 - o2)) % 26               # Nouvelle entrée R3 (pont horizontal)
    out3 = st.session_state.r3_base[idx2]        # Sortie physique R3
    idx3 = (out3 - o3) % 26                      # Sortie finale
    return [idx0, out1, idx1, out2, idx2, out3, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Correction du trajet et Clavier 26 touches")

# Retour du Timer
delay = st.sidebar.slider("Vitesse de rotation (sec)", 0.0, 5.0, 1.5, step=0.5)

col_log, col_kbd = st.columns([1, 1.2])
with col_log:
    st.write(f"**Rotors :** `{alphabet[st.session_state.off1]}-{alphabet[st.session_state.off2]}-{alphabet[st.session_state.off3]}`")
    st.info(f"**Clair :** `{st.session_state.text_in}`")
    st.success(f"**Chiffré :** `{st.session_state.text_out}`")
    if st.button("⏪ Reset Machine", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.session_state.pressed_key = None
        st.rerun()

with col_kbd:
    # Clavier AZERTY complet (26 lettres)
    rows = [
        ["A","Z","E","R","T","Y","U","I","O","P"],
        ["Q","S","D","F","G","H","J","K","L","M"],
        ["W","X","C","V","B","N"]
    ]
    for row in rows:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"key_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[6]]

# --- 4. DESSIN ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3) if st.session_state.pressed_key else None

    for s in range(3):
        w = wirings[s]
        y_top, y_bot = levels[s] - 0.15, levels[s+1] + 0.15
        
        # 1. Fils internes des rotors
        active_in = path[s*2] if path else -1
        for i in range(26):
            is_active = (i == active_in)
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_top, y_top-0.1, y_bot+0.1, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.15, showlegend=False
            ))
        
        # 2. PONT HORIZONTAL (Le signal repart bien de la case de sortie)
        if path:
            x_out = path[s*2 + 1]
            x_next_in = path[s*2 + 2]
            fig.add_trace(go.Scatter(
                x=[x_out, x_next_in], y=[y_bot, y_bot],
                mode='lines', line=dict(color="red", width=4), showlegend=False
            ))

    # 3. Blocs de lettres (Entrée et Sortie allumées sur chaque ligne)
    for l_idx, y_val in enumerate(levels):
        for i in range(26):
            is_red = False
            if path:
                if l_idx == 0 and i == path[0]: is_red = True
                if l_idx == 1 and (i == path[1] or i == path[2]): is_red = True
                if l_idx == 2 and (i == path[3] or i == path[4]): is_red = True
                if l_idx == 3 and (i == path[5] or i == path[6]): is_red = True

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color="red" if is_red else "#ccc", width=2 if is_red else 1)),
                text=alphabet[(i - offs[l_idx]) % 26],
                textfont=dict(size=9, color="red" if is_red else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    return fig

st.plotly_chart(draw_viz(), use_container_width=True)

# --- 5. FIN DE CYCLE ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    st.session_state.pressed_key = None
    st.rerun()
