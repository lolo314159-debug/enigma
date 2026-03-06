import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma Compact", layout="wide")

# CSS pour un clavier ultra-compact
st.markdown("""
    <style>
    div.stButton > button {
        padding: 0px !important;
        font-size: 12px !important;
        height: 25px !important;
        min-width: 25px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logique Enigma ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)): return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.session_state.pressed_key = None

# --- Clavier AZERTY Compact ---
st.write("### ⌨️ Clavier")
rows = [
    ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
    ["W", "X", "C", "V", "B", "N"]
]

# On centre le clavier
_, clavier_col, _ = st.columns([1, 2, 1])
with clavier_col:
    for row in rows:
        cols = st.columns(10) # Toujours 10 colonnes pour l'alignement
        for i, key in enumerate(row):
            with cols[i]: # On remplit à partir de la gauche
                if st.button(key, key=f"k_{key}", use_container_width=True):
                    st.session_state.pressed_key = key

if st.button('🔄 Reset Rotors'):
    for r in ['r1', 'r2', 'r3']: st.session_state[r] = generate_derangement(n)
    st.rerun()

# --- Schéma Compact ---
def plot_enigma():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    
    levels = [2.1, 1.4, 0.7, 0] # Espacement vertical réduit
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        y_start, y_end = levels[stage] - 0.1, levels[stage+1] + 0.1
        
        for i in range(n):
            target = current_wiring[i]
            # Couleur vive si c'est la lettre pressée, sinon gris clair
            is_active = (stage == 0 and alphabet[i] == st.session_state.pressed_key)
            # (Note: La logique de suivi du chemin sur 3 rotors peut être ajoutée ensuite)
            color = colors[i % len(colors)]
            
            h_level = y_end + 0.05 + (i * (0.15 / n))
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_start, h_level, h_level, y_end],
                mode='lines', line=dict(color=color, width=1.5),
                hoverinfo='skip', showlegend=False
            ))

    # Bornes (Lettres)
    for y_val in levels:
        for i in range(n):
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=16, color='white', line=dict(color='#666', width=1)),
                text=alphabet[i], textfont=dict(size=9, family="Arial Black"),
                showlegend=False
            ))

    fig.update_layout(
        height=450, # Très compact
        margin=dict(l=10, r=10, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.3]),
        plot_bgcolor='white'
    )
    return fig

st.plotly_chart(plot_enigma(), use_container_width=True)
