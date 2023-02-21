# Import elementary libraries/modules
import pandas as pd
import numpy as np
import gradio as gr
from surprise import SVD
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split


# Read the scores dataset and convert the column "scores" to float16
scores_df = pd.read_csv("./datasets/scores.csv")
scores_df["scores"] = np.float16(scores_df["scores"])

# Read the movies dataset to get the movie titles
platform_movies = pd.read_csv("./datasets/platform_movies_scores.csv")

# Set the format to our scores
reader = Reader(rating_scale=(1, 5))

# Load the data to be used to train our recommendation model.
data = Dataset.load_from_df(scores_df[['userId', 'movieId', 'scores']], reader)

# Split the dataset in trainset and testset
trainset, testset = train_test_split(data, test_size=.25, random_state=42)

# Select a recommendation algorithm
model = SVD()

# Train the model with "trainset"
model.fit(trainset)

# Predict using the model and "testset"
predictions = model.test(testset)

# Function to Evaluate and predict if the movie is recommender for the user or not.
def evaluate_recommendation_movie(userId, movieId):
    
    # Get the title of the introduced movie
    movie_title = platform_movies[platform_movies.id == movieId].title.iloc[0].title()

    # Evaluate the movie using the model
    prediction = model.predict(userId,str(movieId))

    if prediction.est > 3.6:
        return "Of course, get some popcorn and enjoy", prediction.est, movie_title
    else:
        return "No, you will sleep in the middle", prediction.est, movie_title

# --------------
# Interface Part
# --------------

title = str("Movie Recommendation System")

with gr.Blocks(title= title) as demo:
    userId = gr.inputs.Number(label="Introduce your User ID")
    movieId = gr.Textbox(label="Introduce your Movie ID")
    evaluate_recommendation_movie_btn = gr.Button("Evaluate if the movie is for you")
    movie_title = gr.Textbox(label = "Film:")
    output = gr.Textbox(label="Will I enjoy the movie?")
    score = gr.Textbox(label="Predicted Score:")
    evaluate_recommendation_movie_btn.click(fn=evaluate_recommendation_movie, inputs=[userId,movieId], outputs=[output, score, movie_title])

demo.launch()