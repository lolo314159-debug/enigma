import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Borniers Pro", layout="wide")

st.title("🔌 Simulateur de Flux Enigma")
st.write("Le signal électrique circule entre les bornes. Chaque lettre est un connecteur physique.")

# --- Logique de calcul ---
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

def plot_enigma_pro():
    fig = go.Figure()
    
    # Couleurs distinctes pour les fils
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#fb9a99']
    
    # Niveaux Y pour les alphabets (les bornes)
    levels = [3, 2, 1, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]

    for stage in range(3):
        current_wiring = wirings[stage]
        # Le fil part de SOUS la lettre du haut vers AU-DESSUS de la lettre du bas
        y_start = levels[stage] - 0.2
        y_end = levels[stage+1] + 0.2
        
        for i in range(n):
            target = current_wiring[i]
            color = colors[i % len(colors)]
            # Palier horizontal
            h_level = y_end + 0.1 + (i * (0.4 / n))

            # Dessin du fil
            fig.add_trace(go.Scatter(
                x=[i, i, target, target],
                y=[y_start, h_level, h_level, y_end],
                mode='lines',
                line=dict(color=color, width=2),
                hoverinfo='skip', showlegend=False
            ))

    # Dessin des "Bornes" (les lettres)
    for y_val in levels:
        # On dessine un rectangle blanc derrière les lettres pour "couper" les lignes si besoin
        # et on place la lettre au centre.
        for i in range(n):
            # Cadre de la borne
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val],
                mode='markers+text',
                marker=dict(symbol='square', size=22, color='white', line=dict(color='black', width=1)),
                text=alphabet[i],
                textfont=dict(size=12, family="Courier New Bold", color="black"),
                hoverinfo='text',
                textposition="middle center",
                showlegend=False
            ))

    fig.update_layout(
        height=900,
        margin=dict(l=50, r=50, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
        plot_bgcolor='rgba(240,240,240,0.5)',
    )
    return fig

st.plotly_chart(plot_enigma_pro(), use_container_width=True)
