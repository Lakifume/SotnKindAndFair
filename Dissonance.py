import Manager
import json
import random
import math
import os

def init():
    global damage_rate
    damage_rate = 1/1.5
    global attributes
    attributes = {
        "FLA": 0x01,
        "ICE": 0x02,
        "LIG": 0x04,
        "AIR": 0x08
    }
    #Enemy info
    global enemy_offset
    enemy_offset = 0xC7E38
    global minor
    minor = []
    global level_skip
    level_skip = []
    global resist_skip
    resist_skip = []
    global resist_pool
    resist_pool = []
    global final_bosses
    final_bosses = ("Maxim", "Dracula Wraith 1")
    global enemy_to_level
    enemy_to_level = {}
    global special_id_to_enemy
    special_id_to_enemy = {
        0x6E: "Skeleton Mirror",
        0x70: "Slime",
        0x71: "Skeleton Glass"
    }
    global enemy_to_global_sheet
    enemy_to_global_sheet = {
        "Slime":            "Tiny Slime",
        "Gold Medusa":      "Medusa Head",
        "Bone Soldier":     "Skeleton",
        "Clear Bone":       "Skeleton",
        "Fleaman Armor":    "Fleaman",
        "White Dragon Lv2": "White Dragon",
        "White Dragon Lv3": "White Dragon",
        "Poison Lizard":    "Lizard Man",
        "Master Lizard":    "Lizard Man",
        "Skeleton Rib":     "Skeleton Spear",
        "Bone Liquid":      "Red Skeleton",
        "Axe Armor Lv2":    "Axe Armor",
        "Arthro Skeleton":  "Skeleton Spider",
        "Pixie":            "Witch",
        "Sylph":            "Siren",
        "Bomber Armor":     "Rock Armor",
        "Big Balloon":      "Balloon",
        "Ruler Sword Lv2":  "Ruler Sword",
        "Specter":          "Ruler Sword",
        "Ruler Sword Lv3":  "Ruler Sword",
        "Disc Armor Lv2":   "Disc Armor"
    }
    #Boss info
    global boss_to_entity_profile
    boss_to_entity_profile = {
        "Peeping Big": 0xCC0078000016000002000000,
        "Pazuzu":      0x40016000006D000000000000,
        "Talos":       0x80009000026F000000000000
    }
    global boss_to_entity_profile_invert
    boss_to_entity_profile_invert = {}
    global boss_to_door_id
    boss_to_door_id = {
        "Giant Bat":       0x01,
        "Skull Knight":    0x02,
        "Living Armor":    0x03,
        "Golem":           0x04,
        "Minotaur":        0x05,
        "Devil":           0x06,
        "Giant Merman":    0x07,
        "Max Slimer":      0x08,
        "Peeping Big":     0x09,
        "Legion (saint)":  0x0A,
        "Shadow":          0x0B,
        "Minotaur Lv2":    0x0C,
        "Legion (corpse)": 0x0D,
        "Talos":           0x0E,
        #"Death 1":         0x0F, #Probably best to leave this one alone
        "Cyclops":         0x10,
        "Pazuzu":          0x12
    }
    global boss_to_door_id_invert
    boss_to_door_id_invert = {}
    global boss_to_door_offset
    boss_to_door_offset = {
        "Giant Bat":       0x49B188,
        "Living Armor":    0x49D61C,
        "Cyclops":         0x49E6A4,
        "Pazuzu":          0x49F858,
        "Legion (corpse)": 0x4A0E74,
        "Skull Knight":    0x4A1FA8,
        "Giant Merman":    0x4A6270,
        "Devil":           0x4A79C0,
        "Legion (saint)":  0x4A8BD8,
        "Max Slimer":      0x4AA104,
        "Peeping Big":     0x4AB744
    }
    global boss_to_layer_offset
    boss_to_layer_offset = {
        "Living Armor":    0x49D658,
        "Cyclops":         0x49E6E0,
        "Pazuzu":          0x49F15C,
        "Legion (corpse)": 0x4A0EB0,
        "Talos":           0x4A3348,
        "Death 1":         0x4A39B0,
        "Golem":           0x4A4CA0,
        "Giant Merman":    0x4A6184,
        "Devil":           0x4A78F4,
        "Legion (saint)":  0x4A8B10
    }
    #Entity info
    global table_range
    table_range = {
        "Consumable": range(0x4B24A4, 0x4B25F4, 0xC),
        "Weapon":     range(0x4B25F4, 0x4B2660, 0xC),
        "Armor":      range(0x4B2660, 0x4B2C60, 0xC),
        "Subweapon":  range(0xE2308 , 0xE23C8 , 0xC),
        "Spell":      range(0xE29D4 , 0xE2C14 , 0xC),
        "Shop":       range(0x4B15C0, 0x4B1674, 0x4)
    }
    global room_pointer_range
    room_pointer_range = range(0x494668, 0x494D44, 0x4)
    global room_to_entity
    room_to_entity = {}
    global all_entity_pointers
    all_entity_pointers = []
    global room_skip
    room_skip = [
        0x4A138C
    ]
    #Replacement
    global enemy_replacement
    enemy_replacement = {}
    global enemy_replacement_invert
    enemy_replacement_invert = {}
    global boss_replacement
    boss_replacement = {}
    global boss_replacement_invert
    boss_replacement_invert = {}
    global all_replacement
    all_replacement = {}
    global all_replacement_invert
    all_replacement_invert = {}
    #FillResistPool
    for i in range(6):
        resist_pool.append(0)
    for i in range(30):
        resist_pool.append(1)
    for i in range(6):
        resist_pool.append(2)
    #Invert dictionary
    for i in boss_to_door_id:
        boss_to_door_id_invert[boss_to_door_id[i]] = i

