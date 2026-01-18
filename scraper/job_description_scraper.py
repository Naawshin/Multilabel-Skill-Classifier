import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import csv
import random
import os


options = uc.ChromeOptions()
driver = uc.Chrome(version_main=141, options=options)


INPUT_FILE = "mechatronics_engineer_global_links.csv"  # Change this for each file


def get_output_filename(input_file):
    """Generate output filename based on input CSV filename"""
    base_name = os.path.splitext(input_file)[0]  # Remove .csv extension
    return f"{base_name}_descriptions.csv"

OUTPUT_FILE = get_output_filename(INPUT_FILE)


def load_urls_from_file(filename):
    """Load job URLs from your CSV file"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                if row and row[0].startswith('http'):
                    urls.append(row[0])
        print(f"Loaded {len(urls)} URLs from {filename}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return urls


def scrape_job_details(url):

    job_data = {
        'job_url': url,
        'title': '',
        'company': '',
        'location': '',
        'salary': '',
        'job_type': '',
        'job_description': '',
        'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for page load


        title_selectors = [
            "h1.jobsearch-JobInfoHeader-title",
            "h1",
            ".jobsearch-JobInfoHeader-title-container h1"
        ]
        for selector in title_selectors:
            try:
                job_data['title'] = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if job_data['title']:
                    break
            except NoSuchElementException:
                continue

        # Extract company
        company_selectors = [
            "[data-company-name='true']",
            ".jobsearch-CompanyInfoContainer",
            ".jobsearch-InlineCompanyRating"
        ]
        for selector in company_selectors:
            try:
                job_data['company'] = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if job_data['company']:
                    break
            except NoSuchElementException:
                continue

        # Extract location
        location_selectors = [
            "[data-testid='inlineHeader-companyLocation']",
            ".jobsearch-JobInfoHeader-subtitle div",
            ".jobsearch-JobMetadataHeader-item"
        ]
        for selector in location_selectors:
            try:
                job_data['location'] = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if job_data['location']:
                    break
            except NoSuchElementException:
                continue


        try:
            salary_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
            for element in salary_elements:
                text = element.text.strip()
                if any(word in text.lower() for word in ['salary', '$', '€', '£', 'per year', 'per hour']):
                    job_data['salary'] = text
                    break
        except NoSuchElementException:
            pass


        try:
            desc_element = driver.find_element(By.CSS_SELECTOR, "#jobDescriptionText")
            job_data['job_description'] = desc_element.text.strip()

        except NoSuchElementException:
            fallback_selectors = [
                ".jobsearch-JobComponent-description",
                "[class*='jobDescription']",
                ".description"
            ]
            for selector in fallback_selectors:
                try:
                    desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                    job_data['job_description'] = desc_element.text.strip()
                    if job_data['job_description']:
                        break
                except NoSuchElementException:
                    continue

        return job_data, True

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return job_data, False


def main():
    urls = load_urls_from_file(INPUT_FILE)
    
    if not urls:
        print("No URLs found.")
        return

    successful = 0
    failed = 0


    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_urls = set()
            reader = csv.DictReader(f)
            for row in reader:
                existing_urls.add(row['job_url'])
        print(f"Found {len(existing_urls)} already scraped URLs. Resuming...")
    except FileNotFoundError:
        existing_urls = set()
        print("Starting fresh scrape...")

    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 60)


    for i, url in enumerate(urls, 1):
        if url in existing_urls:
            print(f"[{i}/{len(urls)}] Already scraped: {url[:60]}...")
            continue

        print(f"[{i}/{len(urls)}] Scraping: {url[:60]}...")
        
        job_data, success = scrape_job_details(url)
        
        if success:

            file_exists = False
            try:
                with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                    file_exists = True
            except FileNotFoundError:
                file_exists = False

            with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=job_data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(job_data)
            
            successful += 1
            print(f"Success! Description length: {len(job_data['job_description'])}")
        else:
            failed += 1
            print(f"Failed!")


        if i < len(urls):
            delay = random.uniform(4, 8)
            print(f"   Waiting {delay:.1f} seconds...")
            time.sleep(delay)

    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(urls)}")


try:
    main()
finally:
    driver.quit()