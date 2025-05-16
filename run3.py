import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 84
    country_name = "Oman"
    total = 222
    asyncio.run(main(cookie_value, country_id, country_name, total))
