import pandas as pd
from helper_functions_and_constants import (
    DFS,
    calculate_film_weight_normalized,
    calculate_film_weight_normalized_production_companies,
    calculate_film_weight_normalized_writers,
    get_season,
    ignore_inflation,
    format_genres,
    format_countries
)


def preprocess(**kwargs):
    loaded_objects = DFS["loaded_objects"]
    cpi_df = DFS["cpi_df"]

    cpi_reference = cpi_df[cpi_df["year"] == 2023]["cpi_index"].values
    data = pd.DataFrame([kwargs])
    # add the column financial_outlier_flag
    budget_bound = 100000000
    data["financial_outlier_flag"] = (data["budget"] > budget_bound).astype(int)

    for key, value in kwargs.items():
        match key:
            case "Duration":
                scale_duration(data, key, loaded_objects)
            case "MPA":
                encode_mpa(data, key, loaded_objects)
            case "release_period":
                encode_release_period(data, key, loaded_objects)
            case "genres":
                data = encode_genres(data, key, loaded_objects)
            case "countries_origin":
                data = encode_countries_origin(data, key, loaded_objects)
            case "budget":
                scale_budget(data, key, cpi_reference, loaded_objects)
            case "director":
                calculate_director_normalized_weight(data, key, loaded_objects)
            case "stars":
                calculate_stars_normalized_weights(data, key, loaded_objects)
            case "writers":
                calculate_writers_normalized_weights(data, key, loaded_objects)
            case "production_company":
                calculate_production_companies_normalized_weights(
                    data, key, loaded_objects
                )

    data = data.drop(
        ["MPA", "release_period", "genres", "countries_origin", "year"], axis=1
    )

    return data


def scale_duration(df, column_name, loaded_objects):
    duration_standard_scaler = loaded_objects["duration_standard_scaler"]
    df[column_name] = duration_standard_scaler.transform(df[[column_name]])


def encode_mpa(df, column_name, loaded_objects):
    mpa_encoder = loaded_objects["mpa_encoder"]
    encoded_mpa = mpa_encoder.transform(df[[column_name]])
    df["MPA_Encoded"] = encoded_mpa


def encode_release_period(df, column_name, loaded_objects):
    release_period_encoder = loaded_objects["release_period_encoder"]
    df[column_name] = pd.to_datetime(df[column_name])
    df[column_name] = df[column_name].dt.month.apply(get_season)
    encoded_release_period = release_period_encoder.transform(df[[column_name]])
    df[release_period_encoder.categories_[0]] = encoded_release_period.flatten()


def encode_genres(df, column_name, loaded_objects):
    genres_encoder = loaded_objects["genre_mlb"]
    df[column_name].values[0] = format_genres(df[column_name].values[0])
    df[column_name] = df[column_name].apply(lambda x: x if isinstance(x, list) else [x])
    encoded_genres = genres_encoder.transform(df[column_name])
    encoded_df = pd.DataFrame(
        encoded_genres, columns=genres_encoder.classes_, index=df.index
    )
    df = pd.concat([df, encoded_df], axis=1)
    return df


def encode_countries_origin(df, column_name, loaded_objects):
    countries_encoder = loaded_objects["countries_mlb"]
    df[column_name].values[0] = format_countries(df[column_name].values[0])
    df[column_name] = df[column_name].apply(lambda x: x if isinstance(x, list) else [x])
    encoded_countries = countries_encoder.transform(df[column_name])
    encoded_df = pd.DataFrame(
        encoded_countries, columns=countries_encoder.classes_, index=df.index
    )
    df = pd.concat([df, encoded_df], axis=1)
    return df


def scale_budget(df, column_name, cpi_reference, loaded_objects):
    year = df["year"].values[0]
    df[column_name] = ignore_inflation(df[column_name], year, cpi_reference)
    budget_scaler = loaded_objects["budget_scaler"]
    df[column_name] = budget_scaler.transform(df[[column_name]])


def calculate_director_normalized_weight(df, column_name, loaded_objects):
    directors_df = DFS["directors_df"]

    director = df[column_name][0]
    wi = (
        directors_df[
            directors_df["Director"].str.lower() == str(director).strip().lower()
            ]["Director_weight"].values[0]
        if str(director).strip().lower() in directors_df["Director"].str.lower().values
        else 0
    )
    df[column_name] = wi
    directors_scaler = loaded_objects["directors_robust_scaler"]
    df[column_name] = directors_scaler.transform(df[[column_name]])


def calculate_stars_normalized_weights(df, column_name, loaded_objects):
    df[column_name] = calculate_film_weight_normalized(df[column_name][0])
    actors_scaler = loaded_objects["actors_robust_scaler"]
    df[column_name] = actors_scaler.transform(df[[column_name]])


def calculate_writers_normalized_weights(df, column_name, loaded_objects):
    df[column_name] = calculate_film_weight_normalized_writers(df[column_name][0])
    writers_scaler = loaded_objects["writers_robust_scaler"]
    df[column_name] = writers_scaler.transform(df[[column_name]])


def calculate_production_companies_normalized_weights(df, column_name, loaded_objects):
    df[column_name] = calculate_film_weight_normalized_production_companies(
        df[column_name][0]
    )
    production_company_scaler = loaded_objects["production_company_robust_scaler"]
    df[column_name] = production_company_scaler.transform(df[[column_name]])


def financial_feature_engineering(data):
    financial_data = data
    importances = [0.2, 0.35, 0.45]
    financial_data["filming_crew"] = (importances[0] * financial_data['writers'] +
                                      importances[1] * financial_data['director'] +
                                      importances[2] * financial_data['stars']
                                      )
    financial_data = financial_data.drop(['writers', 'director', 'stars'], axis=1)

    financial_data['budget^2'] = financial_data['budget'] ** 2

    financial_data['budget_x_financial_outlier_flag'] = financial_data['budget'] * financial_data[
        'financial_outlier_flag']
    financial_data['Duration_x_financial_outlier_flag'] = financial_data['Duration'] * financial_data[
        'financial_outlier_flag']

    correct_order = [
        'Duration', 'production_company', 'financial_outlier_flag',
        'MPA_Encoded', 'Autumn', 'Beginning of the year', 'End of the year',
        'Spring', 'Summer', 'Action & Adventure', 'Comedy',
        'Documentary & Biography', 'Drama', 'Family & Animation',
        'Horror & Thriller', 'Romance', 'Sci-Fi & Fantasy', 'other_genres',
        'Australia', 'Canada', 'China', 'European countries', 'Germany',
        'India', 'Japan', 'Other_regions', 'United Kingdom', 'United States',
        'filming_crew', 'budget', 'budget^2',
        'budget_x_financial_outlier_flag', 'Duration_x_financial_outlier_flag'
    ]

    return financial_data[correct_order]
