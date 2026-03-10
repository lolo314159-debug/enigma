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

st.set_page_config(page_title="Enigma : Alphabet Roulant", layout="wide")
alphabet = string.ascii_uppercase

# --- 2. LOGIQUE DE CHIFFREMENT ---
def get_enigma_path(key_char, o1, o2, o3):
    # La lettre pressée correspond à un index fixe (0-25) sur le clavier
    idx0 = alphabet.index(key_char)
    
    # Pour chaque rotor, on calcule la sortie en fonction de l'alphabet décalé
    # C'est ici que la rotation (offset) impacte le résultat
    idx1 = (st.session_state.r1_base[(idx0 + o1) % 26] - o1) % 26
    idx2 = (st.session_state.r2_base[(idx1 + o2) % 26] - o2) % 26
    idx3 = (st.session_state.r3_base[(idx2 + o3) % 26] - o3) % 26
    
    return [idx0, idx1, idx2, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Rotation visuelle et Clavier complet")

col_log, col_kbd = st.columns([1, 1.3])
with col_log:
    st.write(f"**Positions (Offsets) :** `{st.session_state.off1} | {st.session_state.off2} | {st.session_state.off3}`")
    st.info(f"**Entrée :** `{st.session_state.text_in}`")
    st.success(f"**Sortie :** `{st.session_state.text_out}`")
    if st.button("⏪ Reset Machine", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.rerun()

with col_kbd:
    # Clavier AZERTY 26 touches (complet)
    rows = [["A","Z","E","R","T","Y","U","I","O","P"], 
            ["Q","S","D","F","G","H","J","K","L","M"], 
            ["W","X","C","V","B","N"]]
    for row in rows:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- 4. VISUALISATION (ALPHABET QUI TOURNE) ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offsets = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3]
    
    path = None
    if st.session_state.pressed_key:
        path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    # 1. Dessin des lignes de contact (Fils rouges)
    if path:
        for s in range(3):
            fig.add_trace(go.Scatter(
                x=[path[s], path[s+1]], y=[levels[s], levels[s+1]],
                mode='lines', line=dict(color="red", width=4), showlegend=False
            ))

    # 2. Dessin des lettres défilantes
    for l_idx, y_val in enumerate(levels):
        off = offsets[l_idx]
        for i in range(26):
            # C'est ici que l'alphabet "tourne" : la lettre affichée à l'index i change
            char_to_show = alphabet[(i + off) % 26]
            is_active = (path and path[l_idx] == i)
            
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=20, color='white', 
                            line=dict(color="red" if is_active else "#eee", width=2 if is_active else 1)),
                text=char_to_show,
                textfont=dict(size=10, color="red" if is_active else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    return fig

st.plotly_chart(draw_viz(), use_container_width=True)

# --- 5. LOGIQUE DE ROTATION (APRÈS CHAQUE TOUCHE) ---
if st.session_state.pressed_key:
    time.sleep(0.8) # Petit temps pour voir le chemin
    # Le rotor 1 tourne à chaque fois
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    # Si le rotor 1 fait un tour, le rotor 2 tourne (double-step simplifié)
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    
    st.session_state.pressed_key = None
    st.rerun()
