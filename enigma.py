import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Chiffrement Complet", layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        padding: 0px !important; font-size: 12px !important;
        height: 25px !important; min-width: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)): return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

# Initialisation du session_state
if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.session_state.pressed_key = None
    st.session_state.text_in = ""
    st.session_state.text_out = ""

# --- Fonctions de gestion ---
def reset_path():
    st.session_state.pressed_key = None

def clear_all():
    st.session_state.text_in = ""
    st.session_state.text_out = ""
    st.session_state.pressed_key = None

# --- Clavier AZERTY ---
st.write("### ⌨️ Clavier et Contrôles")
rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
        ["W", "X", "C", "V", "B", "N"]]

col_clavier, col_ctrl = st.columns([3, 1])

with col_clavier:
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, key=f"k_{key}", use_container_width=True):
                    st.session_state.pressed_key = key
                    st.session_state.text_in += key
                    # Calcul du codage
                    idx0 = alphabet.index(key)
                    idx1 = st.session_state.r1[idx0]
                    idx2 = st.session_state.r2[idx1]
                    idx3 = st.session_state.r3[idx2]
                    st.session_state.text_out += alphabet[idx3]

with col_ctrl:
    st.button("🔴 Effacer chemin", on_click=reset_path, use_container_width=True)
    st.button("🗑️ Reset Texte", on_click=clear_all, use_container_width=True)
    if st.button('🔄 Recâbler Rotors', use_container_width=True):
        for r in ['r1', 'r2', 'r3']: st.session_state[r] = generate_derangement(n)
        clear_all()
        st.rerun()

# --- Zone de texte ---
st.info(f"**Texte Clair :** `{st.session_state.text_in}`")
st.success(f"**Texte Chiffré :** `{st.session_state.text_out}`")

# --- Calcul du chemin pour le schéma ---
path = []
if st.session_state.pressed_key:
    idx0 = alphabet.index(st.session_state.pressed_key)
    idx1 = st.session_state.r1[idx0]
    idx2 = st.session_state.r2[idx1]
    idx3 = st.session_state.r3[idx2]
    path = [idx0, idx1, idx2, idx3]

def plot_enigma_final():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    levels = [2.4, 1.6, 0.8, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        y_top_exit, y_bottom_entry = levels[stage] - 0.12, levels[stage+1] + 0.12
        v_space = y_top_exit - y_bottom_entry
        
        for i in range(n):
            target = current_wiring[i]
            is_on_path = (len(path) > 0 and path[stage] == i)
            
            h_level = y_bottom_entry + (v_space * 0.1) + (i * (v_space * 0.8 / n))
            color = "red" if is_on_path else colors[i % len(colors)]
            width = 5 if is_on_path else 1.2
            opacity = 1.0 if is_on_path else 0.3

            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_top_exit, h_level, h_level, y_bottom_entry],
                mode='lines', line=dict(color=color, width=width),
                opacity=opacity, hoverinfo='skip', showlegend=False
            ))

    for l_idx, y_val in enumerate(levels):
        for i in range(n):
            is_active_letter = (len(path) > 0 and path[l_idx] == i)
            b_color = "red" if is_active_letter else "#666"
            b_width = 3 if is_active_letter else 1
            f_color = "red" if is_active_letter else "black"

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=20, color='white', line=dict(color=b_color, width=b_width)),
                text=alphabet[i], textfont=dict(size=10, family="Arial Black", color=f_color),
                showlegend=False
            ))

    fig.update_layout(
        height=550, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 2.7]),
        plot_bgcolor='white'
    )
    return fig

st.plotly_chart(plot_enigma_final(), use_container_width=True)
