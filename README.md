# EDPriceCheckBot
A Discord bot to check mineral prices and alert on high prices for Elite: Dangerous

### Link to add this bot to a discord server you own or admin:
https://discordapp.com/oauth2/authorize?&client_id=701891610530807819&scope=bot&permissions=83968

## About
This Discord bot lets users check current prices for a range of supported minerals.  Additionally, it will notify the primary channel of a high sell price (>1.5mil, >2000 demand) along with DMing any user that has signed up for alerts.  High price stations are added to a timeout list that expires after 24 hours to prevent DM/Channel spam.

Upon adding the bot to your server, make sure to use the `!setchannel` command in the channel you want it to respond to commands in.

### Bot Help Dialogue
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

## Running the bot from your own server
Gather the requirements:

`python3 -m pip install -r requirements.txt`

Run the bot:

`python3 EDPriceCheckBot.py`
