import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 7
    country_name = "Egypt"
    total = 986
    asyncio.run(main(cookie_value, country_id, country_name, total))
