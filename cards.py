with open("card_data/body.txt", "r") as f:
    body = f.readlines()
with open("card_data/mind.txt", "r") as f:
    mind = f.readlines()
with open("card_data/spirit.txt", "r") as f:
    spirit = f.readlines()
with open("card_data/chance.txt", "r") as f:
    chance = f.readlines()

import random
def pick_card(level):
    chance_cards = chance[level::3]
    if level ==0:
        base_cards = mind
    elif level ==1:
        base_cards = body
    elif level ==2:
        base_cards = spirit
    card = random.choice(base_cards+chance_cards)
    if card in base_cards:
        return card, level
    elif card in chance_cards:
        return card, 3
    else:
        return card, -1

