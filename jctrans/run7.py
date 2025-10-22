import asyncio

from run import main

if __name__ == '__main__':
    country_id = 86
    country_name = "Myanmar"
    total = 190
    asyncio.run(main(country_id, country_name, total))
