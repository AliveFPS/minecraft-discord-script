import requests
import json
import time

"""
This module implements a Script designed to interact with a Minecraft-related 
coinflip game. The script performs the following actions:

* Retrieves recent messages from a specified Discord channel.
* Identifies game state changes (wins and losses) from message content.
* Automatically places coinflip bets using Discord's interaction system.
* Maintains statistics like win/loss counts, total earnings, and loss streaks.

Key Dependencies:
* requests: For making HTTP requests to Discord.
* json: For parsing JSON data from Discord API responses.
* time: For implementing delays and timing related to actions.

I made this script for a specific server I play on and their coinflip bot.
This might offer as some guidance to creating something similar for your own use case.
"""

class DiscordMinecraftBot:
    def __init__(self, authorization_token, channel_id, initalBet,next_bet_factor):
        self.authorization_token = authorization_token
        self.channel_id = channel_id
        self.initalBet = initalBet
        self.next_bet_factor = next_bet_factor
        self.processed_ids = set()
        self.wins = 0
        self.loss = 0
        self.total = 0
        self.counter = 0
        self.lossStreak = 0
        self.headers = {
            'authorization': authorization_token
        }

    def game_state_identifier(self, content_string, currID):
        if content_string == "":
            return 

        if currID not in self.processed_ids:
            self.processed_ids.add(currID) 

            if "has defeated <YOUR_DISCORD_ID>" in content_string:
                return "lost"
            elif "<YOUR_DISCORD_ID> has defeated" in content_string:
                return "won"

        return None 
    
    def starter(self):
            messages = self.retrieve_messages()
            if messages: 
                for message in messages:
                    emptyCheck, val = message["content"],  message["id"]
                    if emptyCheck == "":
                        return 
                    if val not in self.processed_ids:
                        self.processed_ids.add(val) 

    def retrieve_messages(self):
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=10"  
        r = requests.get(url, headers=self.headers)
        json_data = json.loads(r.text)

        relevant_messages = []
        for message in json_data: 
            if "<YOUR_DISCORD_ID>" in message['content']:
                relevant_messages.append(message)

        return relevant_messages
    

    def post_cf_command(self):
        webhook_url = "https://discord.com/api/v9/interactions"  

        payload = {
            "type": 2,
            "application_id": "plug-and-play",  #  Update with correct application ID
            "guild_id": "plug-and-play",  
            "channel_id": "plug-and-play",
            "session_id": "plug-and-play",  # Might need updates from time to time
            "data": {
                "version": "plug-and-play",
                "id": "plug-and-play",
                "guild_id": "plug-and-play",
                "name": "cf",
                "type": 1,
                "options": [
                    {"type": 3, "name": "amount", "value": str(self.initalBet * self.next_bet_factor)},
                    {"type": 3, "name": "face", "value": "heads"}
                ],
            }
        }


        headers = {
            'authorization': self.authorization_token 
        }
        
        print("Wins: " + str(self.wins) + " Loss: " + str(self.loss) + "\nTotal: " + format(self.total,",")+ "\nLoss Streak: " + str(self.lossStreak) + "\n")
        r = requests.post(webhook_url, headers=headers, json=payload)
        time.sleep(8) 
        return r

    def money_maker(self): 
        game_state_changed = False  # Add a flag
        while True:
            messages = self.retrieve_messages()
            if messages: 
                for message in messages:  
                    game_state = self.game_state_identifier(message["content"], message["id"])
                    if game_state == "won":
                        self.wins += 1
                        self.counter = 0
                        self.next_bet_factor = 1
                        self.total += self.initalBet
                        game_state_changed = True
                    elif game_state == "lost":
                        self.loss += 1
                        self.counter += 1
                        self.next_bet_factor *= 2
                        game_state_changed = True
                        if self.counter > self.lossStreak:
                            self.lossStreak = self.counter

                if game_state_changed:  # Post command only if the state changed
                    self.post_cf_command() 
                    game_state_changed = False  # Reset the flag
            else:
                time.sleep(4) 

# Usage:
bot = DiscordMinecraftBot('DISCORD_AUTH_TOKEN', 'CHANNEL_ID',100,1) #Inputs(AuthToken, channel_id, initalBet, next_bet_factor)
bot.starter()
bot.money_maker()
