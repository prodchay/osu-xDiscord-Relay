## What is this?

I had this small idea after a friend kept sending me maps on Discord for me to play. Every time he sent one, I had to tab out of osu! so I could download it.

This project is a small bridge between Discord and osu!, using Bancho IRC to send messages directly to my osu! account. Now, instead of needing to tab out, my friend can simply send a beatmap link on Discord and let the bot send me a dm with the map link.

I'm sure there are better solutions than mine out there but I learned a lot while making it. Also I'm always open for pull requests :D

**THIS ONLY WORKS FOR THE STABLE CLIENT UNLESS YOU HAVE A FRIEND TO USE THEIR ACCOUNT TO SEND MAPS TO YOU!**

## How does it work?

```text
Sender
  │
  │ Sends beatmap link in this format "https ://osu.ppy.sh/beatmapsets" or "https ://osu.ppy.sh/beatmaps"
  ▼
Discord
  │
  │ Message received
  ▼
Discord Bot
  │
  ├── Detects osu! beatmap link
  ├── Extracts beatmap ID
  └── Gets beatmap information
  │
  ▼
Bancho IRC
  │
  │ Sends message to osu! account
  ▼
Your osu! DMs
  │
  │ Beatmap link received
  ▼
Download & Play
```

## Configuration

These environment variables are needed for the bot to work:

Get your Discord token from: **https://discord.com/developers/home**
The bot needs the `Message Content Intent`
- `DISCORD_TOKEN`: Discord bot token

Get your IRC login from: **https://osu.ppy.sh/home/account/edit**
- `IRC_USERNAME`: IRC username
- `IRC_PASSWORD`: IRC password

Get your client id and secret from: **https://osu.ppy.sh/home/account/edit**
- `OSU_CLIENT_ID`: osu! API client ID
- `OSU_CLIENT_SECRET`: osu! API client secret
- `OSU_REDIRECT_URI`: osu! redirect URI -> use something like "http://127.0.0.1:8080" (honestly not needed because it passes None when creating the client)

Just fill this with the username that you want to send the map to
- `OSU_TARGET`: IRC user or channel to receive beatmap links
