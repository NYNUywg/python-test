import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 87
    country_name = "Malaysia"
    total = 1049
    asyncio.run(main(cookie_value, country_id, country_name, total))
