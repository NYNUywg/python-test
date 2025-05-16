import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 92
    country_name = "Pakistan"
    total = 1965
    asyncio.run(main(cookie_value, country_id, country_name, total))
