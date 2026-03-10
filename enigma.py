import streamlit as st
import plotly.graph_objects as go
import random
import string
import time

# --- 1. INITIALISATION ---
def generate_derangement():
    indices = list(range(26))
    while True:
        random.shuffle(indices)
        if all(indices[i] != i for i in range(26)): return indices

if 'r1_base' not in st.session_state:
    st.session_state.r1_base = generate_derangement()
    st.session_state.r2_base = generate_derangement()
    st.session_state.r3_base = generate_derangement()
    st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
    st.session_state.text_in, st.session_state.text_out = "", ""
    st.session_state.pressed_key = None

st.set_page_config(page_title="Enigma : Physique des Contacts", layout="wide")
alphabet = list(string.ascii_uppercase)

# --- 2. LOGIQUE DE SIGNAL (CONTACTS VERTICAUX ENTRE ROTORS) ---
def get_enigma_path(key_char, o1, o2, o3):
    # 1. Entrée Clavier -> Position physique Rotor 1
    k_idx = alphabet.index(key_char)
    p0 = (k_idx + o1) % 26  # Point d'entrée physique R1
    
    # 2. Traversée Rotor 1 (Sortie physique = Entrée physique Rotor 2)
    p1 = st.session_state.r1_base[p0] 
    
    # 3. Traversée Rotor 2 (Sortie physique = Entrée physique Rotor 3)
    p2 = st.session_state.r2_base[p1]
    
    # 4. Traversée Rotor 3 (Sortie physique finale)
    p3 = st.session_state.r3_base[p2]
    
    # 5. Conversion Sortie physique -> Lettre (Stator de sortie fixe)
    # On compense l'offset du dernier rotor pour revenir au cadre fixe
    out_idx = (p3 - o1) % 26 
    
    return [k_idx, p0, p1, p2, p3, out_idx]

# --- 3. INTERFACE ---
st.title("📟 Enigma : Correction des Contacts Verticaux")

delay = st.sidebar.slider("Délai d'observation (sec)", 0.0, 5.0, 1.5, step=0.5)

col_log, col_kbd = st.columns([1, 1.2])
with col_log:
    st.write(f"**Positions :** `{alphabet[st.session_state.off1]}-{alphabet[st.session_state.off2]}-{alphabet[st.session_state.off3]}`")
    st.info(f"**Clair :** `{st.session_state.text_in}`")
    st.success(f"**Chiffré :** `{st.session_state.text_out}`")
    if st.button("⏪ Reset Machine", use_container_width=True):
        st.session_state.off1, st.session_state.off2, st.session_state.off3 = 0, 0, 0
        st.session_state.text_in, st.session_state.text_out = "", ""
        st.session_state.pressed_key = None
        st.rerun()

with col_kbd:
    # Clavier AZERTY complet
    rows = [["A","Z","E","R","T","Y","U","I","O","P"], ["Q","S","D","F","G","H","J","K","L","M"], ["W","X","C","V","B","N"]]
    for row in rows:
        cols = st.columns(len(row))
        for i, key in enumerate(row):
            if cols[i].button(key, key=f"key_{key}", use_container_width=True):
                st.session_state.pressed_key = key
                st.session_state.text_in += key
                p = get_enigma_path(key, st.session_state.off1, st.session_state.off2, st.session_state.off3)
                st.session_state.text_out += alphabet[p[5]]

# --- 4. DESSIN ---
def draw_viz():
    fig = go.Figure()
    levels = [2.2, 1.5, 0.8, 0.1, -0.6] # 5 niveaux (Clavier, R1, R2, R3, Sortie)
    offs = [0, st.session_state.off1, st.session_state.off2, st.session_state.off3, 0]
    wirings = [st.session_state.r1_base, st.session_state.r2_base, st.session_state.r3_base]
    
    path = get_enigma_path(st.session_state.pressed_key, st.session_state.off1, st.session_state.off2, st.session_state.off3) if st.session_state.pressed_key else None

    # Dessin des rotors
    for s in range(3):
        w = wirings[s]
        y_top, y_bot = levels[s+1] + 0.1, levels[s+2] - 0.1
        
        # Signal interne au rotor
        active_in = path[s+1] if path else -1
        active_out = path[s+2] if path else -1
        
        for i in range(26):
            is_active = (i == active_in)
            fig.add_trace(go.Scatter(
                x=[i, wirings[s][i]], y=[levels[s+1], levels[s+2]],
                mode='lines', line=dict(color="red" if is_active else "#eee", width=4 if is_active else 1),
                opacity=1.0 if is_active else 0.1, showlegend=False
            ))

    # Jonctions (Clavier -> R1 et R3 -> Sortie)
    if path:
        # Clavier (p[0]) vers Entrée R1 (p[1])
        fig.add_trace(go.Scatter(x=[path[0], path[1]], y=[levels[0], levels[1]], mode='lines', line=dict(color="red", width=4), showlegend=False))
        # Sortie R3 (p[4]) vers Lampe (p[5])
        fig.add_trace(go.Scatter(x=[path[4], path[5]], y=[levels[4], levels[5]], mode='lines', line=dict(color="red", width=4), showlegend=False))

    # Dessin des lettres et cases
    for l_idx, y_val in enumerate(levels):
        current_off = offs[l_idx]
        for i in range(26):
            is_red = (path and path[l_idx] == i)
            fig.add_trace(go.Scatter(
                x=[i], y=[y_val], mode='markers+text',
                marker=dict(symbol='square', size=18, color='white', line=dict(color="red" if is_red else "#ccc", width=2 if is_red else 1)),
                text=alphabet[(i - current_off) % 26],
                textfont=dict(size=9, color="red" if is_red else "black"),
                showlegend=False
            ))

    fig.update_layout(height=600, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white',
                      xaxis=dict(showgrid=False, range=[-0.5, 25.5], showticklabels=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    return fig

st.plotly_chart(draw_viz(), use_container_width=True)

# --- 5. FIN DE CYCLE ---
if st.session_state.pressed_key:
    if delay > 0: time.sleep(delay)
    st.session_state.off1 = (st.session_state.off1 + 1) % 26
    st.session_state.pressed_key = None
    st.rerun()
