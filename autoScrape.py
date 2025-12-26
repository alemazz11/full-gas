from playwright.sync_api import sync_playwright, Playwright
import json
import pandas as pd
import numpy as np
import time

def handle_cookies(page):
    try:
        button = page.locator('button:has-text("Accept")').first
        if button.is_visible(timeout=5000):
            button.click()
            print("Cookies accepted.")
    except:
        print("No cookie banner appeared.")


        
condition_mapping = {'UsedCondition': 'Used', 'NewCondition': 'New'}


def run(playwright: Playwright, brands, cars):
    
    for brand in brands:
        print(f"Scraping {brand}...")
        if brand == 'Lynk & Co':
            brand = 'lynk-%26-co'
        start_url = f"https://www.autoscout24.com/lst/{brand}?sort=standard&desc=0&ustate=N%2CU&atype=C&cy=D%2CA%2CI%2CB%2CNL%2CE%2CL%2CF&damaged_listing=exclude&source=homepage_search-mask"
        
        chrome = playwright.chromium
        browser = chrome.launch(headless=True, slow_mo=50)
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
            for link in page.locator("a[data-anchor-overlay='true']").all()[:1]: 
                
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
                try:
                    Brand = json_data["brand"]["name"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Brand = np.nan
                
                try:
                    Model = json_data["offers"]["itemOffered"]["model"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Model = np.nan
                
                try:
                    Price = json_data["offers"]["price"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Price = np.nan
                
                try:
                    Country = json_data["offers"]["offeredBy"]["address"]['addressCountry']
                except (KeyError, IndexError, StopIteration, TypeError):
                    Country = np.nan
                
                try:
                    Body = json_data["offers"]["itemOffered"]["bodyType"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Body = np.nan
                
                try:
                    Mileage = json_data["offers"]["itemOffered"]["mileageFromOdometer"]["value"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Mileage = 0
                
                try:
                    Condition = condition_mapping.get(json_data["offers"]["itemCondition"])
                except (KeyError, IndexError, StopIteration, TypeError):
                    Condition = json_data["offers"]["itemCondition"]
                
                try:
                    Power = next((p["value"] for p in json_data.get("offers", {}).get("itemOffered", {}).get("vehicleEngine", [{}])[0]
                                        .get("enginePower", []) if p.get("unitCode") == "BHP"), 0)
                except(KeyError, IndexError, StopIteration, TypeError):
                    Power = np.nan
                
                try:
                    Engine_Size_cc = json_data["offers"]["itemOffered"]["vehicleEngine"][0]["engineDisplacement"]["value"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Engine_Size_cc = np.nan

                try:
                    Fuel_Consumption_l = json_data["offers"]["itemOffered"]["fuelConsumption"]["value"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Fuel_Consumption_l = np.nan

                try:
                    Seats = json_data["offers"]["itemOffered"]["seatingCapacity"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Seats = np.nan
                
                try:
                    Doors = json_data["offers"]["itemOffered"]["numberOfDoors"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Doors = np.nan
                
                try:
                    Drivetrain = json_data["offers"]["itemOffered"]["driveWheelConfiguration"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Drivetrain = np.nan

                try:
                    Gearbox = json_data["offers"]["itemOffered"]["vehicleTransmission"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Gearbox = np.nan

                try:
                    Gears = json_data["offers"]["itemOffered"]["numberOfForwardGears"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Gears = np.nan
                try:
                    Year = json_data["offers"]["itemOffered"]["productionDate"].split("-")[0]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Year = np.nan

                try:
                    Color = json_data["color"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Color = np.nan

                try:
                    Image_url = json_data["image"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Image_url = np.nan
                
                try:
                    Previous_Owners = json_data["offers"]["itemOffered"]["numberOfPreviousOwners"]
                except (KeyError, IndexError, StopIteration, TypeError):
                    Previous_Owners = np.nan

                details = json_data2.get("props", {}).get("pageProps", {}).get("listingDetails", {})
                try:
                    Fuel_Type = details.get("vehicle", {}).get("fuelCategory", {}).get("formatted", np.nan)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Fuel_Type = np.nan
                try:
                    Upholstery = details.get("vehicle", {}).get("upholstery", np.nan)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Upholstery = np.nan
                try:
                    Cylinders = details.get("vehicle", {}).get("cylinders", np.nan)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Cylinders = np.nan
                try:
                    Seller = details.get("seller", {}).get("type", np.nan)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Seller = np.nan

                try:
                    Full_Service_History = details.get("vehicle", {}).get("hasFullServiceHistory", False)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Full_Service_History = False

                try:
                    Non_Smoker_Vehicle = details.get("vehicle", {}).get("nonSmoking", False)
                except (KeyError, IndexError, StopIteration, TypeError):
                    Non_Smoker_Vehicle = False

                cars.append([Brand, Model, Body, Mileage, Price, Year, Country, Condition,
                             Fuel_Type, Fuel_Consumption_l, Drivetrain, Gearbox, Gears, 
                             Power, Engine_Size_cc, Cylinders, Seats, Doors, Color, Upholstery,
                              Full_Service_History, Non_Smoker_Vehicle, Previous_Owners, Seller, Image_url])
                
                p.close()

            # navigate to the next page
            next_page = page.locator('button[aria-label="Go to next page"]')
            if next_page.get_attribute("aria-disabled") == "true":
                print("Finished Scraping this brand")
                browser.close()
                break
            else:
                next_page.click()

    return cars          
            
            

            
        


def main():
    columns = [
    "Brand", "Model", "Body", "Mileage_km", "Price", "Year", "Country", "Condition",
    "Fuel_Type", "Fuel_Consumption_l", "Drivetrain", "Gearbox", "Gears", 
    "Power_hp", "Engine_Size_cc", "Cylinders", "Seats", "Doors", "Color", "Upholstery",
    "Full_Service_History", "Non_Smoker_Vehicle", "Previous_Owners", "Seller", "Image_url"
    ]
    
    brands = ['McLaren','Alfa-Romeo','Lynk & Co','Abarth', 'Fiat', 'Citroen', 'Opel', 'Renault', 'Dacia', 'CUPRA', 'Honda', 'Hyundai', 
            'Ford', 'Volvo', 'Toyota', 'SEAT', 'Peugeot', 'Jeep', 'Kia',
            'Land-Rover', 'Nissan', 'Skoda', 'Suzuki','MINI','Lancia'
            , 'Volkswagen', 'Audi', 'BMW', 'Mazda',"smart",
            'Mercedes-Benz', 'Jaguar', 'Lexus','Cadillac',"MG","BYD",
            'Chevrolet', 'Dodge', 'Iveco', 'Tesla', "Mitsubishi",
              'Ferrari','Porsche', 'Maserati', 'Lamborghini', 
             'Aston-Martin', 'Bentley', 'Rolls-Royce', 'Corvette']
   
    cars = []

   
    with sync_playwright() as playwright:
        cars_data = run(playwright, brands, cars)
    
    if cars_data:
        df = pd.DataFrame(cars_data, columns=columns)
        df.drop_duplicates(inplace=True)
        df.to_csv("auto_df.csv", index=False)
        print("Data saved to auto_df.csv")

    
if __name__ == "__main__":
    main()
    