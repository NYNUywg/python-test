import asyncio

from run import main

if __name__ == '__main__':
    country_id = 84
    country_name = "Oman"
    total = 225
    asyncio.run(main(country_id, country_name, total))