def open_json():
    global values
    values = {}
    for i in os.listdir("Data\\Dissonance\\Values"):
        name, extension = os.path.splitext(i)
        with open("Data\\Dissonance\\Values\\" + i, "r") as file_reader:
            values[name] = json.load(file_reader)
    global dictionary
    dictionary = {}
    for i in os.listdir("Data\\Dissonance\\Dicts"):
        name, extension = os.path.splitext(i)
        with open("Data\\Dissonance\\Dicts\\" + i, "r") as file_reader:
            dictionary[name] = json.load(file_reader)

def get_seed():
    #If the rom is randomized reuse its seed
    Manager.rom.seek(0x6A0000)
    seed = int.from_bytes(Manager.rom.read(20), "big")
    if seed == 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
        return random.random()
    else:
        start_with_spirit_orb()
        return seed

def start_with_spirit_orb():
    #Start the player with spirit orb
    Manager.rom.seek(0x499818 + 4)
    Manager.rom.write((0xC307000007000300).to_bytes(8, "big"))
    #Replace the original one by a potion or something
    for i in room_to_entity:
        for e in room_to_entity[i]:
            if is_spirit_orb(e):
                Manager.rom.seek(e + 5)
                Manager.rom.write((3).to_bytes(1, "little"))
                Manager.rom.seek(e + 10)
                Manager.rom.write((0).to_bytes(2, "little"))

def gather_data():
    #Store original enemy levels
    for i in values["Enemy"]:
        enemy_to_level[i] = values["Enemy"][i]["Level"]
    #Collect entities per room
    for i in room_pointer_range:
        #Get room pointer
        Manager.rom.seek(i)
        room_pointer = int.from_bytes(Manager.rom.read(3), "little")
        if room_pointer == 0:
            continue
        create_entity_list(room_pointer)
        #Get event pointer
        Manager.rom.seek(room_pointer + 0x4)
        event_pointer = int.from_bytes(Manager.rom.read(3), "little")
        if event_pointer == 0:
            continue
        create_entity_list(event_pointer)
    #Complete boss entity profile dictionary
    for i in room_to_entity:
        for e in room_to_entity[i]:
            Manager.rom.seek(e + 4)
            type = (int.from_bytes(Manager.rom.read(1), "little") & 0xC0) >> 6
            Manager.rom.seek(e + 5)
            subtype = int.from_bytes(Manager.rom.read(1), "little")
            if type == 0 and Manager.get_enemy_name(subtype) in boss_to_door_id:
                Manager.rom.seek(e)
                boss_to_entity_profile[Manager.get_enemy_name(subtype)] = int.from_bytes(Manager.rom.read(12), "big")
    #Invert dictionary
    for i in boss_to_entity_profile:
        boss_to_entity_profile_invert[boss_to_entity_profile[i]] = i

def create_entity_list(room_pointer):
    if room_pointer in room_to_entity:
        return
    room_to_entity[room_pointer] = []
    Manager.rom.seek(room_pointer + 0x18)
    entity_pointer = int.from_bytes(Manager.rom.read(3), "little")
    if entity_pointer == 0 or entity_pointer in all_entity_pointers:
        return
    all_entity_pointers.append(entity_pointer)
    count = 0
    while True:
        offset = entity_pointer + count*0xC
        Manager.rom.seek(offset)
        if int.from_bytes(Manager.rom.read(4), "little") == 0x7FFF7FFF:
            break
        room_to_entity[room_pointer].append(offset)
        count += 1

