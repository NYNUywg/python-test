import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 68
    country_name = "United Arab Emirates"
    total = 2369
    asyncio.run(main(cookie_value, country_id, country_name, total))
