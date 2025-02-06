import streamlit as st
import requests
import base64
import os
import pickle

# ============================ CONFIGURE STORAGE METHOD ============================
STORAGE_METHOD = "gdrive"  # Choose: "gdrive", "s3", or "huggingface"

# ============================ GOOGLE DRIVE METHOD ============================
if STORAGE_METHOD == "gdrive":
    import gdown

    similarity_file_id = "1gzOPUVgnzKWfcMXxHICdo3VyxBCutM99"
    movie_list_file_id = "1ttCQR1vZcviZ2ItzXdgtOsHfjEGNFb6a"

    similarity_path = "similarity.pkl"
    movie_list_path = "movie_list.pkl"

    if not os.path.exists(similarity_path):
        gdown.download(f"https://drive.google.com/uc?id={similarity_file_id}", similarity_path, quiet=False)

    if not os.path.exists(movie_list_path):
        gdown.download(f"https://drive.google.com/uc?id={movie_list_file_id}", movie_list_path, quiet=False)

# ============================ LOAD MODELS ============================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


# ============================ MOVIE POSTER FETCH FUNCTION ============================
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"


# ============================ RECOMMEND FUNCTION ============================
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters


# ============================ BACKGROUND IMAGE ============================
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


background_image_path = "static/image.jpg"
if os.path.exists(background_image_path):
    encoded_image = get_base64_image(background_image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpeg;base64,{encoded_image});
            background-size: cover;
            background-position: center center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================ STREAMLIT UI ============================
st.header('Movie Recommendation System')

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])