def apply_ips_patch(patch):
    #Replicate Lunar IPS' process of applying patches to not have to include it in the download
    with open("Data\\Dissonance\\Patches\\" + patch + ".ips", "r+b") as mod:
        progress = 5
        while progress < os.path.getsize("Data\\Dissonance\\Patches\\" + patch + ".ips") - 3:
            mod.seek(progress)
            offset = int.from_bytes(mod.read(3), "big")
            length = int.from_bytes(mod.read(2), "big")
            if length == 0:
                repeat = int.from_bytes(mod.read(2), "big")
                change = int.from_bytes(mod.read(1), "big")
                Manager.rom.seek(offset)
                for e in range(repeat):
                    Manager.rom.write(change.to_bytes(1, "big"))
                progress += 8
            else:
                change = int.from_bytes(mod.read(length), "big")
                Manager.rom.seek(offset)
                Manager.rom.write(change.to_bytes(length, "big"))
                progress += 5 + length

def remove_enemy_drops():
    for i in values["Enemy"]:
        offset = enemy_offset + 0x24*Manager.get_enemy_id(i)
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Drop1"]["Offset"], 16))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop2"]["Length"], "little"))
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Drop2"]["Offset"], 16))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop2"]["Length"], "little"))

def write_simple_data():
    #Lower overall defense bonuses
    for i in table_range["Armor"]:
        Manager.rom.seek(i + 7)
        defense = int.from_bytes(Manager.rom.read(1), "little")
        defense = round(defense/3)
        Manager.rom.seek(i + 7)
        Manager.rom.write(defense.to_bytes(1, "little"))
    #Adjust weapons
    modifications = {
        0x001C: 0,
        0x001D: 20,
        0x001E: 30,
        0x001F: 10,
        0x0020: 10,
        0x0021: 10,
        0x0022: 10,
        0x0023: 10,
        0x0024: 10
    }
    for i in table_range["Weapon"]:
        Manager.rom.seek(i)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item] & 0xFF
            Manager.rom.seek(i + 6)
            Manager.rom.write(value.to_bytes(1, "little"))
    #Adjust spells
    modifications = {
        0x0807F255: 80,  #fire axe
        0x0807F31D: 30,  #fire knife
        0x0807F3AD: 30,  #fire holy water
        0x080826A5: 50,  #ice bible
        0x08084C35: 80,  #wind bible
        0x08084CB5: 30,  #wind fist
        0x08084CFD: 100, #wind cross
        0x08084D21: 80,  #wind knife
        0x08088ACD: 200, #bolt bible, this one is Alucard Shield spell level of OP
        0x08088C69: 50,  #bolt axe
        0x0808D7A1: 80,  #summon bible
        0x0808D8DD: 80,  #summon knife
        0x0808D9D9: 80   #summon axe
    }
    for i in table_range["Spell"]:
        Manager.rom.seek(i)
        code = int.from_bytes(Manager.rom.read(4), "little")
        if code in modifications:
            value = modifications[code]
            Manager.rom.seek(i + 6)
            Manager.rom.write(value.to_bytes(2, "little"))
    #Adjust consumables
    modifications = {
        0x0000: 20,
        0x0001: 100,
        0x0002: 9999,
        0x0003: 16,
        0x0004: 60
    }
    for i in table_range["Consumable"]:
        Manager.rom.seek(i)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item]
            Manager.rom.seek(i + 6)
            Manager.rom.write(value.to_bytes(2, "little"))
    #Adjust prices
    modifications = {
        0x0003: 200,
        0x0103: 2000,
        0x0203: 20000,
        0x0303: 100,
        0x0403: 1000,
        0x0503: 2000,
        0x0603: 10000,
        0x0703: 300,
        0x0803: 300,
        0x0903: 5000
    }
    for i in table_range["Shop"]:
        Manager.rom.seek(i)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item]
            Manager.rom.seek(i + 2)
            Manager.rom.write(value.to_bytes(2, "little"))
    #Music
    #Manager.rom.seek(0x4950EA)
    #Manager.rom.write((0x1A).to_bytes(2, "little"))
    #Manager.rom.seek(0x495102)
    #Manager.rom.write((0x1A).to_bytes(2, "little"))

