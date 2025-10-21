import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 91
    country_name = "Cambodia"
    total = 193
    asyncio.run(main(cookie_value, country_id, country_name, total))
