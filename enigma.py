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

# États (Reset indépendant)
if 'off1' not in st.session_state:
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.pressed_key = None
    st.session_state.text_in, st.session_state.text_out = "", ""

st.set_page_config(page_title="Enigma : Correction R2-R3 Finale", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (TRANSFERT PHYSIQUE) ---
def get_full_path(key_char, o1, o2, o3):
    # Position de la lettre sur la Ligne 1 (Rotor 1)
    p0 = (alphabet.index(key_char) + o1) % 26
    
    # Sortie physique du Rotor 1
    p1_out = st.session_state.r1_base[p0]
    
    # Arrivée sur le Rotor 2 : on ajuste selon la différence de rotation
    p1_in_r2 = (p1_out + (o2 - o1)) % 26
    
    # Sortie physique du Rotor 2
    p2_out = st.session_state.r2_base[p1_in_r2]
    
    # Arrivée sur le Rotor 3
    p2_in_r3 = (p2_out + (o3 - o2)) % 26
    
    # Sortie physique du Rotor 3
    p3_out = st.session_state.r3_base[p2_in_r3]
    
    # Sortie finale vers le tableau fixe
    p3_final = (p3_out - o3) % 26
    
    # On renvoie les points de contact pour le dessin
    # [Entrée R1, Sortie R1, Sortie R2, Sortie R3]
    return [p0, p1_out, p2_out, p3_final]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Correction des Liaisons et Resets")
delay = st.sidebar.slider("Délai d'observation (sec)", 0, 10, 3)

col_log, col_kbd = st.columns([1, 1])

with col_log:
    # Protection contre AttributeError vue sur image_ce38c7.png
    t_in = st.session_state.get('text_in', "")
    t_out = st.session_state.get('text_out', "")
    
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}`-`{alphabet[st.session_state.off2]}`-`{alphabet[st.session_state.off3]}`")
    st.info(f"**Clair :** `{t_in}`")
    st.success(f"**Chiffré :** `{t_out}`")

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
                path = get_full_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[path[3]]

# --- 4. GRAPHIQUE ---
def draw_enigma():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1]
    offs = [st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = []
    if st.session_state.pressed_key:
        path = get_full_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3)

    for stage in range(3):
        w = wirings[stage]
        y_t, y_b = levels[stage] - 0.15, levels[stage+1] + 0.15
        
        # Le point de départ du fil dépend du rotor précédent
        # On définit quel index i est "actif" pour ce rotor précis
        active_idx = -1
        if len(path) > 0:
            if stage == 0: active_idx = path[0]
            if stage == 1: active_idx = (path[1] + (offs[1] - offs[0])) % 26
            if stage == 2: active_idx = (path[2] + (offs[2] - offs[1])) % 26

        for i in range(26):
            is_active = (active_idx == i)
            # Un fil relie physiquement l'entrée i du rotor à sa sortie w[i]
            fig.add_trace(go.Scatter(
                x=[i, i, w[i], w[i]], y=[y_t, y_t-0.1, y_b+0.1, y_b],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.2, showlegend=False
            ))

    # Dessin des blocs de lettres
    for l_idx, y_val in enumerate(levels):
        o = offs[l_idx]
        for i in range(26):
            # Une case est rouge si elle correspond à un point du path
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

# --- 5. ROTATION ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    if st.session_state.off1 == 0:
        st.session_state.off2 = (st.session_state.off2 + 1) % 26
        if st.session_state.off2 == 0:
            st.session_state.off3 = (st.session_state.off3 + 1) % 26
    st.session_state.pressed_key = None 
    st.rerun()