def randomize_enemies():
    #Randomize in a dictionary
    enemy_category = {}
    for i in values["Enemy"]:
        enemy_category[values["Enemy"][i]["Category"]] = []
    for i in values["Enemy"]:
        enemy_category[values["Enemy"][i]["Category"]].append(i)
    del enemy_category["None"]
    #Make ground and air categories shared
    enemy_category["Ground"].extend(enemy_category["Air"])
    del enemy_category["Air"]
    enemy_category["GroundBig"].extend(enemy_category["AirBig"])
    del enemy_category["AirBig"]
    #Randomize and check for conflicts
    debug = False
    conflict = True
    while conflict:
        #Shuffle enemies within each category
        for i in enemy_category:
            new_list = list(enemy_category[i])
            random.shuffle(new_list)
            new_dict = dict(zip(enemy_category[i], new_list))
            enemy_replacement.update(new_dict)
        #Invert dictionary
        for i in enemy_replacement:
            enemy_replacement_invert[enemy_replacement[i]] = i
        #Check for conflict
        conflict = False
        for i in room_to_entity:
            entity_types = []
            for e in room_to_entity[i]:
                if is_enemy(e):
                    Manager.rom.seek(e + 5)
                    enemy_id = int.from_bytes(Manager.rom.read(1), "little")
                    enemy_name = Manager.get_enemy_name(enemy_id)
                    if debug:
                        if enemy_id == 0x6A:
                            Manager.rom.seek(e + 10)
                            var_b = int.from_bytes(Manager.rom.read(2), "little")
                            new_enemy_name = Manager.get_enemy_name(var_b)
                        else:
                            new_enemy_name = enemy_name
                    else:
                        if enemy_name in enemy_replacement:
                            new_enemy_name = enemy_replacement[enemy_name]
                        elif enemy_id == 0x6A:
                            Manager.rom.seek(e + 10)
                            var_b = int.from_bytes(Manager.rom.read(2), "little")
                            new_enemy_name = enemy_replacement[Manager.get_enemy_name(var_b)]
                        else:
                            new_enemy_name = enemy_name
                    #Check if enemy shares a sheet with a global enemy
                    if new_enemy_name in enemy_to_global_sheet:
                        new_enemy_name = enemy_to_global_sheet[new_enemy_name]
                    if new_enemy_name != "Unknown":
                        entity_types.append(new_enemy_name)
                else:
                    #Also take in account the other entities in the room, by type
                    Manager.rom.seek(e + 4)
                    type = (int.from_bytes(Manager.rom.read(1), "little") & 0xC0) >> 6
                    Manager.rom.seek(e + 5)
                    subtype = int.from_bytes(Manager.rom.read(1), "little")
                    Manager.rom.seek(e + 8)
                    var_a = int.from_bytes(Manager.rom.read(2), "little")
                    #Small candles, boss doors and pickups don't matter in ram usage
                    if type == 2 and var_a == 0 or type == 1 and subtype == 6 or type == 3:
                        continue
                    if type == 1:
                        entity_types.append((type, subtype))
                    else:
                        entity_types.append((type, var_a))
            #Reroll
            #If a room has more than 1 Gorgon the game will crash
            if entity_types.count("Gorgon") > 1:
                conflict = True
                break
            #If a room uses too many entity gfx they will start to look corrupted
            entity_types = list(dict.fromkeys(entity_types))
            ram_usage = 0
            for e in entity_types:
                try:
                    ram_usage += int(values["Enemy"][e]["RamUsage"], 16)
                except KeyError:
                    if e[0] == 1 and e[1] in [0x1F, 0x2D]:
                        ram_usage += 0x2000
                    elif e[0] == 1 and e[1] == 5:
                        ram_usage += 0x1000
                    else:
                        ram_usage += 0x500
            #Some enemies share half of their gfx with others
            if "Mimic" in entity_types and "O" in entity_types:
                ram_usage -= 0x1000
            if "O" in entity_types and "Rare Ghost" in entity_types:
                ram_usage -= 0x1000
            if "Scarecrow" in entity_types and "Jp Bonepillar" in entity_types:
                ram_usage -= 0x1000
            if "Bone Pillar" in entity_types and "Jp Bonepillar" in entity_types:
                ram_usage -= 0x1000
            #The max ram available for room entities is 0x4000
            if ram_usage > 0x4000:
                if debug:
                    print("0x{:04x}".format(i))
                conflict = True
                break
    #Patch via enemy ids
    for i in room_to_entity:
        if i in room_skip:
            continue
        for e in room_to_entity[i]:
            if is_enemy(e):
                Manager.rom.seek(e + 5)
                enemy_id = int.from_bytes(Manager.rom.read(1), "little")
                enemy_name = Manager.get_enemy_name(enemy_id)
                #Change enemy
                if enemy_name in enemy_replacement and enemy_name != enemy_replacement[enemy_name]:
                    Manager.rom.seek(e + 5)
                    Manager.rom.write(Manager.get_enemy_id(enemy_replacement[enemy_name]).to_bytes(1, "little"))
                    #Adjust position
                    Manager.rom.seek(e)
                    x_pos = int.from_bytes(Manager.rom.read(2), "little")
                    Manager.rom.seek(e + 2)
                    y_pos = int.from_bytes(Manager.rom.read(2), "little")
                    #X
                    #Shift horizontal position for the few enemies that are inside a wall
                    if i in [0x49CEFC, 0x4A5E90]:
                        x_pos += 0x40
                    Manager.rom.seek(e)
                    Manager.rom.write(x_pos.to_bytes(2, "little"))
                    #Y
                    #If bat was replaced lower the position
                    if enemy_name == "Bat":
                        y_pos += random.choice([0x10, 0x20, 0x30])
                    #Raise the enemies in that room with the mermans below the edge
                    if i == 0x4A6CEC:
                        y_pos = 0x78
                    #Raise/lower the enemy if the category is different except for the ball race rooms
                    if not i in [0x4A4880, 0x4AA2E4, 0x4ABC94]:
                        if "Ground" in values["Enemy"][enemy_name]["Category"] and "Air" in values["Enemy"][enemy_replacement[enemy_name]]["Category"]:
                            y_pos -= 0x20
                        elif "Air" in values["Enemy"][enemy_name]["Category"] and "Ground" in values["Enemy"][enemy_replacement[enemy_name]]["Category"]:
                            y_pos += 0x20
                    Manager.rom.seek(e + 2)
                    Manager.rom.write(y_pos.to_bytes(2, "little"))
                    #Set up extra variables
                    if enemy_replacement[enemy_name] == "Bat":
                        var_a = 1
                        var_b = 0
                    elif enemy_replacement[enemy_name] == "Bone Pillar":
                        var_a = 2
                        var_b = 0
                    elif "Slime" in enemy_replacement[enemy_name]:
                        var_a = random.randint(0, 3)
                        var_b = 0
                    elif values["Enemy"][enemy_replacement[enemy_name]]["Category"] != "Spider":
                        var_a = 0
                        var_b = 0
                    Manager.rom.seek(e + 8)
                    Manager.rom.write(var_a.to_bytes(2, "little"))
                    Manager.rom.seek(e + 10)
                    Manager.rom.write(var_b.to_bytes(2, "little"))
                #Change spawner enemy pointer
                elif enemy_id == 0x6A:
                    Manager.rom.seek(e + 10)
                    var_b = int.from_bytes(Manager.rom.read(2), "little")
                    Manager.rom.seek(e + 10)
                    Manager.rom.write(Manager.get_enemy_id(enemy_replacement[Manager.get_enemy_name(var_b)]).to_bytes(2, "little"))
                    #Set up var a
                    if enemy_replacement[Manager.get_enemy_name(var_b)] == "Bat":
                        var_a = 1
                    elif "Slime" in enemy_replacement[Manager.get_enemy_name(var_b)]:
                        var_a = random.randint(0, 3)
                    else:
                        var_a = 0
                    Manager.rom.seek(e + 8)
                    Manager.rom.write(var_a.to_bytes(2, "little"))
    all_replacement.update(enemy_replacement)
    all_replacement_invert.update(enemy_replacement_invert)

