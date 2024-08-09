import Manager
import json
import random
import math
import os
import copy

class Room:
    def __init__(self, entities, gfx_list):
        self.entities = entities
        self.gfx_list = gfx_list
        self.gfx_list_size = len(gfx_list)

class Entity:
    def __init__(self, x_pos, y_pos, unique_id, type, subtype, offset_up, byte_8, var_a, var_b):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.unique_id = unique_id
        self.type = type
        self.subtype = subtype
        self.offset_up = offset_up
        self.byte_8 = byte_8
        self.var_a = var_a
        self.var_b = var_b

def init():
    global damage_rate
    damage_rate = math.log(2.25, 3)
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
    global juste_enemy_offset
    juste_enemy_offset = 0
    global maxim_enemy_offset
    maxim_enemy_offset = 0x7D
    global level_skip
    level_skip = []
    global resist_skip
    resist_skip = []
    global resist_range
    resist_range = (0, 2)
    global final_bosses
    final_bosses = ("Maxim", "Dracula Wraith 1")
    global enemy_to_level
    enemy_to_level = {}
    global special_id_to_enemy
    special_id_to_enemy = {
        0x6D: "Pazuzu",
        0x6E: "Skeleton Mirror",
        0x6F: "Talos",
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
    global boss_to_pointer
    boss_to_pointer = {}
    global boss_to_pointer_invert
    boss_to_pointer_invert = {}
    global boss_to_entity
    boss_to_entity = {}
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
    boss_to_door_id_invert = {value: key for key, value in boss_to_door_id.items()}
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
    global game_rooms
    game_rooms = {}
    global room_skip
    room_skip = [0x4A138C]
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

def open_json():
    global values
    values = {}
    for file in os.listdir("Data\\Dissonance\\Values"):
        file_name = os.path.splitext(file)[0]
        with open(f"Data\\Dissonance\\Values\\{file}", "r") as file_reader:
            values[file_name] = json.load(file_reader)
    global dictionary
    dictionary = {}
    for file in os.listdir("Data\\Dissonance\\Dicts"):
        file_name = os.path.splitext(file)[0]
        with open(f"Data\\Dissonance\\Dicts\\{file}", "r") as file_reader:
            dictionary[file_name] = json.load(file_reader)

def get_seed():
    #If the rom is randomized reuse its seed
    Manager.rom.seek(0x69F1E4)
    seed = int.from_bytes(Manager.rom.read(20), "big")
    if seed == 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
        return random.random()
    return seed

def read_room_data():
    for offset in room_pointer_range:
        #Get room pointer
        Manager.rom.seek(offset)
        room_pointer = int.from_bytes(Manager.rom.read(3), "little")
        if room_pointer == 0:
            continue
        game_rooms[room_pointer] = Room(create_entity_dict(room_pointer), create_gfx_list(room_pointer))
        #Get event pointer
        Manager.rom.seek(room_pointer + 0x4)
        event_pointer = int.from_bytes(Manager.rom.read(3), "little")
        if event_pointer == 0:
            continue
        game_rooms[event_pointer] = Room(create_entity_dict(event_pointer), create_gfx_list(event_pointer))

def create_entity_dict(room_pointer):
    Manager.rom.seek(room_pointer + 0x18)
    entity_list_pointer = int.from_bytes(Manager.rom.read(3), "little")
    if entity_list_pointer == 0:
        return {}
    entity_dict = {}
    count = 0
    while True:
        entity_pointer = entity_list_pointer + count*0xC
        Manager.rom.seek(entity_pointer)
        if int.from_bytes(Manager.rom.read(4), "little") == 0x7FFF7FFF:
            break
        Manager.rom.seek(entity_pointer)
        x_pos     = int.from_bytes(Manager.rom.read(2), "little")
        y_pos     = int.from_bytes(Manager.rom.read(2), "little")
        byte_5    = int.from_bytes(Manager.rom.read(1), "little")
        unique_id = (byte_5 & 0x3F)
        type      = (byte_5 & 0xC0) >> 6
        subtype   = int.from_bytes(Manager.rom.read(1), "little")
        offset_up = int.from_bytes(Manager.rom.read(1), "little")
        byte_8    = int.from_bytes(Manager.rom.read(1), "little")
        var_a     = int.from_bytes(Manager.rom.read(2), "little")
        var_b     = int.from_bytes(Manager.rom.read(2), "little")
        entity_dict[entity_pointer] = Entity(x_pos, y_pos, unique_id, type, subtype, offset_up, byte_8, var_a, var_b)
        count += 1
    return entity_dict

def create_gfx_list(room_pointer):
    Manager.rom.seek(room_pointer + 0x10)
    gfx_list_pointer = int.from_bytes(Manager.rom.read(3), "little")
    if gfx_list_pointer == 0:
        return []
    gfx_list = []
    count = 0
    while True:
        gfx_pointer = gfx_list_pointer + count*0x4
        Manager.rom.seek(gfx_pointer)
        gfx_list.append(int.from_bytes(Manager.rom.read(4), "little"))
        Manager.rom.seek(gfx_pointer)
        if int.from_bytes(Manager.rom.read(4), "little") == 0:
            break
        count += 1
    return gfx_list

def write_room_data():
    #Get a freespace offset that won't conflict with any other hack
    freespace_offset = None
    for offset in range(0x69D400, 0x800000, 0x100):
        Manager.rom.seek(offset)
        if int.from_bytes(Manager.rom.read(0x200), "big") == 0x100**0x200 - 1:
            freespace_offset = offset
            break
    if not freespace_offset:
        raise Exception("Could not find free space in the rom")
    for room_offset in game_rooms:
        #Write entity data
        for entity_offset in game_rooms[room_offset].entities:
            Manager.rom.seek(entity_offset)
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].x_pos.to_bytes(2, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].y_pos.to_bytes(2, "little"))
            byte_5 = (game_rooms[room_offset].entities[entity_offset].unique_id & 0x3F) | ((game_rooms[room_offset].entities[entity_offset].type & 0x3) << 6)
            Manager.rom.write(byte_5.to_bytes(1, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].subtype.to_bytes(1, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].offset_up.to_bytes(1, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].byte_8.to_bytes(1, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].var_a.to_bytes(2, "little"))
            Manager.rom.write(game_rooms[room_offset].entities[entity_offset].var_b.to_bytes(2, "little"))
        #Write gfx list
        Manager.rom.seek(room_offset + 0x10)
        gfx_list_pointer = int.from_bytes(Manager.rom.read(3), "little")
        if len(game_rooms[room_offset].gfx_list) <= game_rooms[room_offset].gfx_list_size:
            for index in range(game_rooms[room_offset].gfx_list_size):
                Manager.rom.seek(gfx_list_pointer + index*0x4)
                if index < len(game_rooms[room_offset].gfx_list):
                    Manager.rom.write(game_rooms[room_offset].gfx_list[index].to_bytes(4, "little"))
                else:
                    Manager.rom.write((0).to_bytes(4, "little"))
        else:
            for index in range(game_rooms[room_offset].gfx_list_size):
                Manager.rom.seek(gfx_list_pointer + index*0x4)
                Manager.rom.write((0).to_bytes(4, "little"))
            Manager.rom.seek(room_offset + 0x10)
            Manager.rom.write((freespace_offset + 0x08000000).to_bytes(4, "little"))
            for index in range(len(game_rooms[room_offset].gfx_list)):
                Manager.rom.seek(freespace_offset + index*0x4)
                Manager.rom.write(game_rooms[room_offset].gfx_list[index].to_bytes(4, "little"))
            freespace_offset += len(game_rooms[room_offset].gfx_list)*4

