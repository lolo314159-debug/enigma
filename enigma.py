import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Flux Coloré", layout="wide")

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

if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.session_state.pressed_key = None

# --- Clavier AZERTY ---
st.write("### ⌨️ Appuyez sur une touche pour voir le chemin")
rows = [["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
        ["W", "X", "C", "V", "B", "N"]]

_, clavier_col, _ = st.columns([1, 2, 1])
with clavier_col:
    for row in rows:
        cols = st.columns(10)
        for i, key in enumerate(row):
            with cols[i]:
                if st.button(key, key=f"k_{key}", use_container_width=True):
                    st.session_state.pressed_key = key

# --- Calcul du chemin ---
path = []
if st.session_state.pressed_key:
    idx0 = alphabet.index(st.session_state.pressed_key)
    idx1 = st.session_state.r1[idx0]
    idx2 = st.session_state.r2[idx1]
    idx3 = st.session_state.r3[idx2]
    path = [idx0, idx1, idx2, idx3]

def plot_enigma_vivid():
    fig = go.Figure()
    # Palette de couleurs pour les fils non-actifs
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    
    levels = [2.1, 1.4, 0.7, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        y_start, y_end = levels[stage] - 0.1, levels[stage+1] + 0.1
        
        for i in range(n):
            target = current_wiring[i]
            is_on_path = (len(path) > 0 and path[stage] == i)
            
            # Paramètres visuels différenciés
            if is_on_path:
                color = "red"
                width = 5  # Très épais
                opacity = 1.0
            else:
                color = colors[i % len(colors)]
                width = 1  # Fin
                opacity = 0.4 # Visible mais en retrait

            h_level = y_end + 0.05 + (i * (0.15 / n))
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_start, h_level, h_level, y_end],
                mode='lines', line=dict(color=color, width=width),
                opacity=opacity, hoverinfo='skip', showlegend=False
            ))

    # Dessin des bornes (Lettres)
    for l_idx, y_val in enumerate(levels):
        for i in range(n):
            is_active_letter = (len(path) > 0 and path[l_idx] == i)
            # Bordure rouge si active, sinon grise
            b_color = "red" if is_active_letter else "#888"
            b_width = 3 if is_active_letter else 1
            f_color = "red" if is_active_letter else "black"

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color=b_color, width=b_width)),
                text=alphabet[i], textfont=dict(size=10, family="Arial Black", color=f_color),
                showlegend=False
            ))

    fig.update_layout(
        height=500, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.3]),
        plot_bgcolor='white'
    )
    return fig

st.plotly_chart(plot_enigma_vivid(), use_container_width=True)

if st.session_state.pressed_key:
    st.success(f"Signal : **{st.session_state.pressed_key}** ➔ Rotor1 ➔ Rotor2 ➔ Rotor3 ➔ **{alphabet[path[3]]}**")
