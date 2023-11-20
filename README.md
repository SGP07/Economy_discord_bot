# Economy_discord_bot

## Overview
The Bushicro Discord Bot is a versatile and engaging Discord bot that includes a variety of features, such as an economy system, games, and utility commands. The bot is designed to provide entertainment and utility to users within a Discord server.

## Features

### Economy System
- **Balance Command**: Check your wallet and bank balances.
- **Work Command**: Earn coins by completing various jobs with different salaries.
- **Beg Command**: Request and receive random coin donations.

### Banking
- **Deposit Command**: Deposit coins into your bank.
- **Withdraw Command**: Withdraw coins from your bank.
- **Send Command**: Transfer coins to another user.

### Games
- **Slots Command**: Try your luck with a slot machine for a chance to win coins.
- **Rob Command**: Attempt to rob coins from another user, with a risk of being caught.

### Social Interaction
- **Leaderboard Command**: View the top richest users on the server.
- **Battle Command**: Challenge another user to a battle, with the winner taking coins from the loser.

## Setup

1. **MongoDB Setup**: Set up a MongoDB database and replace `client = MongoClient("..")` in the code with your MongoDB connection string.

2. **Discord Bot Token**: Replace `token = 'TOKEN'` with your Discord bot token.

3. **Dependencies Installation**: Install the required Python packages using:
   ```bash
   pip install discord.py pymongo
   ```

## Usage
1. **Invite the Bot**: Invite the bot to your Discord server using the provided [invite link](your_bot_invite_link).
2. **Command Prefix**: Use the command prefix `!` to interact with the bot. For example:
    - `!balance`: Check your wallet and bank balances.
    - `!work`: Earn coins by completing various jobs.
    - `!slots`: Try your luck with a slot machine.
    - `!rob @user`: Attempt to rob coins from another user.
    - `!leaderboard`: View the top richest users on the server.
    - `!battle @user amount`: Challenge another user to a battle.
    - and more!

Explore various commands and engage with the economy system, games, and social features.


## TODO
- Implement a dashboard for enhanced user interaction.

## Contributions
Contributions to the project are welcome. Feel free to fork the repository, make changes, and submit pull requests.