def gather_data():
    #Store original enemy levels
    for enemy in values["Enemy"]:
        enemy_to_level[enemy] = values["Enemy"][enemy]["Level"]
    #Gather bosses
    for room_offset in game_rooms:
        is_boss_room = False
        for entity_offset in game_rooms[room_offset].entities:
            if game_rooms[room_offset].entities[entity_offset].type == 1 and game_rooms[room_offset].entities[entity_offset].subtype == 6 and game_rooms[room_offset].entities[entity_offset].var_a == 1 and game_rooms[room_offset].entities[entity_offset].var_b in boss_to_door_id_invert:
                is_boss_room = True
                break
        if is_boss_room:
            for entity_offset in game_rooms[room_offset].entities:
                if game_rooms[room_offset].entities[entity_offset].type == 0:
                    if game_rooms[room_offset].entities[entity_offset].subtype == 0x16 and game_rooms[room_offset].entities[entity_offset].var_a == 2:
                        enemy_name = "Peeping Big"
                    else:
                        enemy_name = Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].subtype)
                    boss_to_pointer[enemy_name] = entity_offset
                    boss_to_entity[enemy_name]  = copy.deepcopy(game_rooms[room_offset].entities[entity_offset])
    boss_to_pointer_invert.update({value: key for key, value in boss_to_pointer.items()})

