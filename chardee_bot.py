from discord.ext.commands import Bot 
import discord
import chardee_name
import asyncio
from discord import FFmpegPCMAudio, VoiceChannel, VoiceClient
from typing import cast
from PIL import Image
import traceback
import os.path
import cards

intents = discord.Intents.all()
client = discord.Client(intents=intents)

bot = Bot(command_prefix='--',intents=intents)

@bot.event
async def on_command_error(context, error):
    await context.send("ERROR in the bot code, please check your spelling and try again. If this fails ask Irene for help")
    ex = error.original
    print(error)
    print(''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))

team_role_ids = [812828725786968144, 812828759345856512]
team_channel_ids = [811087128184356914, 811087175709491200]
senior_role_id = 811086481955225630
emojis = [":orange_heart:", ":purple_heart:"]
state = 0
game_name = "Chardee MacDennis"
game_image = None
turn = 0
levels = [0,0]
team_cards = [[0,0,0], [0,0,0]]
last_card_type = -1

def text_level(team_index):
    lev = levels[team_index]
    if lev == 0:
        return "MIND"
    if lev == 1:
        return "BODY"
    if lev == 2:
        return "SPIRIT"
    return ""

def team_members(team_index, context):
    team_role = discord.utils.get(context.guild.roles, id=team_role_ids[team_index])
    return team_role.members

def team_name(team_index, context):
    team_role = discord.utils.get(context.guild.roles, id=team_role_ids[team_index])
    return team_role.name 

async def print_teams(context):
    string = ""
    string += str(team_name(0, context))+" :\n"
    members = team_members(0, context)
    for mem in members:
        string+="\t <@"+str(mem.id)+">\n"
    string += str(team_name(1, context))+" :\n"
    members = team_members(1, context)
    for mem in members:
        string+="\t <@"+str(mem.id)+">\n"
    await context.send(string)


async def set_team_name(team_index, context, new_name):
    team_role = discord.utils.get(context.guild.roles, id=team_role_ids[team_index])
    old_name = team_role.name 
    await context.send("Renaming "+ old_name + " to " +  new_name + ".")
    await team_role.edit(name=new_name)
    team_channel = discord.utils.get(context.guild.channels, id=team_channel_ids[team_index])
    await team_channel.edit(name=new_name)

async def get_player_tokens(team_index, context):
    members = team_members(team_index, context)
    tokens = []
    success = True
    for mem in members:
        file_name = f'tokens/'+str(mem.id)+'_token.png'
        if os.path.exists(file_name):
            print("Fetching Token for", mem)
            im = Image.open(file_name)
            tokens.append(file_name)
        else:
            await context.send("ERROR: could not retrieve token for <@" + str(mem.id) + ">")
            success = False
    return success, tokens

# @bot.command(name='reloadgame')
# async def reload_game(context, arg):
#     senior_role = discord.utils.get(context.guild.roles, id=senior_role_id)
#     if context.author not in senior_role.members:
#         await context.send("ERROR please ask a senior to reload your game")
#         return
#     global state
#     state = int(arg)
#     if state > 2:
#         success1, _ = get_player_tokens(0, context)
#         success2, _ = get_player_tokens(1, context)
#         if (not success1) or (not success2):
#             await context.send("ERROR: could not retrieve all player tokens. Setting you to state 2, rerun when tokens reentered")
#             state =2

@bot.command(name='startstack')
async def intro_message_0(context):
    global state
    if state != 0:
        await context.send("ERROR invalid command at this time")
        return
    state = 1
    
    AUDIO_CHANNEL = discord.utils.get(context.guild.channels, name="Paddy's Pub")
    await AUDIO_CHANNEL.connect()
    
    await context.send(file=discord.File('title_card.png'))
    await context.send(file=discord.File('time_stamp.png'))
    
    vc = cast(VoiceClient, context.voice_client)
    print("Playing Theme Song")
    vc.play(FFmpegPCMAudio("its-always-sunny-in-philadelphia-theme-song.mp3"))
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Theme Song done")

    await context.send(file=discord.File('emoji/paddys.png'))
    with open('messages/intro_0_0.txt','r') as file:
            message = file.read()
            await context.send(message)
    await context.send(file=discord.File('chardeemacdennis.png'))
    with open('messages/intro_0_1.txt','r') as file:
            message = file.read()
            await context.send(message)


@bot.command(name='gamename')
async def set_game_name_1(context, arg):
    global state
    context.typing()
    if state != 1:
        await context.send("ERROR invalid command at this time")
        return
    global game_name
    game_name = arg
    async with context.typing():
        file_name = chardee_name.generate_name_card(arg)
        await context.send(file=discord.File(file_name))
        global game_image
        game_image = file_name

    with open('messages/naming_1_0.txt','r') as file:
            message = file.read()
            await context.send(message)
    await context.send("THE GOLDEN GEESE")
    await context.send(file=discord.File('golden_geese.jpg'))
    await context.send("THE THUNDERMEN")
    await context.send(file=discord.File('thundermen.jpg'))


    with open('messages/naming_1_1.txt','r') as file:
            message = file.read()
            await context.send(message)

    state = 2

