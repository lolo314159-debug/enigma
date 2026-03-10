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

st.set_page_config(page_title="Enigma : Modèle Visuel", layout="wide")
alphabet = string.ascii_uppercase

# --- 2. LOGIQUE DE SIGNAL ---
def get_enigma_path(key_char, o1, o2, o3):
    idx0 = alphabet.index(key_char)
    # R1 (rotatif)
    idx1 = (st.session_state.r1_base[(idx0 + o1) % 26] - o1) % 26
    # R2 et R3
    idx2 = (st.session_state.r2_base[(idx1 + o2) % 26] - o2) % 26
    idx3 = (st.session_state.r3_base[(idx2 + o3) % 26] - o3) % 26
    return [idx0, idx1, idx2, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Visualisation physique")
delay = st.sidebar.slider("Vitesse du signal (sec)", 0.0, 5.0, 1.0, step=0.5)

col_log, col_kbd = st.columns([1, 1.3])
with col_log:
    st.write(f"**Rotations :** R1: `{st.session_state.off1}` | R2: `{st.session_state.off2}` | R3: `{st.session_state.off3}`")
    if st.button("⏪ Reset Machine", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.rerun()

with col_kbd:
    rows = [["A","Z","E","R","T","Y","U","I","O","P"], ["Q","S","D","F","G","H","J","K","L","M"], ["W","X","C","V","B","N"]]
    for row in rows:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- 4. VISUALISATION AMÉLIORÉE ---
def draw_viz():
    fig = go.Figure()
    # Espace réduit entre les lignes (gap de 0.5 au lieu de 0.7)
    levels = [1.8, 1.3, 0.8, 0.3]
    offsets = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3]
    
    path = None
    if st.session_state.pressed_key:
        path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    if path:
        for s in range(3):
            fig.add_trace(go.Scatter(
                x=[path[s], path[s+1]], y=[levels[s], levels[s+1]],
                mode='lines', line=dict(color="#FF4B4B", width=6), showlegend=False
            ))

    for l_idx, y_val in enumerate(levels):
        off = offsets[l_idx]
        for i in range(26):
            char_to_show = alphabet[(i + off) % 26]
            is_active = (path and path[l_idx] == i)
            
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                # Lettres plus grandes
                marker=dict(symbol='square', size=28, color='white', 
                            line=dict(color="#FF4B4B" if is_active else "#ddd", width=3 if is_active else 1)),
                text=char_to_show,
                textfont=dict(size=14, color="#FF4B4B" if is_active else "black", weight="bold"),
                showlegend=False
            ))

    fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    return fig

st.plotly_chart(draw_viz(), use_container_width=True)

# Explication textuelle
st.markdown("""
**Note pédagogique :** Le schéma représente le flux électrique traversant les rotors. 
La première rangée (Clavier) est fixe. La seconde rangée illustre la rotation du **Rotor 1** : 
le déplacement de l'alphabet à chaque pression de touche modifie le point d'entrée du signal 
dans le câblage interne, changeant ainsi la lettre de sortie à chaque cycle.
""")

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
