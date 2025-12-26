from playwright.sync_api import sync_playwright, Playwright
import json
import pandas as pd
import numpy as np

def handle_cookies(page):
    try:
        button = page.locator('button:has-text("Accept")').first
        if button.is_visible(timeout=5000):
            button.click()
            print("Cookies accepted.")
    except:
        print("No cookie banner appeared.")

brands = ['Alfa-Romeo','Lynk & Co', 'McLaren', 'Fiat', 'Citroen', 'Opel', 'Renault', 'Dacia', 'CUPRA', 'Honda', 'Hyundai', 
            'Ford', 'Volvo', 'Toyota', 'SEAT', 'Peugeot', 'Jeep', 'Kia',
            'Land-Rover', 'Nissan', 'Skoda', 'Suzuki','MINI','Lancia'
            , 'Volkswagen', 'Audi', 'BMW', 'Mazda',
            'Mercedes-Benz', 'Jaguar', 'Lexus','Cadillac',
            'Chevrolet', 'Dodge', 'Tesla','Iveco',
            'Ferrari', 'Porsche', 'Maserati', 'Lamborghini', 
             'Aston-Martin', 'Bentley', 'Rolls-Royce', 'Corvette']
        
condition_mapping = {'UsedCondition': 'Used', 'NewCondition': 'New'}

def run(playwright: Playwright, brands=brands):
    
    
    for brand in brands:
        print(f"Scraping {brand}...")
        if brand == 'Lynk & Co':
            brand = 'lynk-%26-co'
        start_url = f"https://www.autoscout24.com/lst/{brand}?sort=standard&desc=0&ustate=N%2CU&atype=C&cy=D%2CA%2CI%2CB%2CNL%2CE%2CL%2CF&damaged_listing=exclude&source=homepage_search-mask"
        
        chrome = playwright.chromium
        browser = chrome.launch(headless=False, slow_mo=50)
        #User agent to act as human
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        page = context.new_page()
        # Blocking images
        page.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())

        page.goto(start_url, wait_until="domcontentloaded")
        # Accepting cookies
        handle_cookies(page)
        while True:
            
            # Going through every listing
            for link in page.locator("a[data-anchor-overlay='true']").all(): 
                
                p = context.new_page()
                p.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
                handle_cookies(page)
                url = link.get_attribute("href")

                if url is not None:
                    p.goto(url, wait_until="domcontentloaded", timeout=20000)
                else:
                    p.close()
                
                #getting json data for each car listing | nth(1) because we want the 2nd json
                data = p.locator("script[type='application/ld+json']").nth(1).text_content()
                data2 = p.locator("script#__NEXT_DATA__").text_content()
                json_data = json.loads(data)
                json_data2 = json.loads(data2)
                
                # Extracting chosen fields
                Brand = json_data["brand"]["name"]
                Model = json_data["offers"]["itemOffered"]["model"]
                Price = json_data["offers"]["price"]
                try:
                    Mileage = json_data["offers"]["itemOffered"]["mileageFromOdometer"]["value"]
                except TypeError:
                    Mileage = 0
                try:
                    Condition = condition_mapping.get(json_data["offers"]["itemCondition"])
                except:
                    Condition = json_data["offers"]["itemCondition"]

                
                details = json_data2.get("props", {}).get("pageProps", {}).get("listingDetails", {})
                Fuel_Type = details.get("vehicle", {}).get("fuelCategory", {}).get("formatted", np.nan)
                
                
                print(Brand, Model, Price, Mileage, Condition, Fuel_Type)

                p.close()

            # navigate to the next page
            next_page = page.locator('button[aria-label="Go to next page"]')
            if next_page.get_attribute("aria-disabled") == "true":
                print("Finished Scraping this brand")
                browser.close()
                break
            else:
                next_page.click()
                
            
            

            
        



def main():
    # closes browser after scraping

    cars = []

    with sync_playwright() as playwright:
        run(playwright, brands=brands)

    
main()
    