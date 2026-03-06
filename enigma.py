import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Rotor Enigma - Sans Invariants", layout="wide")

st.title("🛡️ Rotor Enigma : Interdiction des Invariants")
st.info("Conformément à la réalité historique, ce générateur garantit qu'aucune lettre n'est reliée à elle-même.")

# --- Logique de Dérangement (Permutation sans point fixe) ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        # On vérifie si un élément est à sa propre place (invariant)
        if all(indices[i] != i for i in range(n)):
            return indices

# 1. Initialisation
alphabet = list(string.ascii_uppercase)
n = len(alphabet)

if 'wiring' not in st.session_state:
    st.session_state.wiring = generate_derangement(n)

if st.button('🔄 Générer une permutation (Dérangement strict)'):
    st.session_state.wiring = generate_derangement(n)
    st.rerun()

# 2. Palette de couleurs
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

def plot_enigma_step(alphabet, wiring):
    fig = go.Figure()
    offset = 0.15 

    for i in range(len(alphabet)):
        target_index = wiring[i]
        color = colors[i % len(colors)]
        h_level = 0.2 + (i * (0.6 / len(alphabet)))

        # Tracé orthogonal décalé
        x_coords = [i - offset, i - offset, target_index + offset, target_index + offset]
        y_coords = [1.0, h_level, h_level, 0.0]

        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='lines',
            line=dict(color=color, width=2),
            hoverinfo='text',
            text=f"{alphabet[i]} → {alphabet[target_index]}",
            showlegend=False
        ))

        # Lettres d'entrée et de sortie
        fig.add_trace(go.Scatter(x=[i], y=[1.1], text=[alphabet[i]], mode='text', 
                                 textfont=dict(size=14, family="Courier New Bold"), showlegend=False))
        fig.add_trace(go.Scatter(x=[i], y=[-0.1], text=[alphabet[i]], mode='text', 
                                 textfont=dict(size=14, family="Courier New Bold"), showlegend=False))

    fig.update_layout(
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.2]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_enigma_step(alphabet, st.session_state.wiring), use_container_width=True)
