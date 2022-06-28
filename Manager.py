import json
import random
import math
import copy

def init(module):
    global game
    game = module

def open_rom(path):
    global rom
    rom = open(path, "r+b")

def close_rom():
    rom.close()

def randomize_enemy_levels():
    for i in game.values["Enemy"]:
        if not i in game.level_skip:
            if game.values["Enemy"][i]["MainEntry"]:
                #Make it so that the final boss have opposite levels of each other
                #This prevents the last fight from being too hard or too easy
                if i == game.final_bosses[0] or "Intro" in i:
                    game.values["Enemy"][i]["Level"] = random.randint(1, 99)
                elif i == game.final_bosses[1]:
                    game.values["Enemy"][i]["Level"] = abs(game.values["Enemy"][game.final_bosses[0]]["Level"] - 100)
                else:
                    game.values["Enemy"][i]["Level"] = random_weighted(game.values["Enemy"][i]["Level"], 1, 99, 1, 4)
            else:
                game.values["Enemy"][i]["Level"] = game.values["Enemy"][get_enemy_name(get_enemy_id(i) - 1)]["Level"]

def randomize_enemy_resistances():
    for i in game.values["Enemy"]:
        if not i in game.resist_skip:
            for e in game.attributes:
                if game.values["Enemy"][i]["MainEntry"]:
                    game.values["Enemy"][i]["Resistances"][e] = random.choice(game.resist_pool)
                else:
                    game.values["Enemy"][i]["Resistances"][e] = game.values["Enemy"][get_enemy_name(get_enemy_id(i) - 1)]["Resistances"][e]

def multiply_damage(multiplier):
    for i in game.values["Enemy"]:
        game.values["Enemy"][i]["MaxDamage"] = round(game.values["Enemy"][i]["MaxDamage"]*multiplier**game.damage_rate)
        if game.values["Enemy"][i]["MaxDamage"] > 5000:
            game.values["Enemy"][i]["MaxDamage"] = 5000

def check_meaningful_value(value):
    #If the last 3 numbers of the input value are almost a succession of the same number round the value to that
    for i in range(111, 999, 111):
        if (value % 1000) - 1 == i:
            return value - 1
        elif (value % 1000) + 1 == i:
            return value + 1
    return value

def create_weighted_list(value, minimum, maximum, step, deviation):
    #Create a list in a range with higher odds around a specific value
    list = []
    for i in [(minimum, value + 1), (value, maximum + 1)]:
        sublist = []
        distance = abs(i[0]-i[1])
        new_deviation = round(deviation*(distance/(maximum-minimum)))*2
        for e in range(i[0], i[1]):
            if e % step == 0:
                difference = abs(e-value)
                for o in range(2**(abs(math.ceil(difference*new_deviation/distance)-new_deviation))):
                    sublist.append(e)
        list.append(sublist)
    return list

def random_weighted(value, minimum, maximum, step, deviation):
    return random.choice(random.choice(create_weighted_list(value, minimum, maximum, step, deviation)))

def get_enemy_id(name):
    try:
        return list(game.values["Enemy"]).index(name)
    except ValueError:
        return -1

def get_enemy_name(id):
    if id in game.special_id_to_enemy:
        return game.special_id_to_enemy[id]
    else:
        try:
            return list(game.values["Enemy"])[id]
        except IndexError:
            return "Unknown"