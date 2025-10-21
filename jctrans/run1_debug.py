import asyncio

from run_debug import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 85
    country_name = "India"
    total = 6480
    asyncio.run(main(cookie_value, country_id, country_name, total))

