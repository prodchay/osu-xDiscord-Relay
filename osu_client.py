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


def check_if_config_okay(beatmap) -> bool:
    import config

    return (
        config.MIN_AR <= beatmap.ar <= config.MAX_AR and
        config.MIN_CS <= beatmap.cs <= config.MAX_CS and
        config.MIN_OD <= beatmap.accuracy <= config.MAX_OD and
        config.MIN_HP <= beatmap.drain <= config.MAX_HP and
        config.MIN_BPM <= beatmap.bpm <= config.MAX_BPM and
        config.MIN_LENGTH <= beatmap.total_length <= config.MAX_LENGTH
    )


def get_beatmap_name(beatmap_id: int):
    client = _get_client()
    beatmap = client.get_beatmap(beatmap_id)

    okay = check_if_config_okay(beatmap)
    if not okay:
        return "Beatmap does not meet configuration requirements."
    

    return f"{beatmap.beatmapset.artist} {beatmap.beatmapset.title} [{beatmap.version}]"
