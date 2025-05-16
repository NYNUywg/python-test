import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 61
    country_name = "Bahrain"
    total = 165
    asyncio.run(main(cookie_value, country_id, country_name, total))
