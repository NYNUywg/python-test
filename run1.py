import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 94
    country_name = "Saudi Arabia"
    total = 809
    asyncio.run(main(cookie_value, country_id, country_name, total))
