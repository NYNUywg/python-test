import asyncio

from run import main

if __name__ == '__main__':
    country_id = 91
    country_name = "Cambodia"
    total = 193
    asyncio.run(main(country_id, country_name, total))
