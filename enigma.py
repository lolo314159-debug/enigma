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

st.set_page_config(page_title="Enigma : Correction Trajet Continu", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (7 POINTS DE CONTACT PHYSIQUES) ---
def get_enigma_path(key_char, o1, o2, o3):
    # Rotor 1
    idx0 = (alphabet.index(key_char) + o1) % 26 # Entrée physique
    out1 = st.session_state.r1_base[idx0]        # Sortie physique (ex: 'Y')
    
    # Transfert R1 -> R2
    idx1 = (out1 + (o2 - o1)) % 26               # Nouvelle entrée après décalage
    out2 = st.session_state.r2_base[idx1]
    
    # Transfert R2 -> R3
    idx2 = (out2 + (o3 - o2)) % 26
    out3 = st.session_state.r3_base[idx2]
    
    # Sortie finale
    idx3 = (out3 - o3) % 26
    
    # On renvoie TOUS les points pour le tracé
    return [idx0, out1, idx1, out2, idx2, out3, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Correction du trajet continu")

# Rétablissement du curseur Timer
delay = st.sidebar.slider("Délai d'observation (sec)", 0.0, 5.0, 1.5, step=0.5)

col_log, col_kbd = st.columns([1, 1])
with col_log:
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}-{alphabet[st.session_state.off2]}-{alphabet[st.session_state.off3]}`")
    st.info(f"**Clair :** `{st.session_state.text_in}`")
    st.success(f"**Chiffré :** `{st.session_state.text_out}`")

    c1, c2 = st.columns(2)
    if c1.button("⏪ Reset Complet", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.session_state.pressed_key = None
        st.rerun()
    if c2.button("🔄 Changer Câblage", use_container_width=True):
        st.session_state.r1_base = generate_derangement()
        st.session_state.r2_base = generate_derangement()
        st.session_state.r3_base = generate_derangement()
        st.toast("Nouveau câblage généré !")

with col_kbd:
    for row in [["A","Z","E","R","T"], ["Q","S","D","F","G"], ["W","X","C","V","B"]]:
        cols = st.columns(5)
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[6]]

# --- 4. DESSIN DU CHEMIN ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3) if st.session_state.pressed_key else None

    for s in range(3):
        w = wirings[s]
        y_top, y_bot = levels[s] - 0.15, levels[s+1] + 0.15
        
        # Dessin des 26 fils par rotor
        active_in = path[s*2] if path else -1
        for i in range(26):
            is_active = (i == active_in)
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_top, y_top-0.1, y_bot+0.1, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False
            ))
        
        # AJOUT : Pont horizontal entre la sortie du rotor et l'entrée du suivant
        if path:
            x_exit = path[s*2 + 1]
            x_next_entry = path[s*2 + 2]
            fig.add_trace(go.Scatter(
                x=[x_exit, x_next_entry], y=[y_bot, y_bot],
                mode='lines', line=dict(color="red", width=4), showlegend=False
            ))

    # Dessin des cases de lettres
    for l_idx, y_val in enumerate(levels):
        for i in range(26):
            # Une case est rouge si elle est un point de SORTIE ou d'ENTRÉE sur cette ligne
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

# --- 5. ROTATION ET PAUSE ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    st.session_state.pressed_key = None
    st.rerun()
