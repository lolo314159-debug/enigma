import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma Compact", layout="wide")

st.title("🔌 Circuit Enigma Compact")

# --- Style CSS pour compacter les boutons ---
st.markdown("""
    <style>
    div.stButton > button {
        padding: 5px 0px !important;
        font-size: 14px !important;
        height: 2em !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.write("### ⌨️ Clavier")

# Définition des rangées AZERTY
rows = [
    ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
    ["W", "X", "C", "V", "B", "N"]
]

# On crée un conteneur plus étroit pour réduire la taille globale
with st.container():
    col_pad_left, clavier_corps, col_pad_right = st.columns([1, 4, 1])
    
    with clavier_corps:
        for r_idx, row in enumerate(rows):
            # On crée toujours 10 colonnes pour garder la même largeur de touche
            cols = st.columns(10) 
            
            # Décalage visuel pour les rangées 2 et 3 (optionnel)
            start_col = 0 if r_idx == 0 else (1 if r_idx == 1 else 2)
            
            for i, key in enumerate(row):
                # On place les touches dans les colonnes correspondantes
                with cols[start_col + i]:
                    if st.button(key, key=f"k_{key}", use_container_width=True):
                        st.session_state.pressed_key = key
                        st.rerun()

st.divider()
# --- Logique de dérangement ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)):
            return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)

if st.button('🔄 Recâbler'):
    for r in ['r1', 'r2', 'r3']: st.session_state[r] = generate_derangement(n)
    st.rerun()

def plot_enigma_compact():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    
    # Réduction de l'échelle Y (0.8 unité entre chaque alphabet au lieu de 1.0)
    levels = [2.4, 1.6, 0.8, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        # On réduit l'espace mort (padding) autour des lettres
        y_start = levels[stage] - 0.12
        y_end = levels[stage+1] + 0.12
        
        for i in range(n):
            target = current_wiring[i]
            color = colors[i % len(colors)]
            # Palier horizontal resserré
            h_level = y_end + 0.05 + (i * (0.2 / n))

            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_start, h_level, h_level, y_end],
                mode='lines',
                line=dict(color=color, width=1.5),
                hoverinfo='skip', showlegend=False
            ))

    # Dessin des bornes (lettres)
    for y_val in levels:
        for i in range(n):
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val],
                mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color='#444', width=1)),
                text=alphabet[i],
                textfont=dict(size=10, family="Arial Black", color="black"),
                showlegend=False
            ))

    fig.update_layout(
        height=550, # Hauteur réduite pour tenir sur un écran standard
        margin=dict(l=20, r=20, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 2.7]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_enigma_compact(), use_container_width=True)