def apply_ips_patch(patch):
    #Replicate Lunar IPS' process of applying patches to not have to include it in the download
    with open(f"Data\\Dissonance\\Patches\\{patch}.ips", "r+b") as mod:
        progress = 5
        while progress < os.path.getsize(f"Data\\Dissonance\\Patches\\{patch}.ips") - 3:
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

def all_bigtoss():
    #Multiply every character's damage velocities
    ground_x_vel = 5
    ground_x_dec = 0.5
    crouch_x_vel = 5
    crouch_x_dec = 0.5
    air_x_vel    = 5
    air_Y_vel    = 2
    for offset in [0xE1C34, 0xE1CE0, 0xE1D8C]:
        shift = 0
        for e in [ground_x_vel, ground_x_dec, crouch_x_vel, crouch_x_dec, air_x_vel, air_Y_vel]:
            Manager.rom.seek(offset + shift)
            value = int.from_bytes(Manager.rom.read(4), "little")
            if value > 0x7FFFFFFF:
                value -= 0x100000000
            value = int(value*e) & 0xFFFFFFFF
            Manager.rom.seek(offset + shift)
            Manager.rom.write(value.to_bytes(4, "little"))
            shift += 4

def remove_enemy_drops():
    for enemy in values["Enemy"]:
        offset = enemy_offset + 0x24*Manager.get_enemy_id(enemy)
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Drop1"]["Offset"], 16))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop2"]["Length"], "little"))
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Drop2"]["Offset"], 16))
        Manager.rom.write((0).to_bytes(dictionary["Properties"]["Enemy"]["Drop2"]["Length"], "little"))

def write_simple_data():
    #Lower overall defense bonuses
    for offset in table_range["Armor"]:
        Manager.rom.seek(offset + 7)
        defense = int.from_bytes(Manager.rom.read(1), "little")
        defense = round(defense/3)
        Manager.rom.seek(offset + 7)
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
    for offset in table_range["Weapon"]:
        Manager.rom.seek(offset)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item] & 0xFF
            Manager.rom.seek(offset + 6)
            Manager.rom.write(value.to_bytes(1, "little"))
    #Adjust spells
    modifications = {
        0x0807F255: 80,  #fire axe
        0x0807F31D: 50,  #fire knife
        0x0807F389: 60,  #fire fist
        0x0807F3AD: 40,  #fire holy water
        0x080826A5: 50,  #ice bible
        0x08084C35: 80,  #wind bible
        0x08084CB5: 40,  #wind fist
        0x08084CFD: 100, #wind cross
        0x08084D21: 30,  #wind knife
        0x08088ACD: 200, #bolt bible, this one is Alucard Shield spell level of OP
        0x08088BB1: 80,  #bolt cross
        0x08088C69: 50,  #bolt axe
        0x08088C99: 40,  #bolt fist
        0x0808D7A1: 80,  #summon bible
        0x0808D859: 120, #summon holy water
        0x0808D8DD: 80,  #summon knife
        0x0808D9D9: 80   #summon axe
    }
    for offset in table_range["Spell"]:
        Manager.rom.seek(offset)
        code = int.from_bytes(Manager.rom.read(4), "little")
        if code in modifications:
            value = modifications[code]
            Manager.rom.seek(offset + 6)
            Manager.rom.write(value.to_bytes(2, "little"))
    #Adjust consumables
    modifications = {
        0x0000: 20,
        0x0001: 100,
        0x0002: 9999,
        0x0003: 12,
        0x0004: 60,
        0x0005: 200,
        0x0006: 400
    }
    for offset in table_range["Consumable"]:
        Manager.rom.seek(offset)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item]
            Manager.rom.seek(offset + 6)
            Manager.rom.write(value.to_bytes(2, "little"))
    #Adjust prices
    modifications = {
        0x0003: 200,
        0x0103: 1000,
        0x0203: 5000,
        0x0303: 100,
        0x0403: 500,
        0x0503: 2000,
        0x0603: 4000,
        0x0703: 300,
        0x0803: 300,
        0x0903: 1000
    }
    for offset in table_range["Shop"]:
        Manager.rom.seek(offset)
        item = int.from_bytes(Manager.rom.read(2), "little")
        if item in modifications:
            value = modifications[item]
            Manager.rom.seek(offset + 2)
            Manager.rom.write(value.to_bytes(2, "little"))

