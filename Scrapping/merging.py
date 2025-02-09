import pandas as pd

beginning_year = 1974
ending_year = 2023
years = f"{beginning_year}_{ending_year}"


def merge_data(d1, d2, output):
    # Load the data from CSVs
    movies_data = pd.read_csv(d1)
    df = pd.read_csv(d2)
    # Ensure column names are consistent
    movies_data.rename(columns={'link': 'Movie Link'}, inplace=True)  # Align column names if needed
    # Perform the join on a common column, e.g., 'Movie Link'
    merged_data = pd.merge(df, movies_data, how='inner', on='Movie Link')
    # Save the merged DataFrame to a new CSV
    merged_data.to_csv(output, index=False)


def merge_years(file_list, output):
    dataframes = []  # List to store DataFrames
    for file in file_list:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.to_csv(output, index=False)


if __name__ == '__main__':
    merge_data(f"advanced_movies_details{years}.csv",
               f"imdb_movies{years}.csv",
               f"merged_movies_data{years}.csv")
    # files = [f"Data/Merged_data/merged_movies_data{i}_{i+2}.csv" for i in range(1981, 1995, 3)]
    # files = ["merged_movies_data1974_1980.csv", "TOP_250_FROM_1981_TO_2023.csv"]
    # merge_years(files, "TOP_250_FROM_1974_TO_2023.csv")
