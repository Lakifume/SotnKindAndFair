import Manager
import json
import random
import os

def init():
    global damage_rate
    damage_rate = 1.0
    global attributes
    attributes = {
        "HIT": 0x0020,
        "CUT": 0x0040,
        "POI": 0x0080,
        "CUR": 0x0100,
        "STO": 0x0200,
        "WAT": 0x0400,
        "DAR": 0x0800,
        "HOL": 0x1000,
        "ICE": 0x2000,
        "LIG": 0x4000,
        "FLA": 0x8000
    }
    #Enemy Lists
    global level_skip
    level_skip = [
        "Zombie",
        "Warg"
    ]
    global resist_skip
    resist_skip = [
        "Intro Dracula 1",
        "Intro Dracula 2"
    ]
    global static_enemy
    static_enemy = [
        "Stone Skull",
        "Spike ball",
        "Evil Priest"
    ]
    level_skip.extend(static_enemy)
    resist_skip.extend(static_enemy)
    global final_bosses
    final_bosses = ("Shaft", "Dracula")
    global resist_range
    resist_range = (-2, 4)
    global special_id_to_enemy
    special_id_to_enemy = {}
    #Offsets
    global removal_offset
    removal_offset = [
        0x1195f8,
        0x119658,
        0x1196b8,
        0x1196f4,
        0x119730,
        0x119774,
        0x119634,
        0x119648,
        0x119694,
        0x1196a8,
        0x1196d0,
        0x1196e4,
        0x11970c,
        0x119720,
        0x119750,
        0x119764,
        0x1197b0,
        0x1197c4,
        0x4b6844c,
        0x4b6844e,
        0x4b68452,
        0x4b68450,
        0x4b68454,
        0x4b68456
    ]
    global forced_drops
    forced_drops = [
        0x4BC9324,
        0x4BC9328
    ]

def open_json():
    global offsets
    offsets = {}
    global values
    values = {}
    for file in os.listdir("Data\\Symphony\\Offsets"):
        file_name = os.path.splitext(file)[0]
        offsets[file_name] = {}
        with open(f"Data\\Symphony\\Offsets\\{file}", "r") as file_reader:
            offsets[file_name] = json.load(file_reader)
    for file in os.listdir("Data\\Symphony\\Values"):
        file_name = os.path.splitext(file)[0]
        with open(f"Data\\Symphony\\Values\\{file}", "r") as file_reader:
            values[file_name] = json.load(file_reader)
    global dictionary
    dictionary = {}
    for file in os.listdir("Data\\Symphony\\Dicts"):
        file_name = os.path.splitext(file)[0]
        with open(f"Data\\Symphony\\Dicts\\{file}", "r") as file_reader:
            dictionary[file_name] = json.load(file_reader)

def get_seed():
    #If the rom is randomized reuse its seed
    Manager.rom.seek(0x4389C6C)
    seed = int.from_bytes(Manager.rom.read(30), "big")
    if seed == 0x496E7075742081688168524943485445528168816820746F20706C617900:
        return random.random()
    start_with_spirit_orb()
    return seed

def apply_ppf_patch(patch):
    #Replicate PPF Studio's process of applying patches to not have to include it in the download
    with open(f"Data\\Symphony\\Patches\\{patch}.ppf", "r+b") as mod:
        progress = 0x3C
        while progress < os.path.getsize(f"Data\\Symphony\\Patches\\{patch}.ppf"):
            mod.seek(progress)
            offset = int.from_bytes(mod.read(8), "little")
            length = int.from_bytes(mod.read(1), "little")
            change = int.from_bytes(mod.read(length), "little")
            Manager.rom.seek(offset)
            Manager.rom.write(change.to_bytes(length, "little"))
            progress += 9 + length