def randomize_enemies():
    #Randomize in a dictionary
    enemy_category = {}
    for enemy in values["Enemy"]:
        enemy_category[values["Enemy"][enemy]["Category"]] = []
    for enemy in values["Enemy"]:
        enemy_category[values["Enemy"][enemy]["Category"]].append(enemy)
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
        for category in enemy_category:
            new_list = copy.deepcopy(enemy_category[category])
            random.shuffle(new_list)
            new_dict = dict(zip(enemy_category[category], new_list))
            enemy_replacement.update(new_dict)
        enemy_replacement_invert.update({value: key for key, value in enemy_replacement.items()})
        #Check for conflict
        conflict = False
        #If the regular fleaman is too much stronger than the armor then reroll
        if values["Enemy"][enemy_replacement_invert["Fleaman"]]["Level"] > values["Enemy"][enemy_replacement_invert["Fleaman Armor"]]["Level"] + 10:
            conflict = True
            continue
        #Loop through rooms
        for room_offset in game_rooms:
            entity_types = []
            for entity_offset in game_rooms[room_offset].entities:
                if game_rooms[room_offset].entities[entity_offset].type == 0:
                    enemy_name = Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].subtype)
                    if debug:
                        if game_rooms[room_offset].entities[entity_offset].subtype == 0x6A:
                            new_enemy_name = Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b)
                        else:
                            new_enemy_name = enemy_name
                    else:
                        if enemy_name in enemy_replacement:
                            new_enemy_name = enemy_replacement[enemy_name]
                        elif game_rooms[room_offset].entities[entity_offset].subtype == 0x6A:
                            new_enemy_name = enemy_replacement[Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b)]
                        else:
                            new_enemy_name = enemy_name
                    #Check if enemy shares a sheet with a global enemy
                    if new_enemy_name in enemy_to_global_sheet:
                        new_enemy_name = enemy_to_global_sheet[new_enemy_name]
                    if new_enemy_name:
                        entity_types.append(new_enemy_name)
                else:
                    #Small candles, boss doors and pickups don't matter in ram usage
                    if game_rooms[room_offset].entities[entity_offset].type == 2 and game_rooms[room_offset].entities[entity_offset].var_a == 0 or game_rooms[room_offset].entities[entity_offset].type == 1 and game_rooms[room_offset].entities[entity_offset].subtype == 6 or game_rooms[room_offset].entities[entity_offset].type == 3:
                        continue
                    if game_rooms[room_offset].entities[entity_offset].type == 1:
                        entity_types.append((game_rooms[room_offset].entities[entity_offset].type, game_rooms[room_offset].entities[entity_offset].subtype))
                    else:
                        entity_types.append((game_rooms[room_offset].entities[entity_offset].type, game_rooms[room_offset].entities[entity_offset].var_a))
            #Reroll
            #If a room has more than 1 Gorgon the game will crash
            if entity_types.count("Gorgon") > 1:
                conflict = True
                break
            #If a room uses too many entity gfx they will start to look corrupted
            entity_types = list(dict.fromkeys(entity_types))
            ram_usage = 0
            for entity_offset in entity_types:
                try:
                    ram_usage += int(values["Enemy"][entity_offset]["RamUsage"], 16)
                except KeyError:
                    if entity_offset[0] == 1 and entity_offset[1] in [0x1F, 0x2D]:
                        ram_usage += 0x2000
                    elif entity_offset[0] == 1 and entity_offset[1] == 5:
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
                    print("0x{:04x}".format(room_offset))
                conflict = True
                break
    #Patch via enemy ids
    for room_offset in game_rooms:
        if room_offset in room_skip:
            continue
        #Randomize slime colors per room
        slime_color = random.randint(0, 3)
        for entity_offset in game_rooms[room_offset].entities:
            if entity_offset in boss_to_pointer_invert:
                continue
            if game_rooms[room_offset].entities[entity_offset].type == 0:
                enemy_id = game_rooms[room_offset].entities[entity_offset].subtype
                enemy_name = Manager.get_enemy_name(enemy_id)
                #Change enemy
                if enemy_name in enemy_replacement and enemy_name != enemy_replacement[enemy_name]:
                    game_rooms[room_offset].entities[entity_offset].subtype = Manager.get_enemy_id(enemy_replacement[enemy_name])
                    #Adjust position
                    #X
                    #Shift horizontal position for the large ghost inside a wall
                    if entity_offset == 0x49D8D0:
                        game_rooms[room_offset].entities[entity_offset].x_pos += 0x40
                    #Y
                    #If bat was replaced lower the position
                    if enemy_name == "Bat":
                        game_rooms[room_offset].entities[entity_offset].y_pos += random.choice([0x10, 0x20, 0x30])
                    #Adjust height of the slimes that are too high in cavern b/the mermans that are below the edge in aqueduct b
                    if room_offset in [0x4A4B94, 0x4A5E90, 0x4A6CEC]:
                        game_rooms[room_offset].entities[entity_offset].y_pos = 0x78
                    #Raise/lower the enemy if the category is different except for a few exceptions
                    if not room_offset in [0x4AA2E4, 0x4ABC94] and not entity_offset in [0x4A55D4, 0x4A55EC, 0x4A59F4, 0x4A5A0C, 0x4A5A24, 0x4A70D4]:
                        if "Ground" in values["Enemy"][enemy_name]["Category"] and "Air" in values["Enemy"][enemy_replacement[enemy_name]]["Category"]:
                            game_rooms[room_offset].entities[entity_offset].y_pos -= 0x20
                        if "Air" in values["Enemy"][enemy_name]["Category"] and "Ground" in values["Enemy"][enemy_replacement[enemy_name]]["Category"]:
                            game_rooms[room_offset].entities[entity_offset].y_pos += 0x20
                    #Set up extra variables
                    if enemy_replacement[enemy_name] == "Bat":
                        game_rooms[room_offset].entities[entity_offset].var_a = 1
                        game_rooms[room_offset].entities[entity_offset].var_b = 0
                    elif enemy_replacement[enemy_name] == "Bone Pillar":
                        game_rooms[room_offset].entities[entity_offset].var_a = random.randint(1, 3)
                        game_rooms[room_offset].entities[entity_offset].var_b = 0
                    elif "Slime" in enemy_replacement[enemy_name]:
                        game_rooms[room_offset].entities[entity_offset].var_a = slime_color
                        game_rooms[room_offset].entities[entity_offset].var_b = 0
                    elif values["Enemy"][enemy_replacement[enemy_name]]["Category"] != "Spider":
                        game_rooms[room_offset].entities[entity_offset].var_a = 0
                        game_rooms[room_offset].entities[entity_offset].var_b = 0
                #Change spawner enemy pointer
                elif enemy_id == 0x6A:
                    game_rooms[room_offset].entities[entity_offset].var_b = Manager.get_enemy_id(enemy_replacement[Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b)])
                    #Set up var a
                    if Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b) == "Bat":
                        game_rooms[room_offset].entities[entity_offset].var_a = 1
                    elif "Slime" in Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b):
                        game_rooms[room_offset].entities[entity_offset].var_a = slime_color
                    else:
                        game_rooms[room_offset].entities[entity_offset].var_a = 0
    all_replacement.update(enemy_replacement)
    all_replacement_invert.update(enemy_replacement_invert)

