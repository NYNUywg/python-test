import asyncio

from run import main

if __name__ == '__main__':
    country_id = 87
    country_name = "Malaysia"
    total = 1049
    asyncio.run(main(country_id, country_name, total))
