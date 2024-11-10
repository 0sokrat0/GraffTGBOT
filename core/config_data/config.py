from dataclasses import dataclass
from typing import Optional

from environs import Env

@dataclass
class Server:
    url: str
    

@dataclass
class TgBot:
    token: str
    


@dataclass
class Config:
    tg_bot: TgBot
    server: Server
    


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        server=Server(url=env('SERVER_URL'))
    )
