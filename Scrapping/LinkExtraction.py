from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time


# Step 1: Set up Selenium WebDriver
driver_path = 'chromedriver.exe'
beginning_year = 1974
ending_year = 2023
urls = [f'https://www.imdb.com/search/title/?title_type=feature&release_date={y}-01-01,{y}-12-31&count=100&sort=boxoffice_gross_us,desc' for y in range(beginning_year, ending_year+1)]
print(urls)
exit()
# Configure Chrome options to set the language to English
options = webdriver.ChromeOptions()
options.add_argument("--lang=en-US")  # Set language to English

service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

films_data = []

for url in urls:
    driver.get(url)
    # Optional: Wait for the page to fully load
    time.sleep(3)
    # Step 2: Programmatically click "Load More" until all data is loaded
    loaded_data = 50
    while loaded_data != 250:
        try:
            # Locate the "Load More" button
            load_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(@class, 'ipc-btn') and .//span[contains(text(), '50 more')]]"))
            )
            # Scroll to the button to make it visible
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            # Handle intercept issues by clicking with JavaScript
            driver.execute_script("arguments[0].click();", load_more_button)
            # Wait for new data to load
            time.sleep(3)
            loaded_data += 50

        except Exception as e:
            # Exit the loop when no "Load More" button is found
            print(f"No more 'Load More' button found or an error occurred: {e}")
            break

    # Step 3: Use Beautiful Soup to parse the page content
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    films = soup.find('ul',
                      class_="ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 gFCVNT detailed-list-view ipc-metadata-list--base")
    # Extract li_element metadata
    for film in films.find_all('li', class_='ipc-metadata-list-summary-item'):
        # Title
        title = film.find('h3', class_='ipc-title__text').text if film.find('h3', class_='ipc-title__text') else None

        # Extract metadata for each film (year, duration, and rating)
        metadata_div = film.find('div', class_='sc-300a8231-6 dBUjvq dli-title-metadata')

        # Extract the three pieces of information
        year = metadata_div.find_all('span')[0].text if len(metadata_div.find_all('span')) > 0 else None
        duration = metadata_div.find_all('span')[1].text if len(metadata_div.find_all('span')) > 1 else None
        mpa = metadata_div.find_all('span')[2].text if len(metadata_div.find_all('span')) > 2 else None
        rating_info = film.find('span', class_='ipc-rating-star--rating')
        rating = rating_info.text if rating_info else None

        # Link to the movie
        link_tag = film.find('a', class_='ipc-lockup-overlay ipc-focusable')
        movie_link = f"https://www.imdb.com{link_tag['href']}" if link_tag else None

        # Votes (optional)
        vote_count_info = film.find('span', class_='ipc-rating-star--voteCount')
        vote_count = vote_count_info.text.strip().replace('\xa0', '')[1:-1] if vote_count_info else None

        # Meta score
        meta_score_info = film.find('span', class_='sc-b0901df4-0 bXIOoL metacritic-score-box')
        meta_score = meta_score_info.text if meta_score_info else None

        # Description (specific to the current movie)
        description_div = film.find('div', class_='ipc-html-content-inner-div')
        description = description_div.text.strip() if description_div else None

        films_data.append({
            "Title": title,
            "Year": year,
            "Duration": duration,
            "MPA": mpa,
            "Rating": rating,
            "Votes": vote_count,
            "méta_score": meta_score,
            "description": description,
            "Movie Link": movie_link
        })

driver.quit()
# Convert to DataFrame and display
df = pd.DataFrame(films_data)
df.to_csv(f"imdb_movies{beginning_year}_{ending_year}.csv", index=False)




