from os import getenv

from dotenv import load_dotenv
from osu import Client

load_dotenv()


def _get_client() -> Client:
    client_id = getenv("OSU_CLIENT_ID")
    client_secret = getenv("OSU_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("Missing OSU_CLIENT_ID or OSU_CLIENT_SECRET environment variables")

    return Client.from_credentials(client_id, client_secret, None)


def get_beatmap_name(beatmap_id: int):
    client = _get_client()
    beatmap = client.get_beatmap(beatmap_id)
    return f"{beatmap.beatmapset.artist} {beatmap.beatmapset.title} [{beatmap.version}]"
