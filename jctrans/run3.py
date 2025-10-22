import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = ""
    country_id = 66
    country_name = "Thailand"
    total = 933
    asyncio.run(main(country_id, country_name, total))
