from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import configparser
import sys
import random
import math
import re
import os
import shutil
import requests
import zipfile
import subprocess
import glob
from enum import Enum

#Enemy Lists

pre_minor = [
    "Slogra",
    "Gaibon"
]
minor = [
    "Doppleganger 1"
]
skip = [
    "Zombie",
    "Warg",
    "Spike ball",
    "Shaft Orb",
    "Stone Skull"
]
progress_to_list = {}
resist_pool = []

log = []

#Shop Lists

base = []
ten = []
hundred = []
thousand = []

#Misc Lists

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

class Attributes(Enum):
    HIT = 0x0020
    CUT = 0x0040
    POI = 0x0080
    CUR = 0x0100
    STO = 0x0200
    WAT = 0x0400
    DAR = 0x0800
    HOL = 0x1000
    ICE = 0x2000
    LIG = 0x4000
    FLA = 0x8000

#Vlads: 10CF2C
#Quick 99: 117cf6 (0x62 > 0x65)

#Config

config = configparser.ConfigParser()
config.optionxform = str
config.read("Data\\config.ini")

#Content

with open("Data\\Offsets\\Enemy.json", "r") as file_reader:
    enemy_content = json.load(file_reader)

with open("Data\\Offsets\\Equipment.json", "r") as file_reader:
    equipment_content = json.load(file_reader)

with open("Data\\Offsets\\HandItem.json", "r") as file_reader:
    handitem_content = json.load(file_reader)

with open("Data\\Offsets\\Shop.json", "r") as file_reader:
    shop_content = json.load(file_reader)

with open("Data\\Offsets\\Spell.json", "r") as file_reader:
    spell_content = json.load(file_reader)

with open("Data\\Offsets\\Stat.json", "r") as file_reader:
    stat_content = json.load(file_reader)

#Data

with open("Data\\Values\\Enemy.json", "r") as file_reader:
    enemy_data = json.load(file_reader)

with open("Data\\Values\\Equipment.json", "r") as file_reader:
    equipment_data = json.load(file_reader)

with open("Data\\Values\\HandItem.json", "r") as file_reader:
    handitem_data = json.load(file_reader)

with open("Data\\Values\\Shop.json", "r") as file_reader:
    shop_data = json.load(file_reader)

with open("Data\\Values\\Spell.json", "r") as file_reader:
    spell_data = json.load(file_reader)

with open("Data\\Values\\Stat.json", "r") as file_reader:
    stat_data = json.load(file_reader)

#Filling Enemy Lists
for i in range(19):
    list = []
    for e in range(99):
        if e <= 49:
            for o in range(abs(i - 19)):
                list.append(e+1)
        else:
            list.append(e+1)
    progress_to_list[str(i)] = list

list = []
for i in range(25):
    list.append(i+1)
progress_to_list["PreMinor"] = list

list = []
for i in range(50):
    list.append(i+1)
progress_to_list["Minor"] = list

for i in range(7):
    resist_pool.append(0)

for i in range(42):
    resist_pool.append(1)

for i in range(4):
    resist_pool.append(2)

for i in range(2):
    resist_pool.append(3)

for i in range(1):
    resist_pool.append(4)

#Filling Shop Lists
i = 10
while i <= 90:
    for e in range(10):
        base.append(i)
    i += 10

i = 100
while i <= 900:
    for e in range(10):
        base.append(i)
    i += 100

i = 1000
while i <= 9000:
    for e in range(10):
        base.append(i)
    i += 1000

i = 10000
while i <= 90000:
    for e in range(10):
        base.append(i)
    i += 10000

base.append(100000)

i = 0
while i <= 90:
    ten.append(i)
    i += 10

i = 0
while i <= 900:
    hundred.append(i)
    i += 100

i = 0
while i <= 9000:
    thousand.append(i)
    i += 1000

#Functions

def writing():
    with open("Data\\config.ini", "w") as file_writer:
        config.write(file_writer)
    sys.exit()

#Threads

class Signaller(QObject):
    progress = Signal(int)
    finished = Signal()