@bot.command(name='teamname')
async def set_team_name_2(context, arg):
    global state
    if state != 2:
        await context.send("ERROR invalid command at this time")
        return
    team1_role = discord.utils.get(context.guild.roles, id=team_role_ids[0])
    team2_role = discord.utils.get(context.guild.roles, id=team_role_ids[1])
    if context.author in team_members(0, context):
        await set_team_name(0, context, arg)
    if context.author in team_members(1, context):
        await set_team_name(1, context, arg)

@bot.command(name='playertoken')
async def set_player_token(context):
    global state
    if state != 2:
        await context.send("ERROR invalid command at this time")
        return
    try:
        user = context.author
        attachments = context.message.attachments
        if len(attachments) !=1:
            await context.send("*ERROR* please attach 1 image")
            return 
        file_name = f'tokens/'+str(context.author.id)+'_token.png'
        await attachments[0].save(file_name)

        # im = Image.open(file_name)  
        # width, height = im.size
        # max_dim = max(width, height)
        # scale = 100/max_dim
        # im1 = im.resize((int(width*scale), int(height*scale)))
        # im1.save(file_name)

        await context.send("Set <@"+str(user.id)+">'s Token Picture!")
    except Exception as e:
        await context.send("Error in setting token, please try again")
        print(e)

@bot.command(name='continue')
async def continue_command(context):
    # if state not in [2] :
    #     return
    # state += 1
    # await context.send("Continuing... If you called this in error, please run `--uncontinue`")
    # async with context.typing():
    #     await asyncio.sleep(3)
    global state
    if state ==2:
        print("Getting Tokens")
        success1, _ = await get_player_tokens(0, context)
        success2, _ = await get_player_tokens(1, context)
        print(success1, success2)
        if (not success1) or (not success2):
            await context.send("Please set remaining player tokens and then run `--continue` again")
            return
        state = 3
        await wine_3(context)
    elif state == 3:
        await print_rules(context)
        state = 4
    elif state ==4:
        await game_begins_5(context)
        state = 5
    elif state ==5:
        state = 6
        await take_turn(context)
    elif state==7:
        state = 6
        await take_turn(context)
    elif state==8:
        state = 9
        await gotobed(context)
    elif state==9:
        await context.send("Thanks for playing!")
    else:
        await context.send("ERROR invalid command at this time")

# @bot.command(name='uncontinue')
# async def uncontinue_command(context):
#     global state
#     if state == 3:
#         state -= 1
#         await context.send("Undoing Continue Command. Run `--continue` when you're ready!")
#     else:
#         await context.send("ERROR invalid command at this time")

async def wine_3(context):
    await context.send("THE GAME BEGINS! OUR TEAMS ARE:")
    await print_teams(context)
    await context.send(file=discord.File('wine_cheese.png'))
    with open('messages/wine_3_0.txt','r') as file:
            message = file.read()
            await context.send(message)

    vc = cast(VoiceClient, context.voice_client)
    print("Playing Wine Song")
    vc.play(FFmpegPCMAudio("wine_music.mp3"))
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Wine Song done")
    print("Playing buzzer")
    vc.play(FFmpegPCMAudio("buzzer.mp3"))
    await context.send(file=discord.File('intimidate.jpg'))
    with open('messages/wine_3_1.txt','r') as file:
            message = file.read()
            await context.send(message)
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Buzzer done")

@bot.command(name='rules')
async def print_rules(context):
    await context.send(file=discord.File(game_image))
    with open('messages/rules.txt','r') as file:
        message = file.read()
        message = message.replace("[GAME NAME]", game_name)
        await context.send(message)
    await context.send(file=discord.File("full_rules.pdf"))

async def game_begins_5(context):
    with open('messages/mind_instructions.txt','r') as file:
        message = file.read()
        await context.send(message)

async def take_turn(context):
    status = f"{emojis[0]} <@&{team_role_ids[0]}> is in the {text_level(0)} LEVEL and has {team_cards[0][0]}/4 Mind cards, {team_cards[0][1]}/3 Body cards, {team_cards[0][2]}/4 Spirit cards\n"
    status += f"{emojis[1]} <@&{team_role_ids[1]}> is in the {text_level(1)} LEVEL and has {team_cards[1][0]}/4 Mind cards, {team_cards[1][1]}/3 Body cards, {team_cards[1][2]}/4 Spirit cards"
    await context.send(status)

    status_string = f"\n{emojis[turn]} <@&{team_role_ids[turn]}> It's your turn! The next player's card is:\n\n\n"
    card_text = f"** {text_level(turn)} card **"
    global last_card_type
    card_text, last_card_type = cards.pick_card(levels[turn])
    status_string +=card_text+"\n"
    status_string +="If the card is successfully completed by you, or stolen by the other team, type `--cardwon @(TeamWhoWonCard)` (@'ing the appropriate team)\n"
    status_string +="If both teams failed, type `--pass`"

    await context.send(status_string)

