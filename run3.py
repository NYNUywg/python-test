import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 106
    country_name = "Mexico"
    total = 389
    asyncio.run(main(cookie_value, country_id, country_name, total))
