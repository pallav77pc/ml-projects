import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id', 'overview']].iloc[movie_indices]

# Fetch movie details from TMDB API
def fetch_movie_details(movie_id):
    api_key = 'faa2385c5e9436427a09ec800494767c'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    # Fetch watch providers
    providers_url = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}'
    providers_response = requests.get(providers_url)
    providers_data = providers_response.json().get('results', {}).get('US', {})
    
    watch_providers = []
    if 'flatrate' in providers_data:
        watch_providers.extend([p['provider_name'] for p in providers_data['flatrate']])
    if 'rent' in providers_data:
        watch_providers.extend([p['provider_name'] + ' (Rent)' for p in providers_data['rent']])
    if 'buy' in providers_data:
        watch_providers.extend([p['provider_name'] + ' (Buy)' for p in providers_data['buy']])
    
    details = {
        'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" if data.get('poster_path') else "",
        'genres': ', '.join([g['name'] for g in data.get('genres', [])]),
        'rating': data.get('vote_average', 'N/A'),
        'release_date': data.get('release_date', 'N/A'),
        'runtime': data.get('runtime', 'N/A'),
        'watch_providers': ', '.join(watch_providers) if watch_providers else 'Not available',
        'tmdb_url': f"https://www.themoviedb.org/movie/{movie_id}"
    }
    return details

# Streamlit UI
st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    # Display each recommendation with full details
    for idx, row in recommendations.iterrows():
        movie_id = row['movie_id']
        movie_title = row['title']
        overview = row['overview']
        
        details = fetch_movie_details(movie_id)
        
        # Create columns for layout
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if details['poster']:
                st.image(details['poster'], width=150)
        
        with col2:
            st.subheader(movie_title)
            st.write(f"**Rating:** {details['rating']}/10")
            st.write(f"**Release Date:** {details['release_date']}")
            st.write(f"**Runtime:** {details['runtime']} minutes")
            st.write(f"**Genres:** {details['genres']}")
            st.write(f"**Overview:** {overview}")
            st.write(f"**Where to Watch:** {details['watch_providers']}")
            st.markdown(f"[View on TMDB for more options →]({details['tmdb_url']})")
        
        st.divider()
