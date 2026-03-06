import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# --- INITIALISATION ---
def generate_derangement():
    indices = list(range(26))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(26)): return indices

if 'r1_base' not in st.session_state:
    st.session_state.r1_base = generate_derangement()
    st.session_state.r2_base = generate_derangement()
    st.session_state.r3_base = generate_derangement()

# Variables de contrôle (Reset indépendant)
if 'off1' not in st.session_state:
    st.session_state.off1 = 0
    st.session_state.off2 = 0
    st.session_state.off3 = 0
    st.session_state.pressed_key = None
    st.session_state.text_in = ""
    st.session_state.text_out = ""

st.set_page_config(page_title="Enigma : Réinitialisation Précise", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- LOGIQUE DE CHEMINEMENT PHYSIQUE ---
def get_correct_path(key_char, o1, o2, o3):
    # 1. Entrée : Quelle case physique contient la lettre pressée ?
    idx0 = (alphabet.index(key_char) + o1) % 26
    
    # 2. Rotor 1 -> Rotor 2
    # Le signal sort du rotor 1 à la position phys_out1
    phys_out1 = st.session_state.r1_base[idx0]
    # Il entre dans le rotor 2 en tenant compte du décalage relatif entre R1 et R2
    idx1 = phys_out1 
    
    # 3. Rotor 2 -> Rotor 3
    # Le signal entre dans R2 à la position (phys_out1 + (o2-o1))
    idx2_in = (phys_out1 + (o2 - o1)) % 26
    phys_out2 = st.session_state.r2_base[idx2_in]
    idx2 = phys_out2
    
    # 4. Rotor 3 -> Sortie Fixe
    # Le signal entre dans R3 à la position (phys_out2 + (o3-o2))
    idx3_in = (phys_out2 + (o3 - o2)) % 26
    phys_out3 = st.session_state.r3_base[idx3_in]
    # La sortie finale est décalée par l'offset du dernier rotor vers le tableau fixe
    idx3 = (phys_out3 - o3) % 26
    
    return [idx0, idx1, idx2, idx3]

st.title("📟 Enigma : Flux Électrique et Reset Indépendant")

# --- INTERFACE ---
delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}`-`{alphabet[st.session_state.off2]}`-`{alphabet[st.session_state.off3]}`")
    st.code(f"Clair   : {st.session_state.text_in if st.session_state.text_in else '-'}")
    st.code(f"Chiffré : {st.session_state.text_out if st.session_state.text_out else '-'}")

    # DEUX BOUTONS DISTINCTS
    c1, c2 = st.columns(2)
    if c1.button("⏪ Reset Positions & Texte", use_container_width=True):
        st.session_state.off1 = 0
        st.session_state.off2 = 0
        st.session_state.off3 = 0
        st.session_state.text_in = ""
        st.session_state.text_out = ""
        st.session_state.pressed_key = None
        st.rerun()
        
    if c2.button("🔄 Changer les Permutations", use_container_width=True):
        st.session_state.r1_base = generate_derangement()
        st.session_state.r2_base = generate_derangement()
        st.session_state.r3_base = generate_derangement()
        st.toast("Fils internes modifiés !")

with col_kbd:
    # Clavier (simplifié pour l'exemple)
    for row in [["A", "Z", "E", "R", "T"], ["Q", "S", "D", "F", "G"], ["W", "X", "C", "V", "B"]]:
        cols = st.columns(5)
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"k_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_correct_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[3]]

# --- GRAPHIQUE ---
def draw_enigma():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    
    path = []
    if st.session_state.pressed_key:
        path = get_correct_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    # Dessin des fils
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    for stage in range(3):
        w = wirings[stage]
        y_t, y_b = levels[stage] - 0.15, levels[stage+1] + 0.15
        
        # Calcul du décalage d'entrée pour ce stage
        # Stage 0: entrée o1. Stage 1: entrée o2. Stage 2: entrée o3.
        current_in_off = offs[stage]
        next_in_off = offs[stage+1]
        
        for i in range(26):
            # Le signal est actif si on est sur le chemin calculé
            # Pour le stage 0, l'entrée est path[0]. Pour stage 1, c'est l'entrée de R2, etc.
            is_active = False
            if len(path) > 0:
                if stage == 0 and path[0] == i: is_active = True
                if stage == 1 and (path[1] + (offs[1]-offs[0])) % 26 == i: is_active = True
                if stage == 2 and (path[2] + (offs[2]-offs[1])) % 26 == i: is_active = True

            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_t, y_t-0.1, y_b+0.1, y_b],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False
            ))

    # Dessin des blocs de lettres
    for l_idx, y_val in enumerate(levels):
        o = offs[l_idx]
        for i in range(26):
            # Détermination de si la case est rouge
            is_red = False
            if len(path) > 0:
                if l_idx == 0 and path[0] == i: is_red = True
                if l_idx == 1 and path[1] == i: is_red = True
                if l_idx == 2 and path[2] == i: is_red = True
                if l_idx == 3 and path[3] == i: is_red = True

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color="red" if is_red else "#ccc", width=2 if is_red else 1)),
                text=alphabet[(i - o) % 26],
                textfont=dict(size=9, color="red" if is_red else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 25.5]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    return fig

st.plotly_chart(draw_enigma(), use_container_width=True)

# --- ROTATION ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    st.session_state.pressed_key = None 
    st.rerun()