def randomize_bosses():
    #Randomize in a dictionary
    new_list = list(boss_to_door_id)
    random.shuffle(new_list)
    new_dict = dict(zip(list(boss_to_door_id), new_list))
    boss_replacement.update(new_dict)
    boss_replacement_invert.update({value: key for key, value in boss_replacement.items()})
    #Patch via entity profiles directly
    for room_offset in game_rooms:
        for entity_offset in game_rooms[room_offset].entities:
            if entity_offset in boss_to_pointer_invert:
                enemy_name = boss_to_pointer_invert[entity_offset]
                #Change boss
                if enemy_name in boss_replacement and enemy_name != boss_replacement[enemy_name]:
                    original_x_pos = game_rooms[room_offset].entities[entity_offset].x_pos
                    original_unique_id = game_rooms[room_offset].entities[entity_offset].unique_id
                    game_rooms[room_offset].entities[entity_offset] = boss_to_entity[boss_replacement[enemy_name]]
                    #If it's Max Slimer randomize its color
                    if "Slime" in boss_replacement[enemy_name]:
                        game_rooms[room_offset].entities[entity_offset].var_a = random.randint(0, 3)
                    #Make bosses inherit the x position of the old entity with a shift for Talos' spot
                    game_rooms[room_offset].entities[entity_offset].x_pos = original_x_pos
                    if enemy_name == "Talos":
                        game_rooms[room_offset].entities[entity_offset].x_pos += 0x40
                    #As well as the unique id
                    game_rooms[room_offset].entities[entity_offset].unique_id = original_unique_id
            #Update boss door pointers
            elif game_rooms[room_offset].entities[entity_offset].type == 1 and game_rooms[room_offset].entities[entity_offset].subtype == 6 and game_rooms[room_offset].entities[entity_offset].var_b in boss_to_door_id_invert:
                game_rooms[room_offset].entities[entity_offset].var_b = boss_to_door_id[boss_replacement[boss_to_door_id_invert[game_rooms[room_offset].entities[entity_offset].var_b]]]
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
    for enemy in values["Enemy"]:
        if enemy in all_replacement_invert:
            values["Enemy"][enemy]["Level"] = enemy_to_level[all_replacement_invert[enemy]]

