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

st.set_page_config(page_title="Enigma : Correction Définitive", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (FLUX PHYSIQUE CONTINU) ---
def get_enigma_path(key_char, o1, o2, o3):
    # Entrée : Position de la lettre sur la Ligne 1
    idx0 = (alphabet.index(key_char) + o1) % 26
    
    # Rotor 1 : Entrée idx0 -> Sortie out1
    out1 = st.session_state.r1_base[idx0]
    
    # Transfert R1 -> R2 (Ligne 2)
    # On calcule l'index physique sur la ligne 2 en compensant la rotation
    idx1 = (out1 + (o2 - o1)) % 26
    out2 = st.session_state.r2_base[idx1]
    
    # Transfert R2 -> R3 (Ligne 3)
    idx2 = (out2 + (o3 - o2)) % 26
    out3 = st.session_state.r3_base[idx2]
    
    # Transfert R3 -> Sortie Fixe (Ligne 4)
    idx3 = (out3 - o3) % 26
    
    # On stocke les points de passage pour l'affichage rouge
    return [idx0, idx1, idx2, idx3]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Correction du câblage R2-R3")

col_log, col_kbd = st.columns([1, 1])
with col_log:
    st.write(f"**Rotors :** `{alphabet[st.session_state.off1]}-{alphabet[st.session_state.off2]}-{alphabet[st.session_state.off3]}`")
    st.info(f"**Entrée :** `{st.session_state.get('text_in', '')}`")
    st.success(f"**Sortie :** `{st.session_state.get('text_out', '')}`")

    c1, c2 = st.columns(2)
    if c1.button("⏪ Reset Rotors & Texte"):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.session_state.pressed_key = None
        st.rerun()
    if c2.button("🔄 Changer Permutations"):
        st.session_state.r1_base = generate_derangement()
        st.session_state.r2_base = generate_derangement()
        st.session_state.r3_base = generate_derangement()
        st.toast("Nouveau câblage interne généré")

with col_kbd:
    # Clavier compact
    for row in [["A","Z","E","R","T"], ["Q","S","D","F","G"], ["W","X","C","V","B"]]:
        cols = st.columns(5)
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- 4. DESSIN ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    
    path = []
    if st.session_state.pressed_key:
        path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for s in range(3):
        w = wirings[s]
        y_top, y_bot = levels[s] - 0.15, levels[s+1] + 0.15
        active_in = path[s] if path else -1
        
        for i in range(26):
            is_active = (i == active_in)
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_top, y_top-0.1, y_bot+0.1, y_bot],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False
            ))

    for l_idx, y_val in enumerate(levels):
        for i in range(26):
            is_red = (path and path[l_idx] == i)
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
    time.sleep(2) # Temps d'observation
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    st.session_state.pressed_key = None
    st.rerun()
