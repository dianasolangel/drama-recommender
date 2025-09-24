import streamlit as st
from app.scraper.fetch_data import get_user_list, get_drama_metadata
from app.recommender.model import recommend_for_user



st.title("Drama Recommender")
st.write("Welcome to the Drama Recommender app!")

username = st.text_input("Enter your MDL username")

if st.button("Recommend"):
    user_list = get_user_list(username)
    user_dramas = [get_drama_metadata(d["slug"]) for d in user_list]

    # TODO: Add proper candidate fetching logic
    candidate_slugs = ["12345-drama-a", "67890-drama-b"]  # Example slugs
    candidate_dramas = [get_drama_metadata(slug) for slug in candidate_slugs]

    recommendations = recommend_for_user(user_dramas, candidate_dramas)
    
    for drama in recommendations:
        st.subheader(drama["title"])
        st.write(drama.get("synopsis", ""))