@bot.command(name='cardwon')
async def cardwon_6(context, arg=None):
    global state
    if state != 6:
        await context.send("ERROR invalid command at this time")
        return
    if arg ==None:
        await context.send("ERROR please @ The team who won the card")
        return
    try:
        team_won = team_role_ids.index(int(arg[3:-1]))
    except Exception as e:
        await context.send("ERROR please @ The team who won the card")
        return

    global turn
    turn = 1-turn


    if last_card_type <3:
        team_cards[team_won][last_card_type] +=1

    if levels[team_won] == 0 and  team_cards[team_won][0] >=4:
        state = 7
        levels[team_won] += 1
        if levels[1-team_won] < 1:
            await level2_intermission(context, team_won)
        else:
            await level2_losers(context, team_won)
        return
    if levels[team_won]==1 and team_cards[team_won][1] >=3:
        levels[team_won] += 1
        state = 7
        if levels[1-team_won] < 2:
            await level3_intermission(context, team_won)
        else:
            await level3_losers(context, team_won)
        return
    if levels[team_won]==2 and team_cards[team_won][2]>=4:
        levels[team_won] += 1
        state = 8
        await winners(context, team_won)
        return

    await take_turn(context)

@bot.command(name='cheat')
async def cheating(context, arg=None):
    global state
    if state != 6:
        await context.send("ERROR invalid command at this time")
        return
    if arg ==None:
        await context.send("ERROR please @ The team who cheated")
        return
    try:
        cheater_team = team_role_ids.index(int(arg[3:-1]))
    except Exception as e:
        await context.send("ERROR please @ the team who cheated")
        return
    other_team = 1-cheater_team
    if levels[cheater_team] !=0 and levels[other_team] < levels[cheater_team]:
        levels[other_team] = levels[cheater_team]
    elif levels[cheater_team] == 0:
        team_cards[cheater_team] = [0,0,0]
        levels[other_team] +=1
    await context.send("The Cheaters Have Been Penalized. The current status is now:")
    status = f"{emojis[0]} <@&{team_role_ids[0]}> is in the {text_level(0)} LEVEL and has {team_cards[0][0]}/4 Mind Cards, {team_cards[0][1]}/3 Body Cards, {team_cards[0][2]}/4 Spirit Cards\n"
    status += f"{emojis[1]} <@&{team_role_ids[1]}> is in the {text_level(1)} LEVEL and has {team_cards[1][0]}/4 Mind Cards, {team_cards[1][1]}/3 Body Cards, {team_cards[1][2]}/4 Spirit Cards"
    await context.send(status)
    await context.send("Justice has been served. Please carry on.")



@bot.command(name='pass')
async def pass_6(context):
    global state
    if state != 6:
        await context.send("ERROR invalid command at this time")
        return
    global turn
    turn = 1-turn
    await take_turn(context)

async def level2_intermission(context, team):
    with open('messages/intermissionmind_0.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)
    
    vc = cast(VoiceClient, context.voice_client)
    print("Playing Wine Song")
    vc.play(FFmpegPCMAudio("wine_music.mp3"))
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Wine Song done")
    print("Playing buzzer")
    vc.play(FFmpegPCMAudio("buzzer.mp3"))

    with open('messages/intermissionmind_1.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)

    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Buzzer done")

async def level2_losers(context, team):
    with open('messages/losersmind_0.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)

async def level3_intermission(context, team):
    with open('messages/intermissionbody_0.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)
    
    vc = cast(VoiceClient, context.voice_client)
    print("Playing Wine Song")
    vc.play(FFmpegPCMAudio("wine_music.mp3"))
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Wine Song done")
    print("Playing buzzer")
    vc.play(FFmpegPCMAudio("buzzer.mp3"))

    with open('messages/intermissionbody_1.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)

    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Buzzer done")

async def level3_losers(context, team):
    with open('messages/losersbody_0.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        await context.send(message)


async def winners(context, team):
    with open('messages/win.txt','r') as file:
        message = file.read()
        message = message.replace("[Team Name]", f"<@&{team_role_ids[team]}>")
        message = message.replace("[GAME NAME]", game_name)
        await context.send(message)
    other_team = 1-team
    _, tokens = await get_player_tokens(other_team,context)
    for tok in tokens:
        await context.send(file=discord.File(tok))


async def gotobed(context):
    with open('messages/gotobed_0.txt','r') as file:
        message = file.read()
        await context.send(message)
    await asyncio.sleep(3)
    with open('messages/gotobed_1.txt','r') as file:
        message = file.read()
        await context.send(message+"....")
    await asyncio.sleep(2)
    vc = cast(VoiceClient, context.voice_client)
    print("Playing Theme Song")
    vc.play(FFmpegPCMAudio("its-always-sunny-in-philadelphia-theme-song.mp3"))
    await context.send(file=discord.File("ganggoestobed.png"))
    await context.send(file=discord.File("tomorrow.png"))
    while vc.is_playing():
        await asyncio.sleep(0.01)
    print("Theme Song done")

#bot.run('[TOKEN HERE]')
