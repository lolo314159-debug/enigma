import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Visualisation du Flux", layout="wide")

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

def plot_enigma_path():
    fig = go.Figure()
    levels = [2.1, 1.4, 0.7, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        y_start, y_end = levels[stage] - 0.1, levels[stage+1] + 0.1
        
        for i in range(n):
            target = current_wiring[i]
            # Vérification si ce fil fait partie du chemin actif
            is_on_path = (len(path) > 0 and path[stage] == i)
            
            color = "red" if is_on_path else "rgba(200, 200, 200, 0.3)"
            width = 4 if is_on_path else 1
            opacity = 1.0 if is_on_path else 0.4
            
            h_level = y_end + 0.05 + (i * (0.15 / n))
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_start, h_level, h_level, y_end],
                mode='lines', line=dict(color=color, width=width),
                opacity=opacity, hoverinfo='skip', showlegend=False
            ))

    # Dessin des bornes
    for l_idx, y_val in enumerate(levels):
        for i in range(n):
            # Surbrillance de la lettre si elle est dans le chemin
            is_active_letter = (len(path) > 0 and path[l_idx] == i)
            b_color = "red" if is_active_letter else "black"
            b_width = 2 if is_active_letter else 1
            f_color = "red" if is_active_letter else "black"

            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color=b_color, width=b_width)),
                text=alphabet[i], textfont=dict(size=10, family="Arial Black", color=f_color),
                showlegend=False
            ))

    fig.update_layout(
        height=500, margin=dict(l=10, r=10, t=0, b=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.3]),
        plot_bgcolor='white'
    )
    return fig

st.plotly_chart(plot_enigma_path(), use_container_width=True)

if st.session_state.pressed_key:
    st.success(f"Résultat : La lettre **{st.session_state.pressed_key}** devient **{alphabet[path[3]]}**")