def randomize_bosses():
    #Randomize in a dictionary
    new_list = list(boss_to_door_id)
    random.shuffle(new_list)
    new_dict = dict(zip(list(boss_to_door_id), new_list))
    boss_replacement.update(new_dict)
    #Invert dictionary
    for i in boss_replacement:
        boss_replacement_invert[boss_replacement[i]] = i
    #Patch via entity profiles directly
    for i in room_to_entity:
        for e in room_to_entity[i]:
            if is_boss(e):
                Manager.rom.seek(e)
                entity_profile = int.from_bytes(Manager.rom.read(12), "big")
                enemy_name     = boss_to_entity_profile_invert[entity_profile]
                #Change boss
                if enemy_name in boss_replacement and enemy_name != boss_replacement[enemy_name]:
                    Manager.rom.seek(e)
                    original_x_pos = int.from_bytes(Manager.rom.read(2), "little")
                    Manager.rom.seek(e + 4)
                    original_unique_id = int.from_bytes(Manager.rom.read(1), "little")
                    Manager.rom.seek(e)
                    Manager.rom.write(boss_to_entity_profile[boss_replacement[enemy_name]].to_bytes(12, "big"))
                    #If it's Max Slimer randomize its color
                    if "Slime" in boss_replacement[enemy_name]:
                        var_a = random.randint(0, 3)
                        Manager.rom.seek(e + 8)
                        Manager.rom.write(var_a.to_bytes(2, "little"))
                    #Make bosses inherit the x position of the old entity with a shift for Talos' spot
                    if enemy_name == "Talos":
                        original_x_pos += 0x40
                    Manager.rom.seek(e)
                    Manager.rom.write(original_x_pos.to_bytes(2, "little"))
                    #As well as the unique id
                    Manager.rom.seek(e + 4)
                    Manager.rom.write(original_unique_id.to_bytes(1, "little"))
                    #Lasty update the entity profile dict
                    Manager.rom.seek(e)
                    new_entity_profile = int.from_bytes(Manager.rom.read(12), "big")
                    boss_to_entity_profile[boss_replacement[enemy_name]] = new_entity_profile
            #Update boss door pointers
            elif is_boss_door(e):
                Manager.rom.seek(e + 10)
                var_b = int.from_bytes(Manager.rom.read(2), "little")
                if var_b in boss_to_door_id_invert:
                    Manager.rom.seek(e + 10)
                    Manager.rom.write(boss_to_door_id[boss_replacement[boss_to_door_id_invert[var_b]]].to_bytes(2, "little"))
    #Recreate the inverted dict
    boss_to_entity_profile_invert.clear()
    for i in boss_to_entity_profile:
        boss_to_entity_profile_invert[boss_to_entity_profile[i]] = i
    #If Pazuzu was moved make his wall invisible
    if boss_replacement["Pazuzu"] != "Pazuzu":
        apply_ips_patch("InvisiblePazuzuWall")
    #If Talos was moved in a room that can be entered from the right move the door transition to the left so that the player doesn't get stuck behind him
    if boss_replacement_invert["Talos"] in boss_to_door_offset:
        Manager.rom.seek(boss_to_door_offset[boss_replacement_invert["Talos"]] + 8)
        dest_x_pos = int.from_bytes(Manager.rom.read(2), "little")
        dest_x_pos -= 0xF0
        dest_x_pos = dest_x_pos & 0xFFFF
        Manager.rom.seek(boss_to_door_offset[boss_replacement_invert["Talos"]] + 8)
        Manager.rom.write(dest_x_pos.to_bytes(2, "little"))
    #Unless it's on Shadow's spot, then just shift the event placement
    if boss_replacement_invert["Talos"] == "Shadow":
        Manager.rom.seek(0x4A9104)
        Manager.rom.write((0x60).to_bytes(2, "little"))
    #If Max Slimer was moved in a room that has 2 layers it will appear behind the foreground so increase the Z index of that layer
    if boss_replacement_invert["Max Slimer"] in boss_to_layer_offset:
        Manager.rom.seek(boss_to_layer_offset[boss_replacement_invert["Max Slimer"]])
        Manager.rom.write((0x1E).to_bytes(1, "little"))
    all_replacement.update(boss_replacement)
    all_replacement_invert.update(boss_replacement_invert)

