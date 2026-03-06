import streamlit as st
import plotly.graph_objects as go
import random
import string

st.set_page_config(page_title="Simulateur de Permutation Enigma", layout="wide")

## Configuration de la page
st.title("🧩 Visualisation d'un Rotor Enigma")
st.write("Chaque rotor d'Enigma effectue une permutation simple de l'alphabet. Cliquez sur le bouton pour générer un nouveau câblage.")

# Initialisation de l'alphabet
alphabet = list(string.ascii_uppercase)

# Bouton pour changer la permutation
if 'permutation' not in st.session_state or st.button('🔄 Générer une nouvelle permutation'):
    shuffled = alphabet.copy()
    random.shuffle(shuffled)
    st.session_state.permutation = shuffled

# --- Création du Graphique avec Plotly ---
def plot_permutation(original, mapped):
    fig = go.Figure()

    # Positions des lettres (Original en haut à y=1, Permuté en bas à y=0)
    for i, (char_orig, char_map) in enumerate(zip(original, mapped)):
        # Ligne de connexion
        fig.add_trace(go.Scatter(
            x=[i, i], 
            y=[1, 0],
            mode='lines',
            line=dict(color='rgba(150, 150, 150, 0.4)', width=1),
            hoverinfo='none'
        ))
        
        # Point et texte pour l'alphabet d'entrée (Haut)
        fig.add_trace(go.Scatter(
            x=[i], y=[1.05],
            text=[char_orig],
            mode='text',
            textfont=dict(size=14, color="blue", family="Courier New"),
            showlegend=False
        ))

        # Point et texte pour l'alphabet de sortie (Bas)
        fig.add_trace(go.Scatter(
            x=[i], y=[-0.05],
            text=[char_map],
            mode='text',
            textfont=dict(size=14, color="red", family="Courier New"),
            showlegend=False
        ))

    # Mise en forme du layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 26]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.2]),
        plot_bgcolor='white',
        showlegend=False
    )
    
    return fig

# Affichage du graphique
st.plotly_chart(plot_permutation(alphabet, st.session_state.permutation), use_container_width=True)

---

### Comment ça fonctionne ?
1.  **L'Alphabet** : On utilise `string.ascii_uppercase` pour obtenir les 26 lettres.
2.  **La Session State** : Streamlit se "recharge" à chaque interaction. Utiliser `st.session_state` permet de garder la permutation en mémoire tant que l'utilisateur ne clique pas sur le bouton.
3.  **Le Tracé** : 
    * Les lettres d'entrée sont placées à la coordonnée $y = 1$.
    * Les lettres de sortie (permutées) sont à $y = 0$.
    * Une ligne (`Scatter` en mode `lines`) relie chaque index $i$ du haut vers le bas.



### Aller plus loin
Dans une vraie machine Enigma, le courant traverse plusieurs rotors à la suite. Pour simuler cela, vous pourriez répéter cette fonction trois fois pour afficher trois rotors alignés verticalement, où la sortie du "Rotor 1" devient l'entrée du "Rotor 2".

Souhaitez-vous que je modifie le code pour ajouter un champ de saisie de texte qui montre en temps réel comment une lettre est transformée à travers ce câblage ?
