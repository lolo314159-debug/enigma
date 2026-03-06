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

# Permutations indépendantes
if 'r1_base' not in st.session_state:
    st.session_state.r1_base = generate_derangement()
    st.session_state.r2_base = generate_derangement()
    st.session_state.r3_base = generate_derangement()

# États des rotors et texte
if 'off1' not in st.session_state:
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.pressed_key = None
    st.session_state.text_in, st.session_state.text_out = "", ""

st.set_page_config(page_title="Enigma : Correction R2-R3", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (TRANSFERT RELATIF) ---
def get_path(key_char, o1, o2, o3):
    # Ligne 0 (Clavier fixe) -> Ligne 1 (Entrée R1)
    # On appuie sur une touche, le signal entre à l'index physique où se trouve la lettre
    idx0 = (alphabet.index(key_char) + o1) % 26
    
    # R1 : Entrée idx0 -> Sortie physique r1[idx0]
    out1 = st.session_state.r1_base[idx0]
    
    # R1 -> R2 : Le signal passe de la sortie de R1 à l'entrée de R2
    # Il faut compenser la différence de rotation entre les deux
    idx1 = (out1 + (o2 - o1)) % 26
    
    # R2 : Entrée idx1 -> Sortie physique r2[idx1]
    out2 = st.session_state.r2_base[idx1]
    
    # R2 -> R3 : Transfert relatif
    idx2 = (out2 + (o3 - o2)) % 26
    
    # R3 : Entrée idx2 -> Sortie physique r3[idx2]
    out3 = st.session_state.r3_base[idx2]
    
    # R3 -> Sortie fixe (Offset final pour revenir au tableau statique)
    idx3 = (out3 - o3) % 26
    
    return [idx0, idx1, idx2, idx3]

# --- 3. INTERFACE ET BOUTONS INDÉPENDANTS ---
st.title("📟 Enigma : Correction des liaisons R2-R3")
delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}`-`{alphabet[st.session_state.off2]}`-`{alphabet[st.session_state.off3]}`")
    st.info(f"**Clair :** `{st.session_state.text_in}`")
    st.success(f"**Chiffré :** `{st.session_state.text_out}`")

    c1, c2 = st.columns(2)
    if c1.button("⏪ Reset Positions & Texte", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.session_state.pressed_key = None
        st.rerun()
        
    if c2.button("🔄 Changer Permutations (Fils)", use_container_width=True):
        st.session_state.r1_base = generate_derangement()
        st.session_state.r2_base = generate_derangement()
        st.session_state.r3_base = generate_derangement()
        st.toast("Câblage interne modifié !")

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
                p = get_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- 4. GRAPHIQUE ---
def draw_enigma():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        y_t, y_b = levels[stage] - 0.15, levels[stage+1] + 0.15
        for i in range(26):
            # Détermination de l'activité du fil
            is_active = (len(path) > 0 and path[stage] == i)
            
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_t, y_t-0.1, y_b+0.1, y_b],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False
            ))

    for l_idx, y_val in enumerate(levels):
        o = offs[l_idx]
        for i in range(26):
            is_red = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', 
                            line=dict(color="red" if is_red else "#ccc", width=2 if is_red else 1)),
                text=alphabet[(i - o) % 26],
                textfont=dict(size=9, color="red" if is_red else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    return fig

st.plotly_chart(draw_enigma(), use_container_width=True)

# --- 5. DÉLAI ET ROTATION ---
if st.session_state.pressed_key:
    if delay > 0:
        time.sleep(delay)
    
    # Incrémentation cascade
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
            
    st.session_state.pressed_key = None 
    st.rerun()