def update_gfx_pointers():
    #Entities require to have their GFX pointers referenced in the room that they're in
    for room_offset in game_rooms:
        if room_offset in room_skip:
            continue
        ram_to_enemy = {
            0x500:  [],
            0x1000: [],
            0x1500: [],
            0x2000: []
        }
        changed = False
        #Get room's enemy types
        enemy_types = []
        for entity_offset in game_rooms[room_offset].entities:
            if entity_offset in boss_to_pointer_invert:
                enemy_name = boss_to_pointer_invert[entity_offset]
                if enemy_name in all_replacement:
                    enemy_types.append(enemy_name)
                    changed = True
            elif game_rooms[room_offset].entities[entity_offset].type == 0:
                enemy_id = game_rooms[room_offset].entities[entity_offset].subtype
                enemy_name = Manager.get_enemy_name(enemy_id)
                if enemy_name in all_replacement:
                    enemy_types.append(all_replacement_invert[enemy_name])
                    changed = True
                elif enemy_id == 0x6A:
                    enemy_types.append(all_replacement_invert[Manager.get_enemy_name(game_rooms[room_offset].entities[entity_offset].var_b)])
                    changed = True
                elif enemy_name:
                    enemy_types.append(enemy_name)
        if not changed:
            continue
        enemy_types = list(dict.fromkeys(enemy_types))
        #Remove original enemy gfx
        for enemy in enemy_types:
            for gfx in values["Enemy"][enemy]["GfxPointer"]:
                gfx_pointer = int(gfx, 16)
                if gfx_pointer in game_rooms[room_offset].gfx_list:
                    game_rooms[room_offset].gfx_list.remove(gfx_pointer)
        #Order enemy list by ram
        for enemy in enemy_types:
            new_enemy = all_replacement[enemy] if enemy in all_replacement else enemy
            ram_to_enemy[int(values["Enemy"][new_enemy]["RamUsage"], 16)].append(new_enemy)
        #Add new enemy gfx
        for ram in ram_to_enemy:
            for enemy_index in range(len(ram_to_enemy[ram])-1, -1, -1):
                for gfx_index in range(len(values["Enemy"][ram_to_enemy[ram][enemy_index]]["GfxPointer"])-1, -1, -1):
                    gfx_pointer = int(values["Enemy"][ram_to_enemy[ram][enemy_index]]["GfxPointer"][gfx_index], 16)
                    if not gfx_pointer in game_rooms[room_offset].gfx_list:
                        game_rooms[room_offset].gfx_list.insert(0, gfx_pointer)

