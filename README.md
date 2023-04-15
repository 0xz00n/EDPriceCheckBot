# This bot is abandoned and has been shut down.  Please feel free to fork and update.
# EDPriceCheckBot
A Discord bot to check mineral prices and alert on high LTD prices for Elite: Dangerous

### Link to add this bot to a discord server you own or admin:
https://discordapp.com/oauth2/authorize?&client_id=701891610530807819&scope=bot&permissions=83968

_Note: If the bot doesn't appear in your server, you may need to manually assign the permissions requested from the link above in your server roles._

## About
EDPriceCheckBot lets users check current prices for a range of supported minerals.  Additionally, it will notify the primary channel of a high LTD sell price (>1.4mil, >2000 demand) along with DMing any user that has signed up for alerts with `!getalerts`.  High price stations are added to a timeout list that expires after 24 hours to prevent DM/Channel spam.

Upon adding the bot to your server, make sure to use the `!setchannel` command in the channel you want it to respond to commands in.

## Supported Minerals
While using the `!check x` command where x is the mineral alias.
| Mineral | Alias |
| --- | --- |
| Low Temp Diamonds | ltd,ltds |
| Void Opals | vopal, vopals, void opal, void opals |
| Painite | painite |
| Benitoite | benitoite |
| Musgravite | musgravite |
| Grandidierite | grandidierite |
| Serendibite | serendibite |
| Tritium | tritium |
| Platinum | platinum, plat |

## Bot Help Dialogue
`!help`

Displays this help message

`!setchannel`

Sets primary channel for pricealerts and communication based on where the command is executed

`!unsetchannel`

Unsets primary channel (Must be run in the currently assigned primary channel)

`!check x`

Checks top 5 mineral prices where x is the name of the mineral

`!getalerts`

Sends DM to user when prices for LTD's reach 1.5mil with at least 2000 demand

`!stopalerts`

Removes user from DM list

`!prune`

Deletes all messages belonging to EDPriceCheckBot

## Running the bot from your own hardware/vps/etc
* Gather the requirements:
    `python3 -m pip install -r requirements.txt`
* Start EDDNListener and allow to run for 5-10 minutes to generate price histories
* Place your bot token, as well as a file named 'botadmin' containing your message.author.id, in the same directory as the py file with the name `token` and run the bot:
    `python3 EDPriceCheckBot.py`

