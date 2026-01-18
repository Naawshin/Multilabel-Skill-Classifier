import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import csv
import random


SEARCH_TERM = "Computer Vision Engineer"  
LOCATIONS = [
    ("United States", "United+States"),
    ("New York", "New+York%2C+NY"),
    ("California", "California"),
    ("Texas", "Texas"),
    ("Florida", "Florida"),
    ("Remote", "Remote"),
    ("Canada", "Canada"),
    ("United Kingdom", "United+Kingdom"),
    ("Germany", "Germany"),
    ("Australia", "Australia"),
    ("India", "India"),
    ("France", "France"),
    ("Netherlands", "Netherlands"),
    ("Sweden", "Sweden"),
    ("Singapore", "Singapore"),
    ("Switzerland", "Switzerland"),
    ("Japan", "Japan"),
    ("South Korea", "South+Korea"),
    ("Brazil", "Brazil"),
    ("Mexico", "Mexico"),
    ("Illinois", "Illinois"),
    ("Washington", "Washington"),
    ("Massachusetts", "Massachusetts"),
    ("North Carolina", "North+Carolina"),
    ("Georgia", "Georgia"),
    ("Colorado", "Colorado"),
    ("Pennsylvania", "Pennsylvania"),
    ("Virginia", "Virginia"),
    ("Ohio", "Ohio"),
    ("Michigan", "Michigan"),
    ("Arizona", "Arizona"),
    ("Tennessee", "Tennessee"),
    ("Minnesota", "Minnesota"),
    ("Utah", "Utah"),
    ("Oregon", "Oregon"),
    ("Ireland", "Ireland"),
    ("Spain", "Spain"),
    ("Italy", "Italy"),
    ("Poland", "Poland"),
    ("United Arab Emirates", "United+Arab+Emirates"),
    ("China", "China"),
    ("Hong Kong", "Hong+Kong"),
    ("Taiwan", "Taiwan"),
    ("Portugal", "Portugal"),
    ("Belgium", "Belgium"),
    ("Austria", "Austria"),
    ("Denmark", "Denmark"),
    ("Norway", "Norway"),
    ("Finland", "Finland"),
    ("New Zealand", "New+Zealand")
]

# setup chromedriver
options = uc.ChromeOptions()
driver = uc.Chrome(version_main=141, options=options)

all_job_links = set()

#scraper function
def scrape_jobs_for_location(location_name, location_param):
    
    job_links = set()
    
    try:
        search_url = f"https://www.indeed.com/jobs?q={SEARCH_TERM.replace(' ', '+')}&l={location_param}"
        print(f"Scraping: {SEARCH_TERM} in {location_name}")
        
        driver.get(search_url)
        time.sleep(8)

        page_count = 0
        while True:
            page_count += 1
            print(f"  Page {page_count}...")
            
            time.sleep(3)
            job_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="slider_item"]')
            print(f"  Found {len(job_elements)} job elements")

            # Extract URLs
            links_on_page = 0
            for job in job_elements:
                try:
                    url = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href")
                    if url and url not in job_links and url not in all_job_links:
                        job_links.add(url)
                        links_on_page += 1
                except NoSuchElementException:
                    continue

            print(f"  Added {links_on_page} new links. Total for {location_name}: {len(job_links)}")
            
            # Pagination
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next"]')
                next_button.click()
                time.sleep(random.uniform(4, 7))
            except NoSuchElementException:
                print(f"  No more pages for {location_name}")
                break
                
    except Exception as e:
        print(f"Error scraping {location_name}: {e}")
    
    return job_links


print(f"Scraping '{SEARCH_TERM}' jobs across {len(LOCATIONS)} locations")
print("=" * 60)

try:
    completed_locations = 0
    
    for location_name, location_param in LOCATIONS:
        print(f"\n[{completed_locations + 1}/{len(LOCATIONS)}] ", end="")
        
        links = scrape_jobs_for_location(location_name, location_param)
        all_job_links.update(links)
        completed_locations += 1
        
        print(f"✓ Completed {location_name}. Total links: {len(all_job_links)}")
        
        progress_file = f"{SEARCH_TERM.replace(' ', '_').lower()}_links_progress.csv"
        with open(progress_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["job_url", "search_term", "location"])
            for link in all_job_links:
                writer.writerow([link, SEARCH_TERM, location_name])
        print(f"💾 Progress saved: {progress_file}")
        

        if len(all_job_links) >= 5000:
            print(f"🎯 Reached target of 5,000 links!")
            break
            
        if completed_locations < len(LOCATIONS) and len(all_job_links) < 5000:
            delay = random.uniform(20, 30)
            print(f"⏳ Waiting {delay:.1f} seconds before next location...")
            time.sleep(delay)

finally:

    driver.quit()
    
    output_filename = f"{SEARCH_TERM.replace(' ', '_').lower()}_global_links.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["job_url", "search_term", "location"])
        for link in all_job_links:
            writer.writerow([link, SEARCH_TERM, "Multiple"])

    print(f"Search term: {SEARCH_TERM}")
    print(f"Locations covered: {completed_locations}")
    print(f"Total job links: {len(all_job_links):,}")
    print(f"Saved to: {output_filename}")