def get_item_address():
    #candle
    zone_pos = 0x055724b8
    entity = 0x2494
    address = entity + 8
    print("0x{:04x}".format(zone_pos + address + address // 0x800 * 0x130))
    #item
    zone_pos = 0x04675f08
    zone_items = 0x0ec0
    index = 4
    address = zone_items + 0x02 * index
    print("0x{:04x}".format(zone_pos + address + address // 0x800 * 0x130))

def start_with_spirit_orb():
    #Start the player with spirit orb and fairy scroll
    Manager.rom.seek(0xFA97C)
    Manager.rom.write((0x0C04DB00).to_bytes(4, "little"))
    Manager.rom.seek(0x158C98)
    Manager.rom.write((0x34020003).to_bytes(4, "little"))
    Manager.rom.write((0x3C038009).to_bytes(4, "little"))
    Manager.rom.write((0xA062796F).to_bytes(4, "little"))
    Manager.rom.write((0xA0627973).to_bytes(4, "little"))
    Manager.rom.write((0x0803924F).to_bytes(4, "little"))
    Manager.rom.write((0x00000000).to_bytes(4, "little"))
    
def keep_equipment():
    #Prevent Death's cutscene from taking Alucard's equipment
    for offset in removal_offset:
        Manager.rom.seek(offset)
        Manager.rom.write((0).to_bytes(2, "little"))

def free_library():
    #Place a library card before Slogra and Gaibon in case they are near unbeatable
    drop = forced_drops[0]
    forced_drops.pop(0)
    Manager.rom.seek(drop)
    Manager.rom.write((0xA6).to_bytes(2, "little"))
    
def unused():
    #Invulnerability
    Manager.rom.seek(0x126626)
    Manager.rom.write((0).to_bytes(1, "little"))
    Manager.rom.seek(0x3A06F52)
    Manager.rom.write((0).to_bytes(1, "little"))
    Manager.rom.seek(0x59EB092)
    Manager.rom.write((0x1000).to_bytes(2, "little"))
    Manager.rom.seek(0x59EBC7A)
    Manager.rom.write((0x1000).to_bytes(2, "little"))
    #No experience
    Manager.rom.seek(0x117cf6)
    Manager.rom.write((0).to_bytes(1, "little"))
    Manager.rom.seek(0x117da0)
    Manager.rom.write((0).to_bytes(4, "little"))

def all_bigtoss():
    #Give every enemy attack the guaranteed bigtoss property
    for enemy in values["Enemy"]:
        if "Intro" in enemy or enemy == "Evil Priest":
            continue
        values["Enemy"][enemy]["DamageType"] = "0x{:04x}".format((int(values["Enemy"][enemy]["DamageType"], 16)//16)*16 + 5)
        for index in range(len(values["Enemy"][enemy]["AttackType"])):
            values["Enemy"][enemy]["AttackType"][index] = "0x{:04x}".format((int(values["Enemy"][enemy]["AttackType"][index], 16)//16)*16 + 5)

def reduce_bigtoss_damage(damage):
    #Reduce damage in such a way that the total bigtoss damage will on average be equal to regular damage
    return round(damage*Manager.lerp(1/1.5, 1, 240/(240 + damage)))

def infinite_wing_smash():
    #Give wing smash the same properties as in the saturn version but at a higher cost
    values["Spell"]["Wing Smash"]["ManaCost"] = round(values["Spell"]["Wing Smash"]["ManaCost"]*3.125)
    Manager.rom.seek(0x134990)
    Manager.rom.write((0).to_bytes(4, "little"))

def remove_enemy_drops():
    for enemy in offsets["Enemy"]:
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Drop1"]["Offset"], 16)))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop1"]["Length"], "little"))
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Drop2"]["Offset"], 16)))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop2"]["Length"], "little"))
    #Give a weapon at the start to compensate
    positive_weapons = []
    for item_id in dictionary["ItemId"]:
        if dictionary["ItemId"][item_id] in values["HandItem"]:
            if values["HandItem"][dictionary["ItemId"][item_id]]["Attack"] > 0 and not values["HandItem"][dictionary["ItemId"][item_id]]["Sprite"] in ["0x0f", "0x15"]:
                positive_weapons.append(item_id)
    drop = forced_drops[0]
    forced_drops.pop(0)
    Manager.rom.seek(drop)
    Manager.rom.write(int(random.choice(positive_weapons), 16).to_bytes(2, "little"))

def check_offset(offset):
    #Shift the input offset if it falls within one of the weird chunks of bytes
    start = 0x18
    position = int((offset - start)/0x930) + 1
    if offset >= start + 0x930*position - 0x130:
        offset += 0x130
    return offset

def write_simple_data():
    #Write data that doesn't need any specific process
    for file in offsets:
        if file == "Enemy":
            continue
        for entry in offsets[file]:
            try:
                for data in values[file][entry]:
                    try:
                        if dictionary["Properties"][file][data]["RawHex"]:
                            values[file][entry][data] = int(values[file][entry][data], 16)
                        else:
                            values[file][entry][data] = values[file][entry][data] & (0x100**dictionary["Properties"][file][data]["Length"]-1)
                        Manager.rom.seek(check_offset(int(offsets[file][entry], 16) + int(dictionary["Properties"][file][data]["Offset"], 16)))
                        Manager.rom.write(int(values[file][entry][data]).to_bytes(dictionary["Properties"][file][data]["Length"], "little"))
                    except (KeyError, TypeError):
                        continue
            except (KeyError, TypeError):
                continue

def write_complex_data():
    #ENEMY
    for enemy in offsets["Enemy"]:
        #Level
        level = values["Enemy"][enemy]["Level"]
        level = level & (0x100**dictionary["Properties"]["Enemy"]["Level"]["Length"]-1)
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Level"]["Offset"], 16)))
        Manager.rom.write(level.to_bytes(dictionary["Properties"]["Enemy"]["Level"]["Length"], "little"))
        #Health
        max_health = values["Enemy"][enemy]["MaxHealth"]
        min_health = int(max_health/100)
        if max_health == 0x7FFF:
            min_health = max_health
        health = Manager.calculate_stat_with_level(min_health, max_health, level)
        health = Manager.check_meaningful_value(health)
        health = health & (0x100**dictionary["Properties"]["Enemy"]["Health"]["Length"]-1)
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Health"]["Offset"], 16)))
        Manager.rom.write(health.to_bytes(dictionary["Properties"]["Enemy"]["Health"]["Length"], "little"))
        #Damage
        max_damage = values["Enemy"][enemy]["MaxDamage"]
        min_damage = int(max_damage/30)
        if enemy in static_enemy:
            min_damage = max_damage
        damage = Manager.calculate_stat_with_level(min_damage, max_damage, level)
        damage = damage & (0x100**dictionary["Properties"]["Enemy"]["Damage"]["Length"]-1)
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16)))
        if not values["Enemy"][enemy]["HasContact"]:
            Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
        elif int(values["Enemy"][enemy]["DamageType"], 16) % 16 == 5:
            Manager.rom.write(reduce_bigtoss_damage(damage).to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
        else:
            Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
        #Defense
        max_defense = values["Enemy"][enemy]["MaxDefense"]
        min_defense = int(max_defense/10)
        defense = Manager.calculate_stat_with_level(min_defense, max_defense, level)
        defense = defense & (0x100**dictionary["Properties"]["Enemy"]["Defense"]["Length"]-1)
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Defense"]["Offset"], 16)))
        Manager.rom.write(defense.to_bytes(dictionary["Properties"]["Enemy"]["Defense"]["Length"], "little"))
        #Experience
        max_experience = values["Enemy"][enemy]["MaxExperience"]
        min_experience = int(max_experience/100)
        experience = Manager.calculate_stat_with_level(min_experience, max_experience, level)
        experience = int(experience*Manager.lerp(1, 1/3, min(level/50, 1)))
        experience = Manager.check_meaningful_value(experience)
        experience = experience & (0x100**dictionary["Properties"]["Enemy"]["Experience"]["Length"]-1)
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Experience"]["Offset"], 16)))
        Manager.rom.write(experience.to_bytes(dictionary["Properties"]["Enemy"]["Experience"]["Length"], "little"))
        #Surface
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Surface"]["Offset"], 16)))
        Manager.rom.write(int(values["Enemy"][enemy]["Surface"], 16).to_bytes(dictionary["Properties"]["Enemy"]["Surface"]["Length"], "little"))
        #Damage type
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["DamageType"]["Offset"], 16)))
        Manager.rom.write(int(values["Enemy"][enemy]["DamageType"], 16).to_bytes(dictionary["Properties"]["Enemy"]["DamageType"]["Length"], "little"))
        #Make stopwatch tolerance scale with level
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + 37))
        if values["Enemy"][enemy]["IsBoss"]:
            Manager.rom.write((0x30).to_bytes(1, "little"))
        elif values["Enemy"][enemy]["Level"] >= 40:
            Manager.rom.write((0x34).to_bytes(1, "little"))
        elif values["Enemy"][enemy]["Level"] >= 20:
            Manager.rom.write((0x16).to_bytes(1, "little"))
        else:
            Manager.rom.write((0x14).to_bytes(1, "little"))
        #Remove all stunframes from enemies
        offset = check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + 38)
        Manager.rom.seek(offset)
        if int.from_bytes(Manager.rom.read(1), "little") < 0x40:
            Manager.rom.seek(offset)
            Manager.rom.write((0x40).to_bytes(1, "little"))
        #Attack
        for index in range(len(offsets["Enemy"][enemy]["AttackAddress"])):
            #Attack correction
            attack = round(damage*values["Enemy"][enemy]["AttackCorrection"][index]**damage_rate)
            attack = attack & (0x100**dictionary["Properties"]["Enemy"]["Damage"]["Length"]-1)
            Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["AttackAddress"][index], 16) + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16)))
            if int(values["Enemy"][enemy]["AttackType"][index], 16) % 16 == 5:
                Manager.rom.write(reduce_bigtoss_damage(attack).to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
            else:
                Manager.rom.write(attack.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
            #Attack type
            Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["AttackAddress"][index], 16) + int(dictionary["Properties"]["Enemy"]["DamageType"]["Offset"], 16)))
            Manager.rom.write(int(values["Enemy"][enemy]["AttackType"][index], 16).to_bytes(dictionary["Properties"]["Enemy"]["DamageType"]["Length"], "little"))
            #Attack stopwatch tolerance
            Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["AttackAddress"][index], 16) + 37))
            if values["Enemy"][enemy]["Level"] >= 40 or values["Enemy"][enemy]["IsBoss"]:
                Manager.rom.write((0x20).to_bytes(1, "little"))
            elif values["Enemy"][enemy]["Level"] >= 20:
                Manager.rom.write((0x12).to_bytes(1, "little"))
            else:
                Manager.rom.write((0x00).to_bytes(1, "little"))
            #Attack no stun
            offset = check_offset(int(offsets["Enemy"][enemy]["AttackAddress"][index], 16) + 38)
            Manager.rom.seek(offset)
            if int.from_bytes(Manager.rom.read(1), "little") < 0x40:
                Manager.rom.seek(offset)
                Manager.rom.write((0x40).to_bytes(1, "little"))
    #Display some damage and sound cues on enemies that lack them
    #Intro Dracula shown damage
    Manager.rom.seek(0xB7677)
    Manager.rom.write((0x08).to_bytes(1, "little"))
    Manager.rom.seek(0xB76EF)
    Manager.rom.write((0x08).to_bytes(1, "little"))
    #Zombie Trevor hit sound
    Manager.rom.seek(0xB94E4)
    Manager.rom.write((0x10).to_bytes(1, "little"))
    #Zombie Trevor shown damage
    Manager.rom.seek(0xB94E7)
    Manager.rom.write((0x08).to_bytes(1, "little"))
    #Beezelbub Flies shown damage
    Manager.rom.seek(0xB9267)
    Manager.rom.write((0x08).to_bytes(1, "little"))
    #Shaft Orb shown damage
    Manager.rom.seek(0xB92B7)
    Manager.rom.write((0x08).to_bytes(1, "little"))
    #Widen some hitboxes so that it is no longer possible to crouch below them
    #Discus Lord saw
    Manager.rom.seek(0xB65DA)
    Manager.rom.write((0x1818).to_bytes(2, "little"))
    #Hippogryph fire breath
    Manager.rom.seek(0xB8ECA)
    Manager.rom.write((0x0A02).to_bytes(2, "little"))
    #Cerberus fireball
    Manager.rom.seek(0xB99AA)
    Manager.rom.write((0x0C0A).to_bytes(2, "little"))
    #Medusa laser
    Manager.rom.seek(0xB9A4A)
    Manager.rom.write((0x0220).to_bytes(2, "little"))
    #Remove the hitbox from Dracula's main body to only leave the hands vulnerable
    Manager.rom.seek(0xB9C02)
    Manager.rom.write((0x0000).to_bytes(2, "little"))
    
    #EQUIPMENT
    for file in ["Enemy", "Equipment"]:
        for entry in offsets[file]:
            if file == "Enemy":
                offset = int(offsets[file][entry]["EnemyAddress"], 16)
            else:
                offset = int(offsets[file][entry], 16)
            #Resistances
            if entry == "Galamoth Head":
                weak = 0
                strong = 0
                immune = 0xFFE0
                absorb = 0
            else:
                weak = 0
                strong = 0
                immune = 0
                absorb = 0
                for attr in attributes:
                    if values[file][entry]["Resistances"][attr] == 0:
                        weak += attributes[attr]
                    elif values[file][entry]["Resistances"][attr] == 2:
                        strong += attributes[attr]
                    elif values[file][entry]["Resistances"][attr] == 3:
                        immune += attributes[attr]
                    elif values[file][entry]["Resistances"][attr] == 4:
                        absorb += attributes[attr]
            Manager.rom.seek(check_offset(offset + int(dictionary["Properties"][file]["Weak"]["Offset"], 16)))
            Manager.rom.write(weak.to_bytes(dictionary["Properties"][file]["Weak"]["Length"], "little"))
            Manager.rom.seek(check_offset(offset + int(dictionary["Properties"][file]["Strong"]["Offset"], 16)))
            Manager.rom.write(strong.to_bytes(dictionary["Properties"][file]["Strong"]["Length"], "little"))
            Manager.rom.seek(check_offset(offset + int(dictionary["Properties"][file]["Immune"]["Offset"], 16)))
            Manager.rom.write(immune.to_bytes(dictionary["Properties"][file]["Immune"]["Length"], "little"))
            Manager.rom.seek(check_offset(offset + int(dictionary["Properties"][file]["Absorb"]["Offset"], 16)))
            Manager.rom.write(absorb.to_bytes(dictionary["Properties"][file]["Absorb"]["Length"], "little"))

    #HANDITEM SPELL
    for file in ["HandItem", "Spell"]:
        for entry in offsets[file]:
            #Element
            total = 0
            for attr in attributes:
                if values[file][entry]["Element"][attr]:
                    total += attributes[attr]
            Manager.rom.seek(check_offset(int(offsets[file][entry], 16) + int(dictionary["Properties"][file]["Element"]["Offset"], 16)))
            Manager.rom.write(total.to_bytes(dictionary["Properties"][file]["Element"]["Length"], "little"))

    #SHOP
    #Make shop prices dynamic with the items that are found on each slot
    #This prevents being able to easily purchase an unreasonable amount of broken items
    for item in offsets["Shop"]:
        Manager.rom.seek(int(offsets["Shop"][item], 16) - 4)
        shift = 0xA9 if int.from_bytes(Manager.rom.read(1), "little") != 0 else 0
        Manager.rom.seek(int(offsets["Shop"][item], 16) - 2)
        price = dictionary["ItemPrice"][dictionary["ItemId"]["0x{:04x}".format(int.from_bytes(Manager.rom.read(2), "little") + shift)]]
        price = price & 0xFFFFFFFF
        Manager.rom.write(int(price).to_bytes(4, "little"))
    Manager.rom.seek(0x47A31E8)
    Manager.rom.write((100).to_bytes(4, "little"))

    #STAT
    #Change the starting stats
    for stat in offsets["Stat"]:
        values["Stat"][stat] = values["Stat"][stat] & 0xFFFF
        Manager.rom.seek(int(offsets["Stat"][stat], 16))
        Manager.rom.write(int(values["Stat"][stat]).to_bytes(2, "little"))
    #One of the health bonus stats does not update automatically
    Manager.rom.seek(0x119CC4)
    Manager.rom.write(int(values["Stat"]["Health"] + 5).to_bytes(2, "little"))

    #DESCRIPTION
    #Update some descriptions to reflect all the changes
    Manager.rom.seek(0xF2400)
    Manager.rom.write(str.encode("Shocking"))
    Manager.rom.seek(0xF2538)
    Manager.rom.write(str.encode(" flail         "))
    Manager.rom.seek(0xF2639)
    Manager.rom.write(str.encode("               "))
    Manager.rom.seek(0xF2735)
    Manager.rom.write(str.encode("EEP"))
    Manager.rom.seek(0xF2740)
    Manager.rom.write(str.encode("Blazing sword of flame "))
    Manager.rom.seek(0xF3BF8)
    Manager.rom.write(str.encode("Immunity to all status effects"))
    Manager.rom.seek(0xF3C75)
    Manager.rom.write(str.encode("O"))
    Manager.rom.seek(0xF3C9A)
    Manager.rom.write(str.encode("T  "))
    Manager.rom.seek(0xF43FC)
    Manager.rom.write(str.encode("Immune to water "))
    Manager.rom.seek(0xF4420)
    Manager.rom.write(str.encode("Affection for cats          "))
    Manager.rom.seek(0xF4450)
    Manager.rom.write(str.encode("Immune to lightning         "))
    Manager.rom.seek(0xF4480)
    Manager.rom.write(str.encode("Immune to darkness          "))
    Manager.rom.seek(0xF44B0)
    Manager.rom.write(str.encode("Immune to ice            "))
    Manager.rom.seek(0xF44DC)
    Manager.rom.write(str.encode("Immune to fire            "))
    Manager.rom.seek(0xF4508)
    Manager.rom.write(str.encode("Immune to light           "))
    Manager.rom.seek(0xF4844)
    Manager.rom.write(str.encode("Strong vs. dark attacks   "))
    Manager.rom.seek(0xF486C)
    Manager.rom.write(str.encode("Immunity to all status effects"))
    Manager.rom.seek(0xF48C4)
    Manager.rom.write(str.encode("Stro"))
    Manager.rom.seek(0xF49F8)
    Manager.rom.write(str.encode("ng vs D water attacks "))
    Manager.rom.seek(0xF49FD)
    Manager.rom.write((0x81).to_bytes(1, "little"))
    Manager.rom.seek(0xF4A10)
    Manager.rom.write(str.encode("7ATER MAIL    "))
    Manager.rom.seek(0xF4A15)
    Manager.rom.write((0).to_bytes(1, "little"))
    Manager.rom.seek(0xF4A1A)
    Manager.rom.write((0).to_bytes(4, "little"))
    Manager.rom.seek(0xF4A2F)
    Manager.rom.write(str.encode(" attacks       "))
    Manager.rom.seek(0xF4A8C)
    Manager.rom.write(str.encode(" attacks       "))
    Manager.rom.seek(0xF2ABC)
    Manager.rom.write(str.encode("DEF { P O  "))
    Manager.rom.seek(0xF2ABF)
    Manager.rom.write((0x81).to_bytes(1, "little"))
    Manager.rom.seek(0xF2AC1)
    Manager.rom.write((0x82).to_bytes(1, "little"))
    Manager.rom.seek(0xF2AC3)
    Manager.rom.write((0x82).to_bytes(1, "little"))

    #MISC
    #Just some personal tweaks
    Manager.rom.seek(0x4369E87)
    Manager.rom.write(str.encode("KOJI  IGA"))
    Manager.rom.seek(0x4369EE1)
    Manager.rom.write(str.encode("KOJI  IGA"))
    Manager.rom.seek(0x4369FBC)
    Manager.rom.write(str.encode("KOJI  IGA"))
    Manager.rom.seek(0x3A06851)
    Manager.rom.write((0x40).to_bytes(1, "little"))
    #
    #Manager.rom.seek(0x4678F00)
    #Manager.rom.write((0x0022).to_bytes(2, "little"))

