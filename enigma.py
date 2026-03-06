import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Enigma : 3 Rotors Intégrés", layout="wide")

st.title("🧩 Cheminement à travers les 3 Rotors")
st.write("Le signal descend du Rotor 1 (haut) vers le Rotor 3 (bas). Les alphabets intermédiaires sont partagés.")

# --- Logique des Dérangements ---
def generate_derangement(n):
    indices = list(range(n))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(n)):
            return indices

alphabet = list(string.ascii_uppercase)
n = len(alphabet)

# Initialisation des câblages
if 'r1' not in st.session_state:
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)

if st.button('🔄 Recâbler les 3 étages'):
    st.session_state.r1 = generate_derangement(n)
    st.session_state.r2 = generate_derangement(n)
    st.session_state.r3 = generate_derangement(n)
    st.rerun()

# --- Construction du Schéma Unique ---
def plot_triple_rotor():
    fig = go.Figure()
    offset = 0.15
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # On définit 4 niveaux de Y (3 étages)
    # y=3 (Haut R1), y=2 (Bas R1 / Haut R2), y=1 (Bas R2 / Haut R3), y=0 (Bas R3)
    levels = [3, 2, 1, 0]
    wirings = [st.session_state.r1, st.session_state.r2, st.session_state.r3]
    labels = ["ROTOR I", "ROTOR II", "ROTOR III"]

    for stage in range(3):
        current_wiring = wirings[stage]
