import asyncio

from run_debug import main

if __name__ == '__main__':
    country_id = 85
    country_name = "India"
    total = 6480
    asyncio.run(main(country_id, country_name, total))