def create_enemy_log():
    log = {}
    for enemy in values["Enemy"]:
        log[enemy] = {}
        #Stats
        for stat in ["Level", "Health", "Damage", "Defense", "Experience"]:
            Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"][stat]["Offset"], 16)))
            log[enemy][stat] = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][stat]["Length"]), "little")
            if log[enemy][stat] > (0x100**dictionary["Properties"]["Enemy"][stat]["Length"]/2) - 1:
                log[enemy][stat] -= 0x100**dictionary["Properties"]["Enemy"][stat]["Length"]
        #Resistances
        log[enemy]["Resistances"] = {}
        for attr in attributes:
            log[enemy]["Resistances"][attr] = 1
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Weak"]["Offset"], 16)))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Weak"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 0
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Strong"]["Offset"], 16)))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Strong"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 2
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Immune"]["Offset"], 16)))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Immune"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 3
        Manager.rom.seek(check_offset(int(offsets["Enemy"][enemy]["EnemyAddress"], 16) + int(dictionary["Properties"]["Enemy"]["Absorb"]["Offset"], 16)))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Absorb"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 4
        #Attack damage
        log[enemy]["AttackDamage"] = []
        for offset in offsets["Enemy"][enemy]["AttackAddress"]:
            Manager.rom.seek(check_offset(int(offset, 16) + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16)))
            damage = int.from_bytes(Manager.rom.read(2), "little")
            if damage > (0x100**dictionary["Properties"]["Enemy"]["Damage"]["Length"]/2) - 1:
                damage -= 0x100**dictionary["Properties"]["Enemy"]["Damage"]["Length"]
            log[enemy]["AttackDamage"].append(damage)
    
    with open("SpoilerLog\\Enemy.json", "w") as file_writer:
        file_writer.write(json.dumps(log, indent=2))