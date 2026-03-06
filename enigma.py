import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Rotor Enigma - Fils décalés", layout="wide")

st.title("🔌 Câblage avec Décalage Anti-Superposition")
st.write("Les lignes verticales d'entrée et de sortie sont décalées pour éviter toute confusion visuelle.")

# 1. Configuration de base
alphabet = list(string.ascii_uppercase)
n = len(alphabet)

if 'wiring' not in st.session_state:
    indices = list(range(n))
    random.shuffle(indices)
    st.session_state.wiring = indices

if st.button('🔄 Nouveau câblage'):
    indices = list(range(n))
    random.shuffle(indices)
    st.session_state.wiring = indices
    st.rerun()

# 2. Palette de couleurs
colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
    '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#e7ba52'
]

def plot_offset_wiring(alphabet, wiring):
    fig = go.Figure()
    offset = 0.15  # Le décalage pour éviter la superposition

    for i in range(len(alphabet)):
        target_index = wiring[i]
        color = colors[i % len(colors)]
        
        # Niveau horizontal unique pour chaque lettre
        h_level = 0.2 + (i * (0.6 / len(alphabet)))

        # --- Coordonnées avec décalage ---
        # x_start : position de la lettre du haut - offset
        # x_end   : position de la lettre du bas + offset
        x_coords = [i - offset, i - offset, target_index + offset, target_index + offset]
        y_coords = [1.0, h_level, h_level, 0.0]

        # Tracé du fil
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='lines',
            line=dict(color=color, width=2),
            hoverinfo='text',
            text=f"Entrée {alphabet[i]} → Sortie {alphabet[target_index]}",
            showlegend=False
        ))

        # --- Lettres (Positions fixes i) ---
        # Haut
        fig.add_trace(go.Scatter(
            x=[i], y=[1.1],
            text=[alphabet[i]],
            mode='text',
            textfont=dict(size=14, family="Courier New Bold", color="navy"),
            showlegend=False
        ))
        # Bas
        fig.add_trace(go.Scatter(
            x=[i], y=[-0.1],
            text=[alphabet[i]],
            mode='text',
            textfont=dict(size=14, family="Courier New Bold", color="darkred"),
            showlegend=False
        ))

    fig.update_layout(
        height=600,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.2]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_offset_wiring(alphabet, st.session_state.wiring), use_container_width=True)
