import streamlit as st
import plotly.graph_objects as go
import random
import string

# 1. Initialisation du session_state
if 'r1_base' not in st.session_state:
    def generate_derangement(n):
        indices = list(range(n))
        while True:
            random.shuffle(indices)
            if all(indices[i] != i for i in range(n)): return indices
    
    st.session_state.r1_base = generate_derangement(26)
    st.session_state.r2_base = generate_derangement(26)
    st.session_state.r3_base = generate_derangement(26)
    
    st.session_state.off1 = 0
    st.session_state.off2 = 0
    st.session_state.off3 = 0
    
    st.session_state.pressed_key = None
    st.session_state.text_in = ""
    st.session_state.text_out = ""

st.set_page_config(page_title="Enigma : Rotors Physiques", layout="wide")

st.markdown("<style>div.stButton > button {height: 30px; font-weight: bold;}</style>", unsafe_allow_html=True)
alphabet = list(string.ascii_uppercase)

# --- Logique de Chiffrement avec Décalage de l'Alphabet ---
def encrypt_letter(key_char):
    # Position d'entrée physique (0 à 25)
    idx = alphabet.index(key_char)
    
    # Passage à travers les rotors en tenant compte du décalage des lettres
    # Le signal entre sur la lettre affichée, mais le fil interne correspond à (idx + offset)
    def pass_rotor(input_idx, wiring, offset):
        contact_in = (input_idx + offset) % 26
        contact_out = wiring[contact_in]
        return (contact_out - offset) % 26

    idx = pass_rotor(idx, st.session_state.r1_base, st.session_state.off1)
    idx = pass_rotor(idx, st.session_state.r2_base, st.session_state.off2)
    idx = pass_rotor(idx, st.session_state.r3_base, st.session_state.off3)
    return idx

def reset_rotations():
    st.session_state.off1 = 0
    st.session_state.off2 = 0
    st.session_state.off3 = 0
    st.session_state.text_in = ""
    st.session_state.text_out = ""
    st.session_state.pressed_key = None

st.title("📟 Enigma : Décalage Visuel de l'Alphabet")

# --- ZONE D'AFFICHAGE ---
col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.write(f"**Positions (Fenêtres) :** R1: `{alphabet[st.session_state.off1]}` | R2: `{alphabet[st.session_state.off2]}` | R3: `{alphabet[st.session_state.off3]}`")
    area_in = st.empty()
    area_in.code(st.session_state.text_in if st.session_state.text_in else " ")
    area_out = st.empty()
    area_out.code(st.session_state.text_out if st.session_state.text_out else " ")
    
    c1, c2 = st.columns(2)
    c1.button("⏪ Remettre à 'A'", on_click=reset_rotations, use_container_width=True)
    if c2.button("🔄 Nouveau Câblage", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- CLAVIER ---
with col_kbd:
    rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["W", "X", "C", "V", "B", "N"]]
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, key=f"k_{key}", use_container_width=True):
                    # Rotation mécanique (cliquet)
                    st.session_state.off1 = (st.session_state.off1 + 1) % 26
                    if st.session_state.off1 == 0:
                        st.session_state.off2 = (st.session_state.off2 + 1) % 26
                    
                    st.session_state.pressed_key = key
                    st.session_state.text_in += key
                    res_idx = encrypt_letter(key)
                    st.session_state.text_out += alphabet[res_idx]
                    
                    area_in.code(st.session_state.text_in)
                    area_out.code(st.session_state.text_out)

# --- CALCUL DU CHEMIN POUR LE DESSIN ---
# On recalcule les étapes pour la mise en évidence
path = []
if st.session_state.pressed_key:
    def get_step_idx(input_idx, wiring, offset):
        contact_in = (input_idx + offset) % 26
        return wiring[contact_in], (wiring[contact_in] - offset) % 26

    idx_start = alphabet.index(st.session_state.pressed_key)
    _, idx1 = get_step_idx(idx_start, st.session_state.r1_base, st.session_state.off1)
    _, idx2 = get_step_idx(idx1, st.session_state.r2_base, st.session_state.off2)
    _, idx3 = get_step_idx(idx2, st.session_state.r3_base, st.session_state.off3)
    path = [idx_start, idx1, idx2, idx3]

# --- DESSIN ---
def plot_mechanical_enigma():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    levels = [2.2, 1.5, 0.8, 0.1]
    offsets = [st.session_state.off1, st.session_state.off2, st.session_state.off3]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    dx = 0.18

    for stage in range(3):
        w = wirings[stage]
        off = offsets[stage]
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        
        for i in range(26):
            # Le fil interne relie physiquement le contact 'i' au contact 'w[i]'
            # Mais visuellement, le contact 'i' correspond à la lettre (i-offset)
            is_active = (len(path) > 0 and (path[stage] + off) % 26 == i)
            
            target = w[i]
            # On dessine les fils de manière fixe entre les indices physiques 0-25
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx], y=[y_top, h_y, h_y, y_bot],
                mode='lines', line=dict(color="red" if is_active else colors[i % 10], width=5 if is_active else 1.2),
                opacity=1.0 if is_active else 0.25, showlegend=False, hoverinfo='skip'
            ))

    # Bornes avec Alphabet Décalé
    for l_idx, y_val in enumerate(levels):
        # L'alphabet affiché dépend de l'offset du rotor concerné
        # Niveau 0: fixe, Niveau 1: décalé par off1, etc.
        current_off = offsets[l_idx-1] if l_idx > 0 else 0
        if l_idx == 0: current_off = 0 # Entrée fixe
        elif l_idx == 1: current_off = st.session_state.off1
        elif l_idx == 2: current_off = st.session_state.off2
        else: current_off = st.session_state.off3

        for i in range(26):
            # La lettre affichée à la position physique 'i' est (i - offset)
            char_idx = (i - current_off) % 26
            is_active = (len(path) > 0 and path[l_idx] == i) # Ici on utilise l'index de fenêtre
            
            # Correction visuelle pour que la lettre active soit celle du chemin
            is_active_letter = (len(path) > 0 and path[l_idx] == i)

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=20, color='white', 
                            line=dict(color="red" if is_active_letter else "#999", width=2 if is_active_letter else 1)),
                text=alphabet[char_idx], 
                textfont=dict(size=10, family="Arial Black", color="red" if is_active_letter else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.5]),
                      plot_bgcolor='white')
    return fig

st.plotly_chart(plot_mechanical_enigma(), use_container_width=True)