class Patch(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.signaller = Signaller()

    def run(self):
        self.signaller.progress.emit(0)
        
        root = os.getcwd()
        os.chdir("ErrorRecalc")
        os.system("cmd /c error_recalc.exe \"rom.bin\"")
        os.chdir(root)
        
        self.signaller.progress.emit(1)
        
        if config.get("Misc", "sOutputFolder") and os.path.isdir(config.get("Misc", "sOutputFolder")):
            shutil.move("ErrorRecalc\\rom.bin", config.get("Misc", "sOutputFolder") + "\\" + config.get("Misc", "sInputFile").split("\\")[-1])
        else:
            shutil.move("ErrorRecalc\\rom.bin", config.get("Misc", "sInputFile"))
        
        shutil.copyfile("BizhawkCheats\\Cheats.cht", config.get("Misc", "sInputFile").split("\\")[-1][:-4].replace(" (Track 1)", "") + ".cht")
        
        self.signaller.finished.emit()

class Update(QThread):
    def __init__(self, progressBar, api):
        QThread.__init__(self)
        self.signaller = Signaller()
        self.progressBar = progressBar
        self.api = api

    def run(self):
        progress = 0
        self.signaller.progress.emit(progress)
        
        with open("SotnKindAndFair.zip", "wb") as file_writer:
            url = requests.get(self.api["assets"][0]["browser_download_url"], stream=True)
            for data in url.iter_content(chunk_size=4096):
                file_writer.write(data)
                progress += len(data)
                self.signaller.progress.emit(progress)
        
        self.progressBar.setLabelText("Extracting...")
        
        os.rename("KindAndFair.exe", "OldKindAndFair.exe")
        with zipfile.ZipFile("SotnKindAndFair.zip", "r") as zip_ref:
            zip_ref.extractall("")
        os.remove("SotnKindAndFair.zip")
        
        subprocess.Popen("KindAndFair.exe")
        sys.exit()

#Interface

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)
        self.initUI()
        self.check_for_updates()

    def initUI(self):
        self.setStyleSheet("QWidget{background:transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QLabel{border: 1px}"
        + "QMessageBox{background-color: #1d150f}"
        + "QDialog{background-color: #1d150f}"
        + "QProgressDialog{background-color: #1d150f}"
        + "QPushButton{background-color: #1d150f}"
        + "QLineEdit{background-color: #1d150f}"
        + "QMenu{background-color: #1d150f}"
        + "QToolTip{border: 0px; background-color: #1d150f; color: #ffffff; font-family: Cambria; font-size: 18px}")
        
        #MainLayout
        
        grid = QGridLayout()
        grid.setSpacing(10)

        #Groupboxes

        box_1_grid = QGridLayout()
        self.box_1 = QGroupBox("Enemy Randomization")
        self.box_1.setLayout(box_1_grid)
        grid.addWidget(self.box_1, 0, 0, 1, 1)

        box_3_grid = QGridLayout()
        self.box_3 = QGroupBox("Shop Randomization")
        self.box_3.setLayout(box_3_grid)
        grid.addWidget(self.box_3, 0, 1, 1, 1)

        box_4_grid = QGridLayout()
        self.box_4 = QGroupBox("Extra Tweaks")
        self.box_4.setLayout(box_4_grid)
        grid.addWidget(self.box_4, 1, 0, 1, 2)

        box_2_grid = QGridLayout()
        self.box_2 = QGroupBox("Enemy Damage")
        self.box_2.setLayout(box_2_grid)
        grid.addWidget(self.box_2, 2, 0, 1, 1)

        box_7_grid = QGridLayout()
        self.box_7 = QGroupBox("Special Mode")
        self.box_7.setLayout(box_7_grid)
        grid.addWidget(self.box_7, 2, 1, 1, 1)

        box_5_grid = QGridLayout()
        self.box_5 = QGroupBox("Input File")
        self.box_5.setLayout(box_5_grid)
        grid.addWidget(self.box_5, 3, 0, 1, 1)

        box_6_grid = QGridLayout()
        self.box_6 = QGroupBox("Output Folder")
        self.box_6.setLayout(box_6_grid)
        grid.addWidget(self.box_6, 3, 1, 1, 1)
        
        #Checkboxes

        self.check_box_1 = QCheckBox("Enemy Levels")
        self.check_box_1.setToolTip("Randomize the level of every enemy. Stats that scale with \nlevel include HP, attack, defense and EXP.\nPicking this option will disable the removal of your\nstarting equipment from Death's cutscene.")
        self.check_box_1.stateChanged.connect(self.check_box_1_changed)
        box_1_grid.addWidget(self.check_box_1, 0, 0)

        self.check_box_2 = QCheckBox("Enemy Tolerances")
        self.check_box_2.setToolTip("Randomize the resistance/weakness attributes of every enemy.")
        self.check_box_2.stateChanged.connect(self.check_box_2_changed)
        box_1_grid.addWidget(self.check_box_2, 1, 0)
        
        self.check_box_3 = QCheckBox("Item Cost")
        self.check_box_3.setToolTip("Randomize shop prices. Does not affect the relic slot.")
        self.check_box_3.stateChanged.connect(self.check_box_3_changed)
        box_3_grid.addWidget(self.check_box_3, 0, 0)
        
        self.check_box_4 = QCheckBox("Level 1 Locked")
        self.check_box_4.setToolTip("Set all enemy EXP to 0, locking you at level 1 for the entire game.")
        self.check_box_4.stateChanged.connect(self.check_box_4_changed)
        box_4_grid.addWidget(self.check_box_4, 0, 0)
        
        self.check_box_5 = QCheckBox("Bigtoss Only")
        self.check_box_5.setToolTip("Any enemy attack that is not overriden by your defense will bigtoss.")
        self.check_box_5.stateChanged.connect(self.check_box_5_changed)
        box_4_grid.addWidget(self.check_box_5, 1, 0)

        #RadioButtons
        
        self.radio_button_1 = QRadioButton("x1")
        self.radio_button_1.setToolTip("Enemy damage is close to vanilla.")
        self.radio_button_1.toggled.connect(self.radio_button_group_1_checked)
        box_2_grid.addWidget(self.radio_button_1, 0, 0)
        
        self.radio_button_2 = QRadioButton("x2")
        self.radio_button_2.setToolTip("Base enemy attack power is doubled.")
        self.radio_button_2.toggled.connect(self.radio_button_group_1_checked)
        box_2_grid.addWidget(self.radio_button_2, 1, 0)
        
        self.radio_button_3 = QRadioButton("None")
        self.radio_button_3.setToolTip("No special game mode.")
        self.radio_button_3.toggled.connect(self.radio_button_group_2_checked)
        box_7_grid.addWidget(self.radio_button_3, 0, 0)
        
        self.radio_button_4 = QRadioButton("God Mode")
        self.radio_button_4.setToolTip("Alucard is invincible and can kill enemies by running into them.")
        self.radio_button_4.toggled.connect(self.radio_button_group_2_checked)
        box_7_grid.addWidget(self.radio_button_4, 1, 0)
        
        #InitCheckboxes
        
        if config.getboolean("EnemyRandomization", "bEnemyLevels"):
            self.check_box_1.setChecked(True)
        if config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            self.check_box_2.setChecked(True)
        if config.getboolean("ShopRandomization", "bItemCost"):
            self.check_box_3.setChecked(True)
        if config.getboolean("ExtraTweaks", "bLevelOneLocked"):
            self.check_box_4.setChecked(True)
        if config.getboolean("ExtraTweaks", "bBigtossOnly"):
            self.check_box_5.setChecked(True)
        
        if config.getboolean("EnemyDamage", "bx1"):
            self.radio_button_1.setChecked(True)
        else:
            self.radio_button_2.setChecked(True)
        
        if config.getboolean("SpecialMode", "bNone"):
            self.radio_button_3.setChecked(True)
        else:
            self.radio_button_4.setChecked(True)
        
        #TextField

        self.input_field = QLineEdit(config.get("Misc", "sInputFile"))
        self.input_field.setToolTip("Path to your input rom.")
        self.input_field.textChanged[str].connect(self.new_input)
        box_5_grid.addWidget(self.input_field, 0, 0)
        
        self.output_field = QLineEdit(config.get("Misc", "sOutputFolder"))
        self.output_field.setToolTip("Path to your output folder.")
        self.output_field.textChanged[str].connect(self.new_output)
        box_6_grid.addWidget(self.output_field, 0, 0)

        #Buttons
        
        button_1 = QPushButton("Patch")
        button_1.setToolTip("Patch rom with current settings.")
        button_1.clicked.connect(self.button_1_clicked)
        grid.addWidget(button_1, 5, 0, 1, 2)
        
        button_2 = QPushButton()
        button_2.setIcon(QPixmap("Data\\browse.png"))
        button_2.setToolTip("Browse input.")
        button_2.clicked.connect(self.button_2_clicked)
        box_5_grid.addWidget(button_2, 0, 1)
        
        button_3 = QPushButton()
        button_3.setIcon(QPixmap("Data\\browse.png"))
        button_3.setToolTip("Browse output.")
        button_3.clicked.connect(self.button_3_clicked)
        box_6_grid.addWidget(button_3, 0, 1)
        
        button_4 = QPushButton("About")
        button_4.setToolTip("What this mod does.")
        button_4.clicked.connect(self.button_4_clicked)
        grid.addWidget(button_4, 4, 0, 1, 1)
        
        button_5 = QPushButton("Credits")
        button_5.setToolTip("People involved with this mod.")
        button_5.clicked.connect(self.button_5_clicked)
        grid.addWidget(button_5, 4, 1, 1, 1)
        
        #Window
        
        self.setLayout(grid)
        self.setFixedSize(512, 432)
        self.setWindowTitle("KindAndFair")
        self.setWindowIcon(QIcon("Data\\icon.png"))
        
        #Background
        
        background = QPixmap("Data\\background.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, background)
        self.show()        
        self.setPalette(palette)
        
        #Position
        
        center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        geo = self.frameGeometry()
        geo.moveCenter(center)
        self.move(geo.topLeft())
        
        QApplication.processEvents()

    def check_box_1_changed(self):
        if self.check_box_1.isChecked():
            config.set("EnemyRandomization", "bEnemyLevels", "true")
        else:
            config.set("EnemyRandomization", "bEnemyLevels", "false")

    def check_box_2_changed(self):
        if self.check_box_2.isChecked():
            config.set("EnemyRandomization", "bEnemyTolerances", "true")
        else:
            config.set("EnemyRandomization", "bEnemyTolerances", "false")

    def check_box_3_changed(self):
        if self.check_box_3.isChecked():
            config.set("ShopRandomization", "bItemCost", "true")
        else:
            config.set("ShopRandomization", "bItemCost", "false")

    def check_box_4_changed(self):
        if self.check_box_4.isChecked():
            config.set("ExtraTweaks", "bLevelOneLocked", "true")
        else:
            config.set("ExtraTweaks", "bLevelOneLocked", "false")

    def check_box_5_changed(self):
        if self.check_box_5.isChecked():
            config.set("ExtraTweaks", "bBigtossOnly", "true")
        else:
            config.set("ExtraTweaks", "bBigtossOnly", "false")

    def radio_button_group_1_checked(self):
        if self.radio_button_1.isChecked():
            config.set("EnemyDamage", "bx1", "true")
            config.set("EnemyDamage", "bx2", "false")
        else:
            config.set("EnemyDamage", "bx1", "false")
            config.set("EnemyDamage", "bx2", "true")

    def radio_button_group_2_checked(self):
        if self.radio_button_3.isChecked():
            config.set("SpecialMode", "bNone", "true")
            config.set("SpecialMode", "bGodMode", "false")
        else:
            config.set("SpecialMode", "bNone", "false")
            config.set("SpecialMode", "bGodMode", "true")
    
    def new_input(self, input):
        config.set("Misc", "sInputFile", input)
    
    def new_output(self, output):
        config.set("Misc", "sOutputFolder", output)
    
    def set_progress(self, progress):
        self.progressBar.setValue(progress)
    
    def patch_finished(self):
        box = QMessageBox(self)
        box.setWindowTitle("Done")
        box.setText("Rom patched !")
        box.exec()
        writing()

    def button_1_clicked(self):
        self.setEnabled(False)
        QApplication.processEvents()
        
        if not config.get("Misc", "sInputFile") or not os.path.isfile(config.get("Misc", "sInputFile")):
            self.no_path()
            self.setEnabled(True)
            return
        
        shutil.copyfile(config.get("Misc", "sInputFile"), "ErrorRecalc\\rom.bin")
        
        self.file = open("ErrorRecalc\\rom.bin", "r+b")

        if config.getboolean("EnemyRandomization", "bEnemyLevels") or config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            self.random_enemy(config.getboolean("EnemyRandomization", "bEnemyLevels"), config.getboolean("EnemyRandomization", "bEnemyTolerances"))
        if config.getboolean("ShopRandomization", "bItemCost"):
            self.random_shop()
        if config.getboolean("ExtraTweaks", "bLevelOneLocked"):
            self.no_exp()
        if config.getboolean("ExtraTweaks", "bBigtossOnly"):
            self.all_toss()
        if config.getboolean("EnemyDamage", "bx2"):
            self.double_damage()
        if config.getboolean("SpecialMode", "bGodMode"):
            self.god_mode()
        self.write_enemy()
        self.write_shop()
        self.write_equip()
        self.write_item()
        self.write_spell()
        self.write_stats()
        self.write_description()
        self.write_misc()
        self.read_enemy()
        
        self.file.close()
        
        self.progressBar = QProgressDialog("Patching...", None, 0, 1, self)
        self.progressBar.setWindowTitle("Status")
        self.progressBar.setWindowModality(Qt.WindowModal)
        
        self.worker = Patch()
        self.worker.signaller.progress.connect(self.set_progress)
        self.worker.signaller.finished.connect(self.patch_finished)
        self.worker.start()
    
    def button_2_clicked(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="File", filter="*.bin")[0]
        if file:
            self.input_field.setText(file.replace("/", "\\"))
    
    def button_3_clicked(self):
        path = QFileDialog.getExistingDirectory(self, "Folder")
        if path:
            self.output_field.setText(path.replace("/", "\\"))
    
    def button_4_clicked(self):
        box = QMessageBox(self)
        box.setWindowTitle("About")
        box.setText("Applying this mod to your rom will change several things by default:<br/><br/><span style=\"color: #f6b26b;\">Balance enemy stats</span>: Bring enemy stat pools closer to each other and avoid extremes like what the vanilla game does.<br/><br/><span style=\"color: #f6b26b;\">Tweak equipment</span>: Tone down god tier items, adjust MP costs and improve underpowered techniques and spells.<br/><br/><span style=\"color: #f6b26b;\">Improve starting stats</span>: Start the game with a minimum of 100 HP and 50 MP.<br/><br/><span style=\"color: #f6b26b;\">Assign elemental attributes</span>: Give player/enemy attacks proper elemental attributes when needed.<br/><br/><span style=\"color: #f6b26b;\">Rework knockback</span>: Make enemy knockback based on the nature of the attack rather than its damage output.")
        box.exec()
    
    def button_5_clicked(self):
        label1_image = QLabel()
        label1_image.setPixmap(QPixmap("Data\\profile1.png"))
        label1_text = QLabel()
        label1_text.setText("<span style=\"font-weight: bold; color: #67aeff;\">Lakifume</span><br/>Author of Kind And Fair<br/><a href=\"https://github.com/Lakifume\"><font face=Cambria color=#67aeff>Github</font></a>")
        label1_text.setOpenExternalLinks(True)
        label2_image = QLabel()
        label2_image.setPixmap(QPixmap("Data\\profile2.png"))
        label2_text = QLabel()
        label2_text.setText("<span style=\"font-weight: bold; color: #3f40ff;\">Z3R0X</span><br/>Creator of enemy stat editor<br/><a href=\"https://www.youtube.com/ClassicGameHacking\"><font face=Cambria color=#3f40ff>YouTube</font></a>")
        label2_text.setOpenExternalLinks(True)
        label3_image = QLabel()
        label3_image.setPixmap(QPixmap("Data\\profile3.png"))
        label3_text = QLabel()
        label3_text.setText("<span style=\"font-weight: bold; color: #b96f49;\">Mauk</span><br/>Offset researcher<br/><a href=\"https://castlevaniamodding.boards.net/thread/593/castlevania-sotn-mod-ps1\"><font face=Cambria color=#b96f49>Hack</font></a>")
        label3_text.setOpenExternalLinks(True)
        label4_image = QLabel()
        label4_image.setPixmap(QPixmap("Data\\profile4.png"))
        label4_text = QLabel()
        label4_text.setText("<span style=\"font-weight: bold; color: #f513dc;\">TheOkayGuy</span><br/>Testing and cheesing<br/><a href=\"https://www.twitch.tv/theokayguy\"><font face=Cambria color=#f513dc>Twitch</font></a>")
        label4_text.setOpenExternalLinks(True)
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.addWidget(label1_image, 0, 0, 1, 1)
        layout.addWidget(label1_text, 0, 1, 1, 1)
        layout.addWidget(label2_image, 1, 0, 1, 1)
        layout.addWidget(label2_text, 1, 1, 1, 1)
        layout.addWidget(label3_image, 2, 0, 1, 1)
        layout.addWidget(label3_text, 2, 1, 1, 1)
        layout.addWidget(label4_image, 3, 0, 1, 1)
        layout.addWidget(label4_text, 3, 1, 1, 1)
        box = QDialog(self)
        box.setLayout(layout)
        box.setWindowTitle("Credits")
        box.exec()
    
    def no_path(self):
        box = QMessageBox(self)
        box.setWindowTitle("Path")
        box.setIcon(QMessageBox.Critical)
        box.setText("Input path invalid.")
        box.exec()
    
    def random_enemy(self, level, resist):
        for i in range(len(enemy_data)):
            if enemy_data[i]["Key"] in skip:
                continue
            
            if level:
                if enemy_data[i]["Value"]["IsMainEntry"]:
                    if enemy_data[i]["Key"] == "Dracula":
                        enemy_data[i]["Value"]["Level"] = abs(shaft_level - 100)
                    elif enemy_data[i]["Key"] in pre_minor:
                        enemy_data[i]["Value"]["Level"] = random.choice(progress_to_list["PreMinor"])
                    elif enemy_data[i]["Key"] in minor:
                        enemy_data[i]["Value"]["Level"] = random.choice(progress_to_list["Minor"])
                    elif enemy_data[i]["Value"]["Level"] > 44:
                        enemy_data[i]["Value"]["Level"] = random.choice(progress_to_list["18"])
                    elif enemy_data[i]["Value"]["Level"] > 42:
                        enemy_data[i]["Value"]["Level"] = random.choice(progress_to_list["17"])
                    else:
                        enemy_data[i]["Value"]["Level"] = random.choice(progress_to_list[str(int(enemy_data[i]["Value"]["Level"]/(40/17)))])
                    if enemy_data[i]["Key"] == "Shaft":
                        shaft_level = enemy_data[i]["Value"]["Level"]
                else:
                    enemy_data[i]["Value"]["Level"] = enemy_data[i-1]["Value"]["Level"]
            
            if "Intro" in enemy_data[i]["Key"]:
                continue
            
            if resist:
                for e in Attributes:
                    if enemy_data[i]["Value"]["IsMainEntry"]:
                        enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] = random.choice(resist_pool)
                    else:
                        enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] = enemy_data[i-1]["Value"]["Resistances"][str(e).split(".")[1]]
                
                if enemy_data[i]["Key"] in pre_minor and enemy_data[i]["Value"]["Resistances"]["HIT"] > 2:
                    enemy_data[i]["Value"]["Resistances"]["HIT"] = 2
                elif enemy_data[i]["Key"] in minor and enemy_data[i]["Value"]["Resistances"]["CUT"] > 2:
                    enemy_data[i]["Value"]["Resistances"]["CUT"] = 2
        
        if level:
            for i in removal_offset:
                self.file.seek(i)
                self.file.write((0).to_bytes(2, "little"))

    def random_shop(self):
        for i in shop_data:
            if i["Key"] == "Slot1":
                continue
            chosen = random.choice(base)
            if chosen != 100000:
                if chosen >= 100:
                    chosen += random.choice(ten)
                if chosen >= 1000:
                    chosen += random.choice(hundred)
                if chosen >= 10000:
                    chosen += random.choice(thousand)
            i["Value"]["Price"] = chosen

    def no_exp(self):
        for i in enemy_data:
            i["Value"]["ExperienceLevel1"] = 0
            i["Value"]["ExperienceLevel99"] = 0

    def all_toss(self):
        for i in enemy_data:
            i["Value"]["ContactDamageType"] = "0x{:04x}".format(int(int(i["Value"]["ContactDamageType"], 16)/16)*16 + 5)
            for e in range(len(i["Value"]["AttackDamageType"])):
                i["Value"]["AttackDamageType"][e] = "0x{:04x}".format(int(int(i["Value"]["AttackDamageType"][e], 16)/16)*16 + 5)

    def double_damage(self):
        for i in enemy_data:
            i["Value"]["ContactDamageLevel1"] *= 2
            i["Value"]["ContactDamageLevel99"] *= 2
        for i in handitem_data:
            if i["Value"]["IsFood"]:
                i["Value"]["Attack"] *= 2
    
    def god_mode(self):
        for i in enemy_data:
            if i["Value"]["HealthLevel1"] == 32767 or "Intro" in i["Key"]:
                continue
            i["Value"]["HealthLevel1"] = 0
            i["Value"]["HealthLevel99"] = 0
            i["Value"]["ExperienceLevel1"] = 0
            i["Value"]["ExperienceLevel99"] = 0
        self.file.seek(0x126626)
        self.file.write((0).to_bytes(1, "little"))
        self.file.seek(0x3A06F52)
        self.file.write((0).to_bytes(1, "little"))
        self.file.seek(0x59EB092)
        self.file.write((4096).to_bytes(2, "little"))
        self.file.seek(0x59EBC7A)
        self.file.write((4096).to_bytes(2, "little"))
    
    def write_enemy(self):
        for i in range(len(enemy_content)):
            health = math.ceil(((enemy_data[i]["Value"]["HealthLevel99"] - enemy_data[i]["Value"]["HealthLevel1"])/98)*(enemy_data[i]["Value"]["Level"]-1) + enemy_data[i]["Value"]["HealthLevel1"])
            if health < 0:
                health = 0
            if health > 0x8000:
                health = 0x8000
            self.file.seek(int(enemy_content[i]["Value"]["Health"], 16))
            self.file.write(health.to_bytes(2, "little"))
            
            strength = math.ceil(((enemy_data[i]["Value"]["ContactDamageLevel99"] - enemy_data[i]["Value"]["ContactDamageLevel1"])/98)*(enemy_data[i]["Value"]["Level"]-1) + enemy_data[i]["Value"]["ContactDamageLevel1"])
            if strength < 0:
                strength = 0
            if strength > 0x8000:
                strength = 0x8000
            self.file.seek(int(enemy_content[i]["Value"]["ContactDamage"], 16))
            
            if enemy_data[i]["Value"]["HasContact"]:
                self.file.write(strength.to_bytes(2, "little"))
            else:
                self.file.write((0).to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["ContactDamageType"], 16))
            self.file.write(int(enemy_data[i]["Value"]["ContactDamageType"], 16).to_bytes(2, "little"))
            
            defense = math.ceil(((enemy_data[i]["Value"]["DefenseLevel99"] - enemy_data[i]["Value"]["DefenseLevel1"])/98)*(enemy_data[i]["Value"]["Level"]-1) + enemy_data[i]["Value"]["DefenseLevel1"])
            if defense < 0:
                defense = 0
            if defense > 0x8000:
                defense = 0x8000
            self.file.seek(int(enemy_content[i]["Value"]["Defense"], 16))
            self.file.write(defense.to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["Surface"], 16))
            self.file.write(int(enemy_data[i]["Value"]["Surface"], 16).to_bytes(2, "little"))
            
            weak = 0
            strong = 0
            immune = 0
            absorb = 0
            
            for e in Attributes:
                if enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 0:
                    weak += e.value
                elif enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 2:
                    strong += e.value
                elif enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 3:
                    immune += e.value
                elif enemy_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 4:
                    absorb += e.value
            
            if enemy_data[i]["Value"]["IsImpervious"]:
                weak = 0
                strong = 0
                immune = 0xFFE0
                absorb = 0
            
            self.file.seek(int(enemy_content[i]["Value"]["Resistances"]["Weak"], 16))
            self.file.write(weak.to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["Resistances"]["Strong"], 16))
            self.file.write(strong.to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["Resistances"]["Immune"], 16))
            self.file.write(immune.to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["Resistances"]["Absorb"], 16))
            self.file.write(absorb.to_bytes(2, "little"))
            
            self.file.seek(int(enemy_content[i]["Value"]["Level"], 16))
            self.file.write(enemy_data[i]["Value"]["Level"].to_bytes(2, "little"))
            
            experience = math.ceil(((enemy_data[i]["Value"]["ExperienceLevel99"] - enemy_data[i]["Value"]["ExperienceLevel1"])/98)*(enemy_data[i]["Value"]["Level"]-1) + enemy_data[i]["Value"]["ExperienceLevel1"])
            if experience < 0:
                experience = 0
            if experience > 0x8000:
                experience = 0x8000
            self.file.seek(int(enemy_content[i]["Value"]["Experience"], 16))
            self.file.write(experience.to_bytes(2, "little"))
            
            for e in range(len(enemy_content[i]["Value"]["AttackDamage"])):
                damage = math.ceil(enemy_data[i]["Value"]["AttackDamageMultiplier"][e]*strength)
                if damage < 0:
                    damage = 0
                if damage > 0x8000:
                    damage = 0x8000
                self.file.seek(int(enemy_content[i]["Value"]["AttackDamage"][e], 16))
                self.file.write(damage.to_bytes(2, "little"))
            
            for e in range(len(enemy_content[i]["Value"]["AttackDamageType"])):
                self.file.seek(int(enemy_content[i]["Value"]["AttackDamageType"][e], 16))
                self.file.write(int(enemy_data[i]["Value"]["AttackDamageType"][e], 16).to_bytes(2, "little"))

    def write_shop(self):
        for i in range(len(shop_content)):
            if shop_data[i]["Value"]["Price"] < 0:
                shop_data[i]["Value"]["Price"] = 0
            if shop_data[i]["Value"]["Price"] > 0x80000000:
                shop_data[i]["Value"]["Price"] = 0x80000000
            self.file.seek(int(shop_content[i]["Value"]["Price"], 16))
            self.file.write(int(shop_data[i]["Value"]["Price"]).to_bytes(4, "little"))

    def write_equip(self):
        for i in range(len(equipment_content)):
            if equipment_data[i]["Value"]["Attack"] < -0x7FFF:
                equipment_data[i]["Value"]["Attack"] = -0x7FFF
            if equipment_data[i]["Value"]["Attack"] > 0x8000:
                equipment_data[i]["Value"]["Attack"] = 0x8000
            if equipment_data[i]["Value"]["Attack"] < 0:
                equipment_data[i]["Value"]["Attack"] += 0x10000
            self.file.seek(int(equipment_content[i]["Value"]["Attack"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Attack"]).to_bytes(2, "little"))
            
            if equipment_data[i]["Value"]["Defense"] < -0x7FFF:
                equipment_data[i]["Value"]["Defense"] = -0x7FFF
            if equipment_data[i]["Value"]["Defense"] > 0x8000:
                equipment_data[i]["Value"]["Defense"] = 0x8000
            if equipment_data[i]["Value"]["Defense"] < 0:
                equipment_data[i]["Value"]["Defense"] += 0x10000
            self.file.seek(int(equipment_content[i]["Value"]["Defense"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Defense"]).to_bytes(2, "little"))
            
            if equipment_data[i]["Value"]["Strength"] < -0x7F:
                equipment_data[i]["Value"]["Strength"] = -0x7F
            if equipment_data[i]["Value"]["Strength"] > 0x80:
                equipment_data[i]["Value"]["Strength"] = 0x80
            if equipment_data[i]["Value"]["Strength"] < 0:
                equipment_data[i]["Value"]["Strength"] += 0x100
            self.file.seek(int(equipment_content[i]["Value"]["Strength"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Strength"]).to_bytes(1, "little"))
            
            if equipment_data[i]["Value"]["Constitution"] < -0x7F:
                equipment_data[i]["Value"]["Constitution"] = -0x7F
            if equipment_data[i]["Value"]["Constitution"] > 0x80:
                equipment_data[i]["Value"]["Constitution"] = 0x80
            if equipment_data[i]["Value"]["Constitution"] < 0:
                equipment_data[i]["Value"]["Constitution"] += 0x100
            self.file.seek(int(equipment_content[i]["Value"]["Constitution"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Constitution"]).to_bytes(1, "little"))
            
            if equipment_data[i]["Value"]["Intelligence"] < -0x7F:
                equipment_data[i]["Value"]["Intelligence"] = -0x7F
            if equipment_data[i]["Value"]["Intelligence"] > 0x80:
                equipment_data[i]["Value"]["Intelligence"] = 0x80
            if equipment_data[i]["Value"]["Intelligence"] < 0:
                equipment_data[i]["Value"]["Intelligence"] += 0x100
            self.file.seek(int(equipment_content[i]["Value"]["Intelligence"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Intelligence"]).to_bytes(1, "little"))
            
            if equipment_data[i]["Value"]["Luck"] < -0x7F:
                equipment_data[i]["Value"]["Luck"] = -0x7F
            if equipment_data[i]["Value"]["Luck"] > 0x80:
                equipment_data[i]["Value"]["Luck"] = 0x80
            if equipment_data[i]["Value"]["Luck"] < 0:
                equipment_data[i]["Value"]["Luck"] += 0x100
            self.file.seek(int(equipment_content[i]["Value"]["Luck"], 16))
            self.file.write(int(equipment_data[i]["Value"]["Luck"]).to_bytes(1, "little"))
            
            weak = 0
            strong = 0
            immune = 0
            absorb = 0
            
            for e in Attributes:
                if equipment_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 0:
                    weak += e.value
                elif equipment_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 2:
                    strong += e.value
                elif equipment_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 3:
                    immune += e.value
                elif equipment_data[i]["Value"]["Resistances"][str(e).split(".")[1]] == 4:
                    absorb += e.value
            
            self.file.seek(int(equipment_content[i]["Value"]["Resistances"]["Weak"], 16))
            self.file.write(weak.to_bytes(2, "little"))
            
            self.file.seek(int(equipment_content[i]["Value"]["Resistances"]["Strong"], 16))
            self.file.write(strong.to_bytes(2, "little"))
            
            self.file.seek(int(equipment_content[i]["Value"]["Resistances"]["Immune"], 16))
            self.file.write(immune.to_bytes(2, "little"))
            
            self.file.seek(int(equipment_content[i]["Value"]["Resistances"]["Absorb"], 16))
            self.file.write(absorb.to_bytes(2, "little"))
    
    def write_item(self):
        for i in range(len(handitem_content)):
            if handitem_data[i]["Value"]["Attack"] < -0x7FFF:
                handitem_data[i]["Value"]["Attack"] = -0x7FFF
            if handitem_data[i]["Value"]["Attack"] > 0x8000:
                handitem_data[i]["Value"]["Attack"] = 0x8000
            if handitem_data[i]["Value"]["Attack"] < 0:
                handitem_data[i]["Value"]["Attack"] += 0x10000
            self.file.seek(int(handitem_content[i]["Value"]["Attack"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Attack"]).to_bytes(2, "little"))
            
            if handitem_data[i]["Value"]["Defense"] < -0x7FFF:
                handitem_data[i]["Value"]["Defense"] = -0x7FFF
            if handitem_data[i]["Value"]["Defense"] > 0x8000:
                handitem_data[i]["Value"]["Defense"] = 0x8000
            if handitem_data[i]["Value"]["Defense"] < 0:
                handitem_data[i]["Value"]["Defense"] += 0x10000
            self.file.seek(int(handitem_content[i]["Value"]["Defense"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Defense"]).to_bytes(2, "little"))
            
            total = 0
            
            for e in Attributes:
                if handitem_data[i]["Value"]["Element"][str(e).split(".")[1]]:
                    total += e.value
            
            self.file.seek(int(handitem_content[i]["Value"]["Element"], 16))
            self.file.write(total.to_bytes(2, "little"))
            
            self.file.seek(int(handitem_content[i]["Value"]["Sprite"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Sprite"], 16).to_bytes(1, "little"))
            
            self.file.seek(int(handitem_content[i]["Value"]["Special"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Special"], 16).to_bytes(1, "little"))
            
            self.file.seek(int(handitem_content[i]["Value"]["Spell"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Spell"], 16).to_bytes(2, "little"))
            
            if handitem_data[i]["Value"]["ManaCost"] < -0x7FFF:
                handitem_data[i]["Value"]["ManaCost"] = -0x7FFF
            if handitem_data[i]["Value"]["ManaCost"] > 0x8000:
                handitem_data[i]["Value"]["ManaCost"] = 0x8000
            if handitem_data[i]["Value"]["ManaCost"] < 0:
                handitem_data[i]["Value"]["ManaCost"] += 0x10000
            self.file.seek(int(handitem_content[i]["Value"]["ManaCost"], 16))
            self.file.write(int(handitem_data[i]["Value"]["ManaCost"]).to_bytes(2, "little"))
            
            if handitem_data[i]["Value"]["StunFrames"] < -0x7FFF:
                handitem_data[i]["Value"]["StunFrames"] = -0x7FFF
            if handitem_data[i]["Value"]["StunFrames"] > 0x8000:
                handitem_data[i]["Value"]["StunFrames"] = 0x8000
            if handitem_data[i]["Value"]["StunFrames"] < 0:
                handitem_data[i]["Value"]["StunFrames"] += 0x10000
            self.file.seek(int(handitem_content[i]["Value"]["StunFrames"], 16))
            self.file.write(int(handitem_data[i]["Value"]["StunFrames"]).to_bytes(2, "little"))
            
            if handitem_data[i]["Value"]["Range"] < -0x7FFF:
                handitem_data[i]["Value"]["Range"] = -0x7FFF
            if handitem_data[i]["Value"]["Range"] > 0x8000:
                handitem_data[i]["Value"]["Range"] = 0x8000
            if handitem_data[i]["Value"]["Range"] < 0:
                handitem_data[i]["Value"]["Range"] += 0x10000
            self.file.seek(int(handitem_content[i]["Value"]["Range"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Range"]).to_bytes(2, "little"))
            
            self.file.seek(int(handitem_content[i]["Value"]["Extra"], 16))
            self.file.write(int(handitem_data[i]["Value"]["Extra"], 16).to_bytes(1, "little"))
    
    def write_spell(self):
        for i in range(len(spell_content)):
            if spell_data[i]["Value"]["ManaCost"] < -0x7F:
                spell_data[i]["Value"]["ManaCost"] = -0x7F
            if spell_data[i]["Value"]["ManaCost"] > 0x80:
                spell_data[i]["Value"]["ManaCost"] = 0x80
            if spell_data[i]["Value"]["ManaCost"] < 0:
                spell_data[i]["Value"]["ManaCost"] += 0x100
            self.file.seek(int(spell_content[i]["Value"]["ManaCost"], 16))
            self.file.write(int(spell_data[i]["Value"]["ManaCost"]).to_bytes(1, "little"))
            
            total = 0
            
            for e in Attributes:
                if spell_data[i]["Value"]["Element"][str(e).split(".")[1]]:
                    total += e.value
            
            self.file.seek(int(spell_content[i]["Value"]["Element"], 16))
            self.file.write(total.to_bytes(2, "little"))
            
            if spell_data[i]["Value"]["Attack"] < -0x7FFF:
                spell_data[i]["Value"]["Attack"] = -0x7FFF
            if spell_data[i]["Value"]["Attack"] > 0x8000:
                spell_data[i]["Value"]["Attack"] = 0x8000
            if spell_data[i]["Value"]["Attack"] < 0:
                spell_data[i]["Value"]["Attack"] += 0x10000
            self.file.seek(int(spell_content[i]["Value"]["Attack"], 16))
            self.file.write(int(spell_data[i]["Value"]["Attack"]).to_bytes(2, "little"))

    def write_stats(self):
        if stat_data["Value"]["StrConIntLck"] < -0x7FFF:
            stat_data["Value"]["StrConIntLck"] = -0x7FFF
        if stat_data["Value"]["StrConIntLck"] > 0x8000:
            stat_data["Value"]["StrConIntLck"] = 0x8000
        if stat_data["Value"]["StrConIntLck"] < 0:
            stat_data["Value"]["StrConIntLck"] += 0x10000
        self.file.seek(int(stat_content["Value"]["StrConIntLck"], 16))
        self.file.write(int(stat_data["Value"]["StrConIntLck"]).to_bytes(2, "little"))
        
        if stat_data["Value"]["Health"] < -0x7FFF:
            stat_data["Value"]["Health"] = -0x7FFF
        if stat_data["Value"]["Health"] > 0x8000 - 5:
            stat_data["Value"]["Health"] = 0x8000 - 5
        if stat_data["Value"]["Health"] < 0:
            stat_data["Value"]["Health"] += 0x10000
        self.file.seek(int(stat_content["Value"]["Health"], 16))
        self.file.write(int(stat_data["Value"]["Health"]).to_bytes(2, "little"))
        
        self.file.seek(0x119CC4)
        self.file.write(int(stat_data["Value"]["Health"] + 5).to_bytes(2, "little"))
        
        if stat_data["Value"]["Hearts"] < -0x7FFF:
            stat_data["Value"]["Hearts"] = -0x7FFF
        if stat_data["Value"]["Hearts"] > 0x8000:
            stat_data["Value"]["Hearts"] = 0x8000
        if stat_data["Value"]["Hearts"] < 0:
            stat_data["Value"]["Hearts"] += 0x10000
        self.file.seek(int(stat_content["Value"]["Hearts"], 16))
        self.file.write(int(stat_data["Value"]["Hearts"]).to_bytes(2, "little"))
        
        if stat_data["Value"]["MaxHearts"] < -0x7FFF:
            stat_data["Value"]["MaxHearts"] = -0x7FFF
        if stat_data["Value"]["MaxHearts"] > 0x8000:
            stat_data["Value"]["MaxHearts"] = 0x8000
        if stat_data["Value"]["MaxHearts"] < 0:
            stat_data["Value"]["MaxHearts"] += 0x10000
        self.file.seek(int(stat_content["Value"]["MaxHearts"], 16))
        self.file.write(int(stat_data["Value"]["MaxHearts"]).to_bytes(2, "little"))
        
        if stat_data["Value"]["Mana"] < -0x7FFF:
            stat_data["Value"]["Mana"] = -0x7FFF
        if stat_data["Value"]["Mana"] > 0x8000:
            stat_data["Value"]["Mana"] = 0x8000
        if stat_data["Value"]["Mana"] < 0:
            stat_data["Value"]["Mana"] += 0x10000
        self.file.seek(int(stat_content["Value"]["Mana"], 16))
        self.file.write(int(stat_data["Value"]["Mana"]).to_bytes(2, "little"))
    
    def write_description(self):
        self.file.seek(0xF2400)
        self.file.write(str.encode("Shocking"))
        self.file.seek(0xF2538)
        self.file.write(str.encode(" flail         "))
        self.file.seek(0xF2736)
        self.file.write(str.encode("N"))
        self.file.seek(0xF3BF8)
        self.file.write(str.encode("Immunity to all status effects"))
        self.file.seek(0xF3C75)
        self.file.write(str.encode("O"))
        self.file.seek(0xF3C9A)
        self.file.write(str.encode("T  "))
        self.file.seek(0xF43FC)
        self.file.write(str.encode("Immune to water "))
        self.file.seek(0xF4420)
        self.file.write(str.encode("Affection for cats          "))
        self.file.seek(0xF4450)
        self.file.write(str.encode("Immune to lightning         "))
        self.file.seek(0xF4480)
        self.file.write(str.encode("Immune to darkness          "))
        self.file.seek(0xF44B0)
        self.file.write(str.encode("Immune to ice            "))
        self.file.seek(0xF44DC)
        self.file.write(str.encode("Immune to fire            "))
        self.file.seek(0xF4508)
        self.file.write(str.encode("Immune to light           "))
        self.file.seek(0xF4844)
        self.file.write(str.encode("Resistant to evil attacks "))
        self.file.seek(0xF486C)
        self.file.write(str.encode("Immunity to all status effects"))

    def write_misc(self):
        self.file.seek(0x134990)
        self.file.write((0).to_bytes(4, "little"))
        self.file.seek(0x4369E87)
        self.file.write(str.encode("KOJI  IGA"))
        self.file.seek(0x4369EE1)
        self.file.write(str.encode("KOJI  IGA"))
        self.file.seek(0x4369FBC)
        self.file.write(str.encode("KOJI  IGA"))
    
    def read_enemy(self):
        for i in enemy_content:
            entry = {}
            entry["Key"] = i["Key"]
            entry["Value"] = {}
            self.file.seek(int(i["Value"]["Health"], 16))
            entry["Value"]["Health"] = int.from_bytes(self.file.read(2), "little")
            self.file.seek(int(i["Value"]["ContactDamage"], 16))
            entry["Value"]["ContactDamage"] = int.from_bytes(self.file.read(2), "little")
            self.file.seek(int(i["Value"]["ContactDamageType"], 16))
            entry["Value"]["ContactDamageType"] = "0x{:04x}".format(int.from_bytes(self.file.read(2), "little"))
            self.file.seek(int(i["Value"]["Defense"], 16))
            entry["Value"]["Defense"] = int.from_bytes(self.file.read(2), "little")
            self.file.seek(int(i["Value"]["Surface"], 16))
            entry["Value"]["Surface"] = "0x{:04x}".format(int.from_bytes(self.file.read(2), "little"))
            
            entry["Value"]["Resistances"] = {}
            for e in Attributes:
                entry["Value"]["Resistances"][str(e).split(".")[1]] = 1
            
            self.file.seek(int(i["Value"]["Resistances"]["Weak"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    entry["Value"]["Resistances"][str(e).split(".")[1]] = 0
            self.file.seek(int(i["Value"]["Resistances"]["Strong"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    entry["Value"]["Resistances"][str(e).split(".")[1]] = 2
            self.file.seek(int(i["Value"]["Resistances"]["Immune"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    entry["Value"]["Resistances"][str(e).split(".")[1]] = 3
            self.file.seek(int(i["Value"]["Resistances"]["Absorb"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    entry["Value"]["Resistances"][str(e).split(".")[1]] = 4
            
            self.file.seek(int(i["Value"]["Level"], 16))
            entry["Value"]["Level"] = int.from_bytes(self.file.read(2), "little")
            self.file.seek(int(i["Value"]["Experience"], 16))
            entry["Value"]["Experience"] = int.from_bytes(self.file.read(2), "little")
    
            entry["Value"]["AttackDamage"] = []
            for e in i["Value"]["AttackDamage"]:
                self.file.seek(int(e, 16))
                entry["Value"]["AttackDamage"].append(int.from_bytes(self.file.read(2), "little"))
            entry["Value"]["AttackDamageType"] = []
            for e in i["Value"]["AttackDamageType"]:
                self.file.seek(int(e, 16))
                entry["Value"]["AttackDamageType"].append("0x{:04x}".format(int.from_bytes(self.file.read(2), "little")))
            log.append(entry)
        
        with open("SpoilerLog.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def check_for_updates(self):
        if os.path.isfile("OldKindAndFair.exe"):
            os.remove("OldKindAndFair.exe")
        try:
            api = requests.get("https://api.github.com/repos/Lakifume/SotnKindAndFair/releases/latest").json()
        except requests.ConnectionError:
            self.setEnabled(True)
            return
        try:
            tag = api["tag_name"]
        except KeyError:
            self.setEnabled(True)
            return
        if tag != config.get("Misc", "sVersion"):
            choice = QMessageBox.question(self, "Auto Updater", "New version found:\n\n" + api["body"] + "\n\nUpdate ?", QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.progressBar = QProgressDialog("Downloading...", None, 0, api["assets"][0]["size"], self)
                self.progressBar.setWindowTitle("Status")
                self.progressBar.setWindowModality(Qt.WindowModal)
                self.progressBar.setAutoClose(False)
                self.progressBar.setAutoReset(False)
                
                self.worker = Update(self.progressBar, api)
                self.worker.signaller.progress.connect(self.set_progress)
                self.worker.start()
            else:
                self.setEnabled(True)
        else:
            self.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(writing)
    main = Main()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()