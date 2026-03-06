import streamlit as st
import plotly.graph_objects as go
import random
import string

# 1. Initialisation PRIORITAIRE du session_state
if 'r1' not in st.session_state:
    def generate_derangement(n):
        indices = list(range(n))
        while True:
            random.shuffle(indices)
            if all(indices[i] != i for i in range(n)): return indices
        
    st.session_state.r1 = generate_derangement(26)
    st.session_state.r2 = generate_derangement(26)
    st.session_state.r3 = generate_derangement(26)
    st.session_state.pressed_key = None
    st.session_state.text_in = ""
    st.session_state.text_out = ""

st.set_page_config(page_title="Enigma Final", layout="wide")

# CSS pour boutons compacts
st.markdown("""
    <style>
    div.stButton > button {
        padding: 0px !important; font-size: 12px !important;
        height: 28px !important; min-width: 28px !important;
    }
    </style>
    """, unsafe_allow_html=True)

alphabet = list(string.ascii_uppercase)

# --- Fonctions de contrôle ---
def clear_text():
    st.session_state.text_in = ""
    st.session_state.text_out = ""
    st.session_state.pressed_key = None

def new_rotors():
    indices = list(range(26))
    def derange():
        idx = list(range(26))
        while True:
            random.shuffle(idx)
            if all(idx[i] != i for i in range(26)): return idx
    st.session_state.r1 = derange()
    st.session_state.r2 = derange()
    st.session_state.r3 = derange()
    clear_text()

# --- Interface Clavier & Logs ---
st.title("📟 Simulateur Enigma")

col_log, col_kbd = st.columns([1, 1])

with col_log:
    st.text_input("Texte Clair", value=st.session_state.text_in, disabled=True)
    st.text_input("Texte Chiffré", value=st.session_state.text_out, disabled=True)
    c1, c2 = st.columns(2)
    c1.button("🗑️ Effacer Texte", on_click=clear_text, use_container_width=True)
    c2.button("🔄 Nouveaux Rotors", on_click=new_rotors, use_container_width=True)

with col_kbd:
    rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
            ["W", "X", "C", "V", "B", "N"]]
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, key=f"k_{key}", use_container_width=True):
                    st.session_state.pressed_key = key
                    st.session_state.text_in += key
                    # Chiffrement
                    i1 = st.session_state.r1[alphabet.index(key)]
                    i2 = st.session_state.r2[i1]
                    i3 = st.session_state.r3[i2]
                    st.session_state.text_out += alphabet[i3]

# --- Calcul du chemin ---
path = []
if st.session_state.pressed_key:
    idx0 = alphabet.index(st.session_state.pressed_key)
    idx1 = st.session_state.r1[idx0]
    idx2 = st.session_state.r2[idx1]
    idx3 = st.session_state.r3[idx2]
    path = [idx0, idx1, idx2, idx3]

# --- Schéma ---
def plot_final():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    levels = [2.2, 1.5, 0.8, 0.1] # Espacement aéré
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.18 # Décalage horizontal

    for stage in range(3):
        w = wirings[stage]
        y_top, y_bot = levels[stage] - 0.15, levels[stage+1] + 0.15
        v_gap = y_top - y_bot
        
        for i in range(26):
            is_active = (len(path) > 0 and path[stage] == i)
            # Palier horizontal centré verticalement
            h_y = y_bot + (v_gap * 0.1) + (i * (v_gap * 0.8 / 26))
            
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, w[i] + dx, w[i] + dx],
                y=[y_top, h_y, h_y, y_bot],
                mode='lines',
                line=dict(color="red" if is_active else colors[i % 10], 
                          width=5 if is_active else 1.2),
                opacity=1.0 if is_active else 0.35,
                showlegend=False, hoverinfo='skip'
            ))

    # Bornes (Lettres)
    for l_idx, y_val in enumerate(levels):
        for i in range(26):
            is_active = (len(path) > 0 and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=20, color='white', 
                            line=dict(color="red" if is_active else "#999", width=2 if is_active else 1)),
                text=alphabet[i], textfont=dict(size=10, family="Arial Black", color="red" if is_active else "black"),
                showlegend=False
            ))

    fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.5]),
                      plot_bgcolor='white')
    return fig

st.plotly_chart(plot_final(), use_container_width=True)
