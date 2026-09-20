import os
import re
from urllib.parse import parse_qs, urlsplit

import discord
from dotenv import load_dotenv

from irc_client import IRCClient
from osu_client import get_beatmap_name

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

trusted_users = ["783805718053781514", "423855230292066314", "694646926720761931"]
OSU_TARGET = os.getenv("OSU_TARGET")
irc_client = IRCClient()


def extract_beatmap_id(raw_url: str):
    if not raw_url or not isinstance(raw_url, str):
        return None

    url = raw_url.strip()
    if "osu.ppy.sh" not in url:
        return None

    parsed = urlsplit(url)
    path_segments = [segment for segment in parsed.path.split("/") if segment]

    for idx, segment in enumerate(path_segments):
        if segment == "beatmaps" and idx + 1 < len(path_segments):
            candidate = path_segments[idx + 1]
            if candidate.isdigit():
                return int(candidate)

    for idx, segment in enumerate(path_segments):
        if segment == "beatmapsets" and idx + 1 < len(path_segments):
            candidate = path_segments[idx + 1]
            if candidate.isdigit():
                if parsed.fragment and "/" in parsed.fragment:
                    fragment_match = re.search(r"/(\d+)$", parsed.fragment)
                    if fragment_match:
                        return int(fragment_match.group(1))
                return int(candidate)

    query_values = parse_qs(parsed.query)
    if "b" in query_values and query_values["b"][0].isdigit():
        return int(query_values["b"][0])

    if parsed.fragment:
        fragment_match = re.search(r"(?:^|/)(\d+)$", parsed.fragment)
        if fragment_match:
            return int(fragment_match.group(1))

    return None


async def send_osu_map(msg):
    if "https://osu.ppy.sh/beatmapsets" not in msg.content and "https://osu.ppy.sh/beatmaps" not in msg.content:
        return

    beatmap_id = extract_beatmap_id(msg.content)
    if beatmap_id is None:
        await msg.channel.send("I couldn't parse a valid osu! beatmap ID from that link.")
        return

    await msg.channel.send("Trying to send osu! beatmap link...")
    print(f"Extracted beatmap id: {beatmap_id}")

    try:
        beatmap_name = get_beatmap_name(beatmap_id)
    except RuntimeError as exc:
        await msg.channel.send(f"osu! setup is incomplete: {exc}")
        return
    except Exception as exc:  # noqa: BLE001
        await msg.channel.send(f"Failed to fetch the beatmap details: {exc}")
        return

    if not irc_client.is_alive():
        try:
            irc_client.start()
        except RuntimeError:
            pass

    result = irc_client.send_message(str(msg.author), beatmap_name, OSU_TARGET, msg.content)
    if result == 0:
        await msg.channel.send("Successfully sent osu! beatmap link.")
        print(f"Successfully sent osu! beatmap link to {OSU_TARGET}")
    else:
        await msg.channel.send("Failed to send osu! beatmap link.")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if not irc_client.is_alive():
        try:
            irc_client.start()
        except RuntimeError:
            pass


@client.event
async def on_message(msg):
    if isinstance(msg.channel, discord.DMChannel):
        if str(msg.author.id) not in trusted_users:
            return

        await send_osu_map(msg)
        return


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable")

    client.run(token)