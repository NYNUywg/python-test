import asyncio
from run import main

if __name__ == '__main__':
    country_id = 85
    country_name = "India"
    total = 6480
    
    print(f"Starting to scrape {country_name} companies...")
    print(f"Total companies to process: {total}")
    print("-" * 50)
    
    asyncio.run(main(country_id, country_name, total))