def write_complex_data():
    #ENEMY
    #For Juste Mode and Maxim Mode
    for char_offset in [juste_enemy_offset, maxim_enemy_offset]:
        for enemy in values["Enemy"]:
            offset = enemy_offset + 0x24*(Manager.get_enemy_id(enemy) + char_offset)
            #Level
            level = values["Enemy"][enemy]["Level"]
            #For Maxim mode tighten the overall level range
            if char_offset == maxim_enemy_offset:
                average_level = 40
                start_level = average_level/2
                level = round(start_level + (level/average_level)*(average_level - start_level))
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Level"]["Offset"], 16))
            Manager.rom.write(level.to_bytes(dictionary["Properties"]["Enemy"]["Level"]["Length"], "little"))
            #Health
            max_health = values["Enemy"][enemy]["MaxHealth"]
            min_health = int(max_health/100)
            health = Manager.calculate_stat_with_level(min_health, max_health, level)
            health = Manager.check_meaningful_value(health)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Health"]["Offset"], 16))
            Manager.rom.write(health.to_bytes(dictionary["Properties"]["Enemy"]["Health"]["Length"], "little"))
            #Damage
            max_damage = values["Enemy"][enemy]["MaxDamage"]
            min_damage = int(max_damage/30)
            damage = Manager.calculate_stat_with_level(min_damage, max_damage, level)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
            Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
            #Defense
            max_defense = values["Enemy"][enemy]["MaxDefense"]
            min_defense = int(max_defense/10)
            defense = Manager.calculate_stat_with_level(min_defense, max_defense, level)
            defense = min(defense, 255)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Defense"]["Offset"], 16))
            Manager.rom.write(defense.to_bytes(dictionary["Properties"]["Enemy"]["Defense"]["Length"], "little"))
            #Experience
            max_experience = values["Enemy"][enemy]["MaxExperience"]
            min_experience = int(max_experience/100)
            experience = Manager.calculate_stat_with_level(min_experience, max_experience, level)
            experience = Manager.check_meaningful_value(experience)
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Experience"]["Offset"], 16))
            Manager.rom.write(experience.to_bytes(dictionary["Properties"]["Enemy"]["Experience"]["Length"], "little"))
            #Damage type
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["DamageType"]["Offset"], 16))
            Manager.rom.write(int(values["Enemy"][enemy]["DamageType"], 16).to_bytes(dictionary["Properties"]["Enemy"]["DamageType"]["Length"], "little"))
            #Resistances
            weak = 0
            resist = 0
            for attr in attributes:
                if values["Enemy"][enemy]["Resistances"][attr] == 0:
                    weak += attributes[attr]
                elif values["Enemy"][enemy]["Resistances"][attr] == 2:
                    resist += attributes[attr]
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Weak"]["Offset"], 16))
            Manager.rom.write(weak.to_bytes(dictionary["Properties"]["Enemy"]["Weak"]["Length"], "little"))
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Resist"]["Offset"], 16))
            Manager.rom.write(resist.to_bytes(dictionary["Properties"]["Enemy"]["Resist"]["Length"], "little"))
            #Attack
            for index in range(len(values["Enemy"][enemy]["AttackCorrection"])):
                attack_id = f"Attack{index + 1}"
                #Attack correction
                attack = round(damage*values["Enemy"][enemy]["AttackCorrection"][index]**damage_rate)
                Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
                Manager.rom.write(attack.to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))
                #Attack type
                Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][f"{attack_id}Type"]["Offset"], 16))
                Manager.rom.write(int(values["Enemy"][enemy]["AttackType"][index], 16).to_bytes(dictionary["Properties"]["Enemy"][f"{attack_id}Type"]["Length"], "little"))
            #Debug
            for index in range(3 - len(values["Enemy"][enemy]["AttackCorrection"])):
                attack_id = "Attack" + str(len(values["Enemy"][enemy]["AttackCorrection"]) + index + 1)
                Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
                Manager.rom.write((damage + 1).to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))
        #Match chase Talos' damage with regular Talos
        Manager.rom.seek(enemy_offset + 0x24*(Manager.get_enemy_id("Talos") + char_offset) + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
        damage = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Damage"]["Length"]), "little")
        Manager.rom.seek(enemy_offset + 0x24*(0x77 + char_offset) + int(dictionary["Properties"]["Enemy"]["Damage"]["Offset"], 16))
        Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"]["Damage"]["Length"], "little"))
        #Fix the Bone Thrower's bone damage actually being in the bat entry
        for index in range(3):
            attack_id = f"Attack{index + 1}"
            Manager.rom.seek(enemy_offset + 0x24*(Manager.get_enemy_id("Bone Thrower") + char_offset) + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            damage = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][attack_id]["Length"]), "little")
            Manager.rom.seek(enemy_offset + 0x24*(Manager.get_enemy_id("Bat") + char_offset) + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            Manager.rom.write(damage.to_bytes(dictionary["Properties"]["Enemy"][attack_id]["Length"], "little"))

def create_enemy_log():
    log = {}
    for enemy in values["Enemy"]:
        offset = enemy_offset + 0x24*Manager.get_enemy_id(enemy)
        log[enemy] = {}
        #Stats
        for stat in ["Level", "Health", "Damage", "Defense", "Experience"]:
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][stat]["Offset"], 16))
            log[enemy][stat] = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][stat]["Length"]), "little")
        #Resistances
        log[enemy]["Resistances"] = {}
        for attr in attributes:
            log[enemy]["Resistances"][attr] = 1
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Weak"]["Offset"], 16))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Weak"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 0
        Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"]["Resist"]["Offset"], 16))
        total = int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"]["Resist"]["Length"]), "little")
        for attr in attributes:
            if (total & attributes[attr]) != 0:
                log[enemy]["Resistances"][attr] = 2
        #Attack damage
        log[enemy]["AttackDamage"] = []
        for index in range(len(values["Enemy"][enemy]["AttackCorrection"])):
            attack_id = f"Attack{index + 1}"
            Manager.rom.seek(offset + int(dictionary["Properties"]["Enemy"][attack_id]["Offset"], 16))
            log[enemy]["AttackDamage"].append(int.from_bytes(Manager.rom.read(dictionary["Properties"]["Enemy"][attack_id]["Length"]), "little"))
        log[enemy]["Position"] = all_replacement_invert[enemy] if enemy in all_replacement and all_replacement[enemy] != enemy else "Unchanged"
    
    with open("Spoiler\\Enemy.json", "w") as file_writer:
        file_writer.write(json.dumps(log, indent=2))