def rebalance_enemies():
    #Make an enemy inherit the level of the enemy it was placed over to retain difficulty scale
    for i in values["Enemy"]:
        if i in all_replacement_invert:
            values["Enemy"][i]["Level"] = enemy_to_level[all_replacement_invert[i]]

def update_gfx_pointers():
    #Entities require to have their GFX pointers referenced in the room that they're in
    freespace_offset = 0x69D400
    for i in room_to_entity:
        if i in room_skip:
            continue
        #Get info pointers
        Manager.rom.seek(i + 0x10)
        gfx_list_offset = int.from_bytes(Manager.rom.read(3), "little")
        count = 0
        while True:
            offset = gfx_list_offset + count*0x4
            Manager.rom.seek(offset)
            if int.from_bytes(Manager.rom.read(4), "little") == 0:
                next_list_offset = offset + 0x4
                break
            count += 1
        #Get room's enemy types
        enemy_types = []
        for e in room_to_entity[i]:
            if is_enemy(e):
                Manager.rom.seek(e + 5)
                enemy_id   = int.from_bytes(Manager.rom.read(1), "little")
                enemy_name = Manager.get_enemy_name(enemy_id)
                if enemy_name in all_replacement:
                    enemy_types.append(all_replacement_invert[enemy_name])
                elif enemy_id == 0x6A:
                    Manager.rom.seek(e + 10)
                    var_b = int.from_bytes(Manager.rom.read(2), "little")
                    enemy_types.append(all_replacement_invert[Manager.get_enemy_name(var_b)])
            if is_boss(e):
                Manager.rom.seek(e)
                entity_profile = int.from_bytes(Manager.rom.read(12), "big")
                enemy_name     = boss_to_entity_profile_invert[entity_profile]
                if enemy_name in all_replacement:
                    enemy_types.append(all_replacement_invert[enemy_name])
        enemy_types = list(dict.fromkeys(enemy_types))
        #Get gfx list
        gfx_list = []
        for e in range(gfx_list_offset, next_list_offset, 0x4):
            Manager.rom.seek(e)
            gfx_pointer = int.from_bytes(Manager.rom.read(4), "little")
            gfx_list.append(gfx_pointer)
        original_size = len(gfx_list)
        #Update enemy gfx list
        for e in range(len(enemy_types)-1, -1, -1):
            for o in values["Enemy"][enemy_types[e]]["GfxPointer"]:
                gfx_pointer = int(o, 16)
                if gfx_pointer in gfx_list:
                    gfx_list.remove(gfx_pointer)
            for o in range(len(values["Enemy"][all_replacement[enemy_types[e]]]["GfxPointer"])-1, -1, -1):
                gfx_pointer = int(values["Enemy"][all_replacement[enemy_types[e]]]["GfxPointer"][o], 16)
                if not gfx_pointer in gfx_list:
                    gfx_list.insert(0, gfx_pointer)
        #Patch rom
        if len(gfx_list) <= original_size:
            count = 0
            for e in range(gfx_list_offset, next_list_offset, 0x4):
                Manager.rom.seek(e)
                if count < len(gfx_list):
                    Manager.rom.write(gfx_list[count].to_bytes(4, "little"))
                else:
                    Manager.rom.write((0).to_bytes(4, "little"))
                count += 1
        else:
            for e in range(gfx_list_offset, next_list_offset, 0x4):
                Manager.rom.seek(e)
                Manager.rom.write((0).to_bytes(4, "little"))
            Manager.rom.seek(i + 0x10)
            Manager.rom.write((freespace_offset + 0x08000000).to_bytes(4, "little"))
            for e in range(len(gfx_list)):
                Manager.rom.seek(freespace_offset + e*0x4)
                Manager.rom.write(gfx_list[e].to_bytes(4, "little"))
            freespace_offset += len(gfx_list)*4

def is_enemy(offset):
    Manager.rom.seek(offset + 4)
    type = (int.from_bytes(Manager.rom.read(1), "little") & 0xC0) >> 6
    if type == 0 and not is_boss(offset):
        return True
    else:
        return False

def is_boss(offset):
    Manager.rom.seek(offset)
    entity_profile = int.from_bytes(Manager.rom.read(12), "big")
    if entity_profile in boss_to_entity_profile_invert:
        return True
    else:
        return False

def is_boss_door(offset):
    Manager.rom.seek(offset + 4)
    type = (int.from_bytes(Manager.rom.read(1), "little") & 0xC0) >> 6
    Manager.rom.seek(offset + 5)
    subtype = int.from_bytes(Manager.rom.read(1), "little")
    if type == 1 and subtype == 6:
        return True
    else:
        return False

def is_spirit_orb(offset):
    Manager.rom.seek(e + 4)
    type = (int.from_bytes(Manager.rom.read(1), "little") & 0xC0) >> 6
    Manager.rom.seek(e + 5)
    subtype = int.from_bytes(Manager.rom.read(1), "little")
    Manager.rom.seek(e + 10)
    var_b = int.from_bytes(Manager.rom.read(2), "little")
    if type == 3 and subtype == 7 and var_b == 3:
        return True
    else:
        return False

def write_complex_data():
    #ENEMY
    for i in values["Enemy"]:
        offset = enemy_offset + 0x24*Manager.get_enemy_id(i)
        #Level
        level = values["Enemy"][i]["Level"]
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Level"]["Offset"], 16))
        Manager.rom.write(level.to_bytes(dictionary["Properties"]["Enemy"]["Level"]["Length"], "little"))
        #Health
        max_health = values["Enemy"][i]["MaxHealth"]
        min_health = int(max_health/100)
        health = round(((max_health - min_health)/98)*(level-1) + min_health)
        health = Manager.check_meaningful_value(health)
        if health < 1:
            health = 1
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Health"]["Offset"], 16))
        Manager.rom.write(health.to_bytes(dictionary["Properties"]["Enemy"]["Health"]["Length"], "little"))
        #Damage
        max_damage = values["Enemy"][i]["MaxDamage"]
        min_damage = int(max_damage/30)
        damage = round(((max_damage - min_damage)/98)*(level-1) + min_damage)
        if damage < 1:
            damage = 1
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
        Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
        #Defense
        max_defense = values["Enemy"][i]["MaxDefense"]
        min_defense = int(max_defense/10)
        defense = round(((max_defense - min_defense)/98)*(level-1) + min_defense)
        if defense > 255:
            defense = 255
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Defense"]["Offset"], 16))
        Manager.rom.write(defense.to_bytes(dictionary["Properties"]["Enemy"]["Defense"]["Length"], "little"))
        #Experience
        max_experience = values["Enemy"][i]["MaxExperience"]
        min_experience = int(max_experience/100)
        experience = round(((max_experience - min_experience)/98)*(level-1) + min_experience)
        experience = Manager.check_meaningful_value(experience)
        if experience < 1:
            experience = 1
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Experience"]["Offset"], 16))
        Manager.rom.write(experience.to_bytes(dictionary["Properties"]["Enemy"]["Experience"]["Length"], "little"))
        #Damage type
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["DamageType"]["Offset"], 16))
        Manager.rom.write(int(values["Enemy"][i]["DamageType"], 16).to_bytes(dictionary["Properties"]["Enemy"]["DamageType"]["Length"], "little"))
        #Resistances
        weak = 0
        resist = 0
        for e in attributes:
            if values["Enemy"][i]["Resistances"][e] == 0:
                weak += attributes[e]
            elif values["Enemy"][i]["Resistances"][e] == 2:
                resist += attributes[e]
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Weak"]["Offset"], 16))
        Manager.rom.write(weak.to_bytes(dictionary["Properties"]["Enemy"]["Weak"]["Length"], "little"))
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Resist"]["Offset"], 16))
        Manager.rom.write(resist.to_bytes(dictionary["Properties"]["Enemy"]["Resist"]["Length"], "little"))
        #Attack
        for e in range(len(values["Enemy"][i]["AttackCorrection"])):
            attack_id = "Attack" + str(e + 1)
            #Attack correction
            attack = round(damage*values["Enemy"][i]["AttackCorrection"][e]**damage_rate)
            if attack < 1:
                attack = 1
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            Manager.rom.write(attack.to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))
            #Attack type
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id + "Type"]["Offset"], 16))
            Manager.rom.write(int(values["Enemy"][i]["AttackType"][e], 16).to_bytes(dictionary["Properties"]["Enemy"][attack_id + "Type"]["Length"], "little"))
        #Debug
        for e in range(3 - len(values["Enemy"][i]["AttackCorrection"])):
            attack_id = "Attack" + str(len(values["Enemy"][i]["AttackCorrection"]) + e + 1)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            Manager.rom.write((damage).to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))
    #Match chase Talos' damage with regular Talos
    Manager.rom.seek(enemy_offset + 0x24*Manager.get_enemy_id("Talos") + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
    damage = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Damage"]["Length"]), "little")
    Manager.rom.seek(enemy_offset + 0x24*0x77 + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
    Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
    #Fix the Bone Thrower's bone damage actually being in the bat entry
    for i in range(3):
        attack_id = "Attack" + str(i + 1)
        Manager.rom.seek(enemy_offset + 0x24*Manager.get_enemy_id("Bone Thrower") + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
        damage = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][attack_id]["Length"]), "little")
        Manager.rom.seek(enemy_offset + 0x24*Manager.get_enemy_id("Bat") + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
        Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))

def create_enemy_log():
    log = {}
    for i in values["Enemy"]:
        offset = enemy_offset + 0x24*Manager.get_enemy_id(i)
        log[i] = {}
        #Stats
        for e in ["Level", "Health", "Damage", "Defense", "Experience"]:
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][e]["Offset"], 16))
            log[i][e] = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][e]["Length"]), "little")
        #Resistances
        log[i]["Resistances"] = {}
        for e in attributes:
            log[i]["Resistances"][e] = 1
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Weak"]["Offset"], 16))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Weak"]["Length"]), "little")
        for e in attributes:
            if (total & attributes[e]) != 0:
                log[i]["Resistances"][e] = 0
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Resist"]["Offset"], 16))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Resist"]["Length"]), "little")
        for e in attributes:
            if (total & attributes[e]) != 0:
                log[i]["Resistances"][e] = 2
        #Attack damage
        log[i]["AttackDamage"] = []
        for e in range(len(values["Enemy"][i]["AttackCorrection"])):
            attack_id = "Attack" + str(e + 1)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            log[i]["AttackDamage"].append(int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][attack_id]["Length"]), "little"))
        if i in all_replacement and all_replacement[i] != i:
            log[i]["Position"] = all_replacement_invert[i]
        else:
            log[i]["Position"] = "Unchanged"
    
    with open("SpoilerLog\\Enemy.json", "w") as file_writer:
        file_writer.write(json.dumps(log, indent=2))