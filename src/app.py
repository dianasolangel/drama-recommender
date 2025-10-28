import streamlit as st
from similarity_case import recommend_from_prompt, recommend_similar_drama

st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #ffe6f0;  /* full pink background */
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }

    h1, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: black !important;
        text-align: center;
    }

    .stMarkdown p, .stRadio label, .stRadio div, .stTextArea label {
        color: black !important;
    }

    .stRadio > div {
        background-color: #ffcce6;
        padding: 10px;
        border-radius: 10px;
    }

    .stTextArea textarea {
        background-color: #ff66b2;  /* même couleur que le bouton */
        border: 2px solid #ff1493;  /* contour rose foncé */
        border-radius: 12px;
        color: white;  /* texte en blanc pour contraste */
        font-weight: bold;
    }

    .stButton button {
        background-color: #ff66b2;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        transition: 0.3s;
    }

    .stButton button:hover {
        background-color: #ff1493;
        cursor: pointer;
    }

   a  {
        color: #cc0066;
        font-weight: bold;
    }

    .block-container {
        padding-top: 2rem;
    }
    
    .st.subheader  {
        color: black !important;
    }
        


    </style>
""", unsafe_allow_html=True)
#UI starts here
st.title("🌸 Asian Drama Recommender 🌸")
# --- Use Case 1: Personalized recommendation based on watchlist ---
#TO DO 


# --- Use Case 2: Prompt-based ---
mode = st.radio("✨ Choose a mode:", ["Prompt-based Recommendation", "Similar to an already watched Drama"], index=0)

if mode == "Prompt-based Recommendation":
    prompt = st.text_area("💭 Describe what you feel like watching:", height=100)
    if st.button("💖 Recommend!"):
        if prompt:
            st.subheader("💎 Recommended Dramas")
            results = recommend_from_prompt(prompt, return_streamlit=True)
            for doc in results:
                st.markdown(f"**🎬 {doc['title']}** ({doc['country']}) — ⭐ {doc['rating']}")
                if doc.get("genres"):
                    st.markdown(f"**Genres:** {doc['genres']}")
                if doc.get("tags"):
                    st.markdown(f"**Tags:** {doc['tags']}")
                st.markdown(f"[🔗 More Info]({doc['url']})\n")
        else:
            st.warning("Please enter a description first! 💡")

elif mode == "Similar to an already watched Drama":
    drama_name = st.text_input("🎀 Enter a drama you liked:")
    if st.button("🔍 Find Similar"):
        if drama_name: 
            st.subheader("💞 Similar Recommendations")
            results = recommend_similar_drama(drama_name, return_streamlit=True)
            if not results:
                st.error("Drama not found. Try a different title 💔")
            else:
                for doc in results:
                    st.markdown(f"**🎬 {doc['title']}** ({doc['country']}) — ⭐ {doc['rating']}")
                    if doc.get("genres"):
                        st.markdown(f"**Genres:** {doc['genres']}")
                    if doc.get("tags"):
                        st.markdown(f"**Tags:** {doc['tags']}")
                    st.markdown(f"[🔗 More Info]({doc['url']})\n")
        else:
            st.warning("Please enter a drama title first! 💡")