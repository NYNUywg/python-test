import asyncio

from run import main

if __name__ == '__main__':
    cookie_value = "b5b265dab3384e84b9c6789dd951d458"
    country_id = 92
    country_name = "Pakistan"
    total = 1911
    asyncio.run(main(cookie_value, country_id, country_name, total))
