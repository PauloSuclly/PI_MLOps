#Import the elementary libraries
from typing import Optional
from fastapi import FastAPI
import pandas as pd
import numpy as np


# We initialize the instance of Fast Api
app = FastAPI()

# Read the platform_movies database (csv file)
platform_movies = pd.read_csv("./datasets/platform_movies_scores.csv")

# List of allowed platforms that will be used to filter
allowed_platforms = ["netflix", "amazon", "hulu", "disney"]

# List of allowed duration_types that will be used to filter.
allowed_duration_types = ["min","season","seasons"]

# Function 1
# Will return the movie with the longest duration.
@app.get("/get_max_duration")
def get_max_duration(year: Optional[int]= None, platform: Optional[str]= None, duration_type: Optional[str] = "min"):
    
    # Here We will filter the registers of the column "duration_type" with the data of the variable duration_type
    if duration_type.lower() in allowed_duration_types:
        if duration_type in ["season","seasons"]:
            platform_mask = platform_movies[platform_movies["duration_type"].isin(["season","seasons"])]
        else:    
            platform_mask = platform_movies[platform_movies["duration_type"] == duration_type]

    else:
        # An error will appear if the duration_type introduced is not part of the allowed ones.
        return {"error": "Please introduce a valid duration_type (Min, Season, Seasons)"}

    if year is not None:
        # We will filter the registers with the condition that the data located in the column "release_year" is equals to the introduced "year".
        platform_mask = platform_mask[platform_mask["release_year"] == year]

    if platform is not None:
        if platform.lower() in allowed_platforms:
            # After filtering the platforms, We pass everything to lowercase.
            platform_id = platform.lower()[0]
            # Here We filter the registers of the column "id". (We use the first letter to extract the content of the platform).
            platform_mask = platform_mask[platform_mask["id"].str.startswith(platform_id)]

        else:
            # An error will appear if the platform introduced is not part of the allowed ones.
            return {"error": "Please introduce a valid platform (Netflix, Amazon, Hulu, Disney)"}

    # Here We will sort the values of the column "duration_int" and get the title of the max_duration audiovisual content
    title = platform_mask.sort_values('duration_int', ascending=False).iloc[0]['title']

    # Return the title of the max_duration audiovisual content
    return {"max_duration_title": title}


# Function 2
# Will return the number of films by platform with a score greater than XX in a given year.
@app.get("/get_score_count({platform},{scored},{year})")
def get_score_count(platform: str, scored: Optional[float] = None, year: Optional[int] = None):

    if platform.lower() in allowed_platforms:

        # After filtering the platforms, We pass everything to lowercase.
        platform_id = platform.lower()[0]
        # Here We filter the registers of the column "id". (We use the first letter to extract the content of the platform).
        platform_mask = platform_movies[platform_movies["id"].str.startswith(platform_id)]
        
        # Now, We will filter the registers with the condition that the data located in the column "prom_scores" is greater than to the introduced "scored".
        platform_mask = platform_mask[platform_mask["prom_scores"] > scored]
        
        # Now, We will filter the registers with the condition that the data located in the column "release_year" is equals to the introduced "year".
        platform_mask = platform_mask[platform_mask["release_year"] == year]

        if len(platform_mask) == 0:
            return {"error": "We could'nt find the film that meets the filters entered."}
        else:
            platform_count = len(platform_mask)
            return {"platform": platform, "count": platform_count}

    else:
        # An error will appear if the platform introduced is not part of the allowed ones.
        return {"error": "Please introduce a valid platform (Netflix, Amazon, Hulu, Disney)."}


# Function 3
# Amount of films per platform with the filter platform. (Function will have the format get_count_platform(platform)).
@app.get("/get_count_platform({platform})")
def get_count_platform(platform: str):

    if platform.lower() in allowed_platforms:

        # After filtering the platforms, We pass everything to lowercase.
        platform_id = platform.lower()[0]
        # Here We filter the registers of the column "id". (We use the first letter to extract the content of the platform).
        platform_mask = platform_movies['id'].str.startswith(platform_id)
        # The next step is to count the number of trues that We had in the previous step.
        platform_count = int(platform_mask.sum())

        #We are going to return a JSON with the platform and the amount of movies/content that the platform has.
        return {"platform": platform, "count": platform_count}

    else:
        # An error will appear if the platform introduced is not part of the allowed ones.
        return {"error": "Please introduce a valid platform (Netflix, Amazon, Hulu, Disney)"}


# Function 4
# Will return the name of the actor who had the most appearances in that year
@app.get("/get_actor({platform},{year})")
def get_actor(platform: str, year: int):

    # After filtering the platforms, We pass everything to lowercase.
    platform_id = platform.lower()[0]

    # Here We will filter the registers of the column "id". (We use the first letter to extract the content of the platform).
    platform_mask = platform_movies[platform_movies["id"].str.startswith(platform_id)]

    # Now, We will filter the registers with the condition that the data located in the column "release_year" is equals to the introduced "year".
    platform_mask = platform_mask[platform_mask["release_year"] == year]

    platform_actors = platform_mask.assign(actor=platform_mask.cast.str.split(',')).explode('cast')
    
    # Contar la cantidad de apariciones de cada actor
    actor_counts = platform_actors.cast.value_counts()
    max_count = actor_counts.max()
    top_actors = actor_counts[actor_counts == max_count].index.tolist()

    return {"platform": platform, "top_actors": top_actors}

