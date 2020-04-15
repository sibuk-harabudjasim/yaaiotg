#### Yet Another Aiotg Bot ####

This is yet another telegram bot for asyncio python3.\
Major difference is scenario system based on generators, so conversation in code can more look like conversation and not a set of handlers.\

```
import asyncio

from environs import Env

from yaaiotg.bot import YaaiotgBot
from yaaiotg.userstorage.in_memory_storage import InMemoryStorage


async def talk(dialog, initial_message=None):
    yield dialog.say('Lets talk')
    age = yield dialog.ask('How old are you')
    yield dialog.say('Thanks {}-er'.format(age))
    await asyncio.sleep(1)
    yield dialog.say('Goodbye')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env('TELEGRAM_TOKEN')
    userstorage = InMemoryStorage()
    bot = YaaiotgBot(userstorage=userstorage, api_token=token)
    bot.entry_point = talk
    bot.run(debug=env('DEBUG'))
```

This project is heavily under construction, so treat it as a proof of concept.\
But I'm working on it to be able to migrate my bot from aiotg to this framework.