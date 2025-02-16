from helper_functions_and_constants import DFS, rescale
from data_preparation import financial_feature_engineering


def model(processed_data_df, year):
    # import the models
    financial_models = DFS["financial_models"]
    artistic_models = DFS["artistic_models"]
    # financial
    best_grossWorldwide_model = financial_models["best_grossWorldwide_model"]
    best_openingWeekendGross = financial_models["best_opening_weekend_Gross"]
    # critique
    best_wins_model = artistic_models["best_wins_model"]
    best_nominations_model = artistic_models["best_nominations_model"]
    best_meta_score_model = artistic_models["best_meta_score_model"]
    best_IMBD_Rating_model = artistic_models["best_IMBD_Rating_model"]

    # Predict
    # feature engineering
    financial_data = financial_feature_engineering(processed_data_df)
    predicted_grossWorldwide = best_grossWorldwide_model.predict(financial_data)
    predicted_openingWeekendGross = best_openingWeekendGross.predict(financial_data)

    # rescaling using cpi dict
    cpi_df = DFS["cpi_df"]
    cpi_reference = cpi_df[cpi_df["year"] == 2023]["cpi_index"].values
    predicted_grossWorldwide = rescale(
        predicted_grossWorldwide, year, cpi_reference, cpi_df
    )
    predicted_openingWeekendGross = rescale(
        predicted_openingWeekendGross, year, cpi_reference, cpi_df
    )

    # critique
    predicted_wins = best_wins_model.predict(financial_data)
    predicted_nominations = best_nominations_model.predict(financial_data)
    predicted_IMBD_Rating = best_IMBD_Rating_model.predict(financial_data)
    predicted_meta_score = best_meta_score_model.predict(financial_data)

    rating = (predicted_IMBD_Rating + 0.1 * predicted_meta_score) / 2
    return {
        "predicted_grossWorldwide": float(predicted_grossWorldwide[0]),
        "predicted_openingWeekendGross": float(predicted_openingWeekendGross[0]),
        "predicted_wins": int(predicted_wins[0]),
        "predicted_nominations": int(predicted_nominations[0]),
        "predicted_Rating": float(rating[0]),
    }
