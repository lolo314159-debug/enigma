import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Borniers & Décalages", layout="wide")

st.title("🔌 Circuit Enigma avec Borniers et Décalages")
st.write("Les fils sortent par la gauche et entrent par la droite de chaque borne pour éviter les superpositions.")

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

if st.button('🔄 Recâbler les rotors'):
    for r in ['r1', 'r2', 'r3']: st.session_state[r] = generate_derangement(n)
    st.rerun()

def plot_enigma_final():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    
    levels = [3, 2, 1, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    
    # Paramètre de décalage pour les fils verticaux
    # Sortie à gauche (-dx), Entrée à droite (+dx)
    dx = 0.15 

    for stage in range(3):
        current_wiring = wirings[stage]
        y_start = levels[stage] - 0.2
        y_end = levels[stage+1] + 0.2
        
        for i in range(n):
            target = current_wiring[i]
            color = colors[i % len(colors)]
            h_level = y_end + 0.1 + (i * (0.4 / n))

            # Tracé avec décalage : i-dx (haut) -> target+dx (bas)
            fig.add_trace(go.Scatter(
                x=[i - dx, i - dx, target + dx, target + dx],
                y=[y_start, h_level, h_level, y_end],
                mode='lines',
                line=dict(color=color, width=2),
                hoverinfo='skip', showlegend=False
            ))

    # Dessin des bornes (lettres) centrées sur l'index entier i
    for y_val in levels:
        for i in range(n):
            # Rectangle blanc pour isoler la lettre
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val],
                mode='markers+text',
                marker=dict(symbol='square', size=24, color='white', line=dict(color='#333', width=1)),
                text=alphabet[i],
                textfont=dict(size=12, family="Courier New Bold", color="black"),
                showlegend=False
            ))

    fig.update_layout(
        height=900,
        margin=dict(l=50, r=50, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_enigma_final(), use_container_width=True)
