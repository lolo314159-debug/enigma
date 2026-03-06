import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : Borniers Vertical", layout="wide")

st.title("🔌 Circuit Intégré Enigma")
st.write("Le signal traverse chaque lettre de haut en bas avant de repartir vers le rotor suivant.")

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
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.rerun()

def plot_triple_rotor_clean():
    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # On définit les centres des alphabets (Y)
    # Les rotors se situent ENTRE ces niveaux
    levels = [3, 2, 1, 0] 
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]

    for stage in range(3):
        current_wiring = wirings[stage]
        y_top_limit = levels[stage] - 0.15     # Sortie du bornier du haut
        y_bottom_limit = levels[stage + 1] + 0.15 # Entrée du bornier du bas
        
        for i in range(n):
            target = current_wiring[i]
            color = colors[i % len(colors)]
            # Palier horizontal unique pour ce fil dans ce rotor
            h_level = y_bottom_limit + 0.1 + (i * (0.5 / n))

            # TRACÉ DU FIL ENTRE LES BORNES
            # Le fil part du bas de la lettre i (y_top_limit) 
            # et arrive au haut de la lettre target (y_bottom_limit)
            fig.add_trace(go.Scatter(
                x=[i, i, target, target],
                y=[y_top_limit, h_level, h_level, y_bottom_limit],
                mode='lines',
                line=dict(color=color, width=1.5),
                hoverinfo='skip',
                showlegend=False
            ))

    # AFFICHAGE DES ALPHABETS ET TRAVERSÉE VERTICALE
    for y_val in levels:
        for i in range(n):
            # Petit trait vertical qui "traverse" la lettre pour montrer le contact
            fig.add_trace(go.Scatter(
                x=[i, i], y=[y_val - 0.15, y_val + 0.15],
                mode='lines',
                line=dict(color='black', width=1),
                hoverinfo='skip', showlegend=False
            ))
            # La lettre elle-même
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val],
                text=[alphabet[i]],
                mode='text',
                textfont=dict(size=13, family="Courier New Bold", color="black"),
                showlegend=False
            ))

    fig.update_layout(
        height=850,
        margin=dict(l=50, r=50, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
        plot_bgcolor='white',
    )
    return fig

st.plotly_chart(plot_triple_rotor_clean(), use_container_width=True)
