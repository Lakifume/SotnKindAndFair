import random

def init(module):
    global game
    game = module
    global wheight_exponents
    wheight_exponents = [3, 1.8, 1.25]

def open_rom(path):
    global rom
    rom = open(path, "r+b")

def close_rom():
    rom.close()

def lerp(minimum, maximum, alpha):
    return minimum + (maximum - minimum)*alpha

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

def set_enemy_level_wheight(wheight):
    global enemy_level_wheight
    enemy_level_wheight = wheight_exponents[wheight - 1]

def set_enemy_tolerance_wheight(wheight):
    global enemy_tolerance_wheight
    enemy_tolerance_wheight = wheight_exponents[wheight - 1]

def randomize_enemy_levels():
    for enemy in game.values["Enemy"]:
        if enemy in game.level_skip:
            continue
        if game.values["Enemy"][enemy]["MainEntry"]:
            #Make it so that the final boss have opposite levels of each other
            #This prevents the last fight from being too hard or too easy
            if enemy == game.final_bosses[0]:
                game.values["Enemy"][enemy]["Level"] = random_weighted(50, 1, 99, 1, enemy_level_wheight)
            elif enemy == game.final_bosses[1]:
                game.values["Enemy"][enemy]["Level"] = abs(game.values["Enemy"][game.final_bosses[0]]["Level"] - 100)
            else:
                game.values["Enemy"][enemy]["Level"] = random_weighted(game.values["Enemy"][enemy]["Level"], 1, 99, 1, enemy_level_wheight)
        else:
            game.values["Enemy"][enemy]["Level"] = game.values["Enemy"][get_enemy_name(get_enemy_id(enemy) - 1)]["Level"]

def randomize_enemy_resistances():
    for enemy in game.values["Enemy"]:
        if enemy in game.resist_skip:
            continue
        if game.values["Enemy"][enemy]["MainEntry"]:
            #Determine average
            average = 0
            for attr in game.attributes:
                average += min(max(game.values["Enemy"][enemy]["Resistances"][attr], 0), 2)
            average /= len(game.attributes)
            #Randomize around average
            for attr in game.attributes:
                game.values["Enemy"][enemy]["Resistances"][attr] = max(random_weighted(average, game.resist_range[0], game.resist_range[1], 1, enemy_tolerance_wheight), 0)
        else:
            for attr in game.attributes:
                game.values["Enemy"][enemy]["Resistances"][attr] = game.values["Enemy"][get_enemy_name(get_enemy_id(enemy) - 1)]["Resistances"][attr]

def multiply_damage(multiplier):
    for enemy in game.values["Enemy"]:
        game.values["Enemy"][enemy]["MaxDamage"] = min(round(game.values["Enemy"][enemy]["MaxDamage"]*multiplier**game.damage_rate), 5000)

def check_meaningful_value(value):
    #If the last 3 numbers of the input value are almost a succession of the same number round the value to that
    for num in range(111, 999, 111):
        if (value % 1000) - 1 == num:
            return value - 1
        elif (value % 1000) + 1 == num:
            return value + 1
    return value

def calculate_stat_with_level(minimum, maximum, level):
    return round(((maximum - minimum)/98)*(level-1) + minimum)

def squircle(value, exponent):
    return -(1-value**exponent)**(1/exponent)+1

def random_weighted(value, minimum, maximum, step, exponent):
    full_range = maximum - minimum
    if random.random() < 0.5:
        distance = maximum - value
        exponent = (exponent-1)*(0.5*4**(distance/full_range))+1
        return round(round((value + squircle(random.random(), exponent)*distance)/step)*step, 3)
    distance = value - minimum
    exponent = (exponent-1)*(0.5*4**(distance/full_range))+1
    return round(round((value - squircle(random.random(), exponent)*distance)/step)*step, 3)

def get_enemy_id(name):
    try:
        return list(game.values["Enemy"]).index(name)
    except ValueError:
        return None

def get_enemy_name(id):
    if id in game.special_id_to_enemy:
        return game.special_id_to_enemy[id]
    try:
        return list(game.values["Enemy"])[id]
    except IndexError:
        return None