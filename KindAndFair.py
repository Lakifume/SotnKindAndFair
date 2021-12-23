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

#Shop Lists

base = []
ten = []
hundred = []
thousand = []
ten_thousand = []

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
i = 100000
while i <= 400000:
    base.append(i)
    i += 100000
base.append(500000)
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
i = 0
while i <= 90000:
    ten_thousand.append(i)
    i += 10000

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
            shutil.copyfile("BizhawkCheats\\Cheats.cht", config.get("Misc", "sOutputFolder") + "\\" + config.get("Misc", "sInputFile").split("\\")[-1][:-4].replace(" (Track 1)", "") + ".cht")
        else:
            shutil.move("ErrorRecalc\\rom.bin", config.get("Misc", "sInputFile"))
            shutil.copyfile("BizhawkCheats\\Cheats.cht", config.get("Misc", "sInputFile")[:-4].replace(" (Track 1)", "") + ".cht")
        
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
        
        #Download
        
        with open("SotnKindAndFair.zip", "wb") as file_writer:
            url = requests.get(self.api["assets"][0]["browser_download_url"], stream=True)
            for data in url.iter_content(chunk_size=4096):
                file_writer.write(data)
                progress += len(data)
                self.signaller.progress.emit(progress)
        
        self.progressBar.setLabelText("Extracting...")
        
        #PurgeFolders
        
        shutil.rmtree("BizhawkCheats")
        shutil.rmtree("Data")
        shutil.rmtree("ErrorRecalc")
        
        os.rename("KindAndFair.exe", "OldKindAndFair.exe")
        with zipfile.ZipFile("SotnKindAndFair.zip", "r") as zip_ref:
            zip_ref.extractall("")
        os.remove("SotnKindAndFair.zip")
        
        #CarryPreviousConfig
        
        new_config = configparser.ConfigParser()
        new_config.optionxform = str
        new_config.read("Data\\config.ini")
        for each_section in new_config.sections():
            for (each_key, each_val) in new_config.items(each_section):
                if each_key == "sVersion":
                    continue
                try:
                    new_config.set(each_section, each_key, config.get(each_section, each_key))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    continue
        with open("Data\\config.ini", "w") as file_writer:
            new_config.write(file_writer)
        
        #OpenNewEXE
        
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
        + "QDoubleSpinBox{background-color: #1d150f}"
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

        box_2_grid = QGridLayout()
        self.box_2 = QGroupBox("Enemy Damage")
        self.box_2.setLayout(box_2_grid)
        grid.addWidget(self.box_2, 1, 0, 1, 1)

        box_4_grid = QGridLayout()
        self.box_4 = QGroupBox("Extra")
        self.box_4.setLayout(box_4_grid)
        grid.addWidget(self.box_4, 2, 0, 1, 2)

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
        self.check_box_4.setToolTip("Alucard is locked at level 1 for the entire game.")
        self.check_box_4.stateChanged.connect(self.check_box_4_changed)
        box_4_grid.addWidget(self.check_box_4, 0, 0)
        
        self.check_box_5 = QCheckBox("Bigtoss Only")
        self.check_box_5.setToolTip("Alucard will always go flying across the room when\ntaking damage. Base enemy damage will be slightly\nreduced to compensate for the extra collision damage.")
        self.check_box_5.stateChanged.connect(self.check_box_5_changed)
        box_4_grid.addWidget(self.check_box_5, 1, 0)
        
        self.check_box_6 = QCheckBox("Continuous Wing Smash")
        self.check_box_6.setToolTip("Wing smashes will cost more MP to initially cast\nbut will no longer need to be chained.")
        self.check_box_6.stateChanged.connect(self.check_box_6_changed)
        box_4_grid.addWidget(self.check_box_6, 0, 1)
        
        #SpinBoxes
        
        if config.getfloat("EnemyDamage", "fDamageMultiplier") < 0.0:
            config.set("EnemyDamage", "fDamageMultiplier", "0.0")
        if config.getfloat("EnemyDamage", "fDamageMultiplier") > 3.0:
            config.set("EnemyDamage", "fDamageMultiplier", "3.0")
        
        self.damage_box = QDoubleSpinBox()
        self.damage_box.setToolTip("Multiplier of damage received.\n(1.0 is close to vanilla)")
        self.damage_box.setDecimals(1)
        self.damage_box.setRange(0.0, 3.0)
        self.damage_box.setSingleStep(0.1)
        self.damage_box.setValue(config.getfloat("EnemyDamage", "fDamageMultiplier"))
        self.damage_box.valueChanged.connect(self.new_damage)
        box_2_grid.addWidget(self.damage_box, 0, 0)
        
        #InitCheckboxes
        
        if config.getboolean("EnemyRandomization", "bEnemyLevels"):
            self.check_box_1.setChecked(True)
        if config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            self.check_box_2.setChecked(True)
        if config.getboolean("ShopRandomization", "bItemCost"):
            self.check_box_3.setChecked(True)
        if config.getboolean("Extra", "bLevel1Locked"):
            self.check_box_4.setChecked(True)
        if config.getboolean("Extra", "bBigtossOnly"):
            self.check_box_5.setChecked(True)
        if config.getboolean("Extra", "bContinuousSmash"):
            self.check_box_6.setChecked(True)
        
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
            config.set("Extra", "bLevel1Locked", "true")
            self.damage_box.setRange(0.0, 2.0)
        else:
            config.set("Extra", "bLevel1Locked", "false")
            self.damage_box.setRange(0.0, 3.0)

    def check_box_5_changed(self):
        if self.check_box_5.isChecked():
            config.set("Extra", "bBigtossOnly", "true")
        else:
            config.set("Extra", "bBigtossOnly", "false")

    def check_box_6_changed(self):
        if self.check_box_6.isChecked():
            config.set("Extra", "bContinuousSmash", "true")
        else:
            config.set("Extra", "bContinuousSmash", "false")
    
    def new_damage(self):
        config.set("EnemyDamage", "fDamageMultiplier", str(round(self.damage_box.value(),1)))
    
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
        
        if not os.path.isdir("SpoilerLog"):
            os.makedirs("SpoilerLog")
        
        shutil.copyfile(config.get("Misc", "sInputFile"), "ErrorRecalc\\rom.bin")
        
        self.file = open("ErrorRecalc\\rom.bin", "r+b")

        if config.getboolean("EnemyRandomization", "bEnemyLevels") or config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            self.random_enemy(config.getboolean("EnemyRandomization", "bEnemyLevels"), config.getboolean("EnemyRandomization", "bEnemyTolerances"))
        if config.getboolean("ShopRandomization", "bItemCost"):
            self.random_shop()
        
        if config.getfloat("EnemyDamage", "fDamageMultiplier") == 0.0:
            self.no_damage()
        self.multiply_damage()
        
        if config.getboolean("Extra", "bLevel1Locked"):
            self.no_exp()
        if config.getboolean("Extra", "bBigtossOnly"):
            self.all_bigtoss()
        if config.getboolean("Extra", "bContinuousSmash"):
            self.wing_smash()
        
        self.write_enemy()
        self.write_equip()
        self.write_item()
        self.write_shop()
        self.write_spell()
        self.write_stat()
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
        box.setText("Applying this mod to your rom will change several things by default:<br/><br/><span style=\"color: #f6b26b;\">Balance enemy stats</span>: Bring enemy stat pools closer to each other and avoid extremes like what the vanilla game does.<br/><br/><span style=\"color: #f6b26b;\">Tweak equipment</span>: Tone down god tier items, adjust MP costs and improve underpowered techniques and spells.<br/><br/><span style=\"color: #f6b26b;\">Improve starting stats</span>: Start the game with a minimum of 120 HP and 50 MP.<br/><br/><span style=\"color: #f6b26b;\">Assign elemental attributes</span>: Give player/enemy attacks proper elemental attributes when needed.<br/><br/><span style=\"color: #f6b26b;\">Rework knockback</span>: Make enemy knockback based on the nature of the attack rather than its damage output.")
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
        label3_text.setText("<span style=\"font-weight: bold; color: #b96f49;\">Mauk</span><br/>Sotn modder<br/><a href=\"https://castlevaniamodding.boards.net/thread/593/castlevania-sotn-mod-ps1\"><font face=Cambria color=#b96f49>Hack</font></a>")
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
        keys_list = list(enemy_data)
        for i in range(len(keys_list)):
            #Level
            if keys_list[i] in skip:
                continue
            if level:
                if enemy_data[keys_list[i]]["IsMainEntry"]:
                    if keys_list[i] == "Shaft":
                        enemy_data[keys_list[i]]["Level"] = random.choice(self.create_list(999, 1, 50))
                    elif keys_list[i] == "Dracula":
                        enemy_data[keys_list[i]]["Level"] = abs(enemy_data["Shaft"]["Level"] - 100)
                    elif keys_list[i] in minor:
                        enemy_data[keys_list[i]]["Level"] = random.choice(self.create_list(enemy_data[keys_list[i]]["Level"], 1, 50))
                    else:
                        enemy_data[keys_list[i]]["Level"] = random.choice(self.create_list(enemy_data[keys_list[i]]["Level"], 1, 99))
                else:
                    enemy_data[keys_list[i]]["Level"] = enemy_data[keys_list[i-1]]["Level"]
            #Resistances
            if "Intro" in keys_list[i]:
                continue
            if resist:
                for e in Attributes:
                    if enemy_data[keys_list[i]]["IsMainEntry"]:
                        enemy_data[keys_list[i]]["Resistances"][str(e).split(".")[1]] = random.choice(resist_pool)
                    else:
                        enemy_data[keys_list[i]]["Resistances"][str(e).split(".")[1]] = enemy_data[keys_list[i-1]]["Resistances"][str(e).split(".")[1]]
        #DeathRemoval
        if level:
            for i in removal_offset:
                self.file.seek(i)
                self.file.write((0).to_bytes(2, "little"))
        #LibraryCard
        self.file.seek(0x4BAA2B0)
        self.file.write((0xA6).to_bytes(1, "little"))

    def create_list(self, value, minimum, maximum):
        list = []
        list_int = minimum
        for i in range(maximum-minimum+1):
            for e in range(2**(abs(math.ceil(abs(list_int-value)*5/max(value-minimum, maximum-value))-5))):
                list.append(list_int)
            list_int += 1
        return list

    def random_shop(self):
        for i in shop_data:
            if i == "Slot1":
                continue
            chosen = random.choice(base)
            if chosen < 500000:
                if chosen >= 100:
                    chosen += random.choice(ten)
                if chosen >= 1000:
                    chosen += random.choice(hundred)
                if chosen >= 10000:
                    chosen += random.choice(thousand)
                if chosen >= 100000:
                    chosen += random.choice(ten_thousand)
            shop_data[i] = chosen
    
    def no_damage(self):
        for i in enemy_data:
            if enemy_data[i]["HealthLevel1"] == 32767 or "Intro" in i:
                continue
            enemy_data[i]["HealthLevel1"] = 0
            enemy_data[i]["HealthLevel99"] = 0
        #Invulnerability
        self.file.seek(0x126626)
        self.file.write((0).to_bytes(1, "little"))
        self.file.seek(0x3A06F52)
        self.file.write((0).to_bytes(1, "little"))
        self.file.seek(0x59EB092)
        self.file.write((0x1000).to_bytes(2, "little"))
        self.file.seek(0x59EBC7A)
        self.file.write((0x1000).to_bytes(2, "little"))

    def multiply_damage(self):
        for i in enemy_data:
            enemy_data[i]["ContactDamageLevel1"] = int(enemy_data[i]["ContactDamageLevel1"]*config.getfloat("EnemyDamage", "fDamageMultiplier"))
            enemy_data[i]["ContactDamageLevel99"] = int(enemy_data[i]["ContactDamageLevel99"]*config.getfloat("EnemyDamage", "fDamageMultiplier"))
        for i in handitem_data:
            if handitem_data[i]["IsFood"]:
                handitem_data[i]["Attack"] = int(handitem_data[i]["Attack"]*config.getfloat("EnemyDamage", "fDamageMultiplier"))

    def no_exp(self):
        self.file.seek(0x117cf6)
        self.file.write((0).to_bytes(1, "little"))
        self.file.seek(0x117da0)
        self.file.write((0).to_bytes(4, "little"))

    def all_bigtoss(self):
        for i in enemy_data:
            if "Intro" in i:
                continue
            enemy_data[i]["ContactDamageType"] = "0x{:04x}".format(int(int(enemy_data[i]["ContactDamageType"], 16)/16)*16 + 5)
            for e in range(len(enemy_data[i]["AttackDamageType"])):
                enemy_data[i]["AttackDamageType"][e] = "0x{:04x}".format(int(int(enemy_data[i]["AttackDamageType"][e], 16)/16)*16 + 5)

    def wing_smash(self):
        spell_data["Wing Smash"]["ManaCost"] = 25
        self.file.seek(0x134990)
        self.file.write((0).to_bytes(4, "little"))
    
    def write_enemy(self):
        for i in enemy_content:
            #Health
            health = math.ceil(((enemy_data[i]["HealthLevel99"] - enemy_data[i]["HealthLevel1"])/98)*(enemy_data[i]["Level"]-1) + enemy_data[i]["HealthLevel1"])
            if health < 0:
                health = 0
            if health > 0x8000:
                health = 0x8000
            self.file.seek(int(enemy_content[i]["Health"], 16))
            self.file.write(health.to_bytes(2, "little"))
            #ContactDamage
            strength = math.ceil(((enemy_data[i]["ContactDamageLevel99"] - enemy_data[i]["ContactDamageLevel1"])/98)*(enemy_data[i]["Level"]-1) + enemy_data[i]["ContactDamageLevel1"])
            if strength < 0:
                strength = 0
            if strength > 0x8000:
                strength = 0x8000
            self.file.seek(int(enemy_content[i]["ContactDamage"], 16))
            if not enemy_data[i]["HasContact"]:
                self.file.write((0).to_bytes(2, "little"))
            elif int(enemy_data[i]["ContactDamageType"], 16) % 16 == 5:
                self.file.write(int(strength*(1 - config.getfloat("EnemyDamage", "fDamageMultiplier")/20)).to_bytes(2, "little"))
            else:
                self.file.write(strength.to_bytes(2, "little"))
            #ContactDamageType
            self.file.seek(int(enemy_content[i]["ContactDamageType"], 16))
            self.file.write(int(enemy_data[i]["ContactDamageType"], 16).to_bytes(2, "little"))
            #Defense
            defense = math.ceil(((enemy_data[i]["DefenseLevel99"] - enemy_data[i]["DefenseLevel1"])/98)*(enemy_data[i]["Level"]-1) + enemy_data[i]["DefenseLevel1"])
            if defense < 0:
                defense = 0
            if defense > 0x8000:
                defense = 0x8000
            self.file.seek(int(enemy_content[i]["Defense"], 16))
            self.file.write(defense.to_bytes(2, "little"))
            #Surface
            self.file.seek(int(enemy_content[i]["Surface"], 16))
            self.file.write(int(enemy_data[i]["Surface"], 16).to_bytes(2, "little"))
            #Resistances
            weak = 0
            strong = 0
            immune = 0
            absorb = 0
            for e in Attributes:
                if enemy_data[i]["Resistances"][str(e).split(".")[1]] == 0:
                    weak += e.value
                elif enemy_data[i]["Resistances"][str(e).split(".")[1]] == 2:
                    strong += e.value
                elif enemy_data[i]["Resistances"][str(e).split(".")[1]] == 3:
                    immune += e.value
                elif enemy_data[i]["Resistances"][str(e).split(".")[1]] == 4:
                    absorb += e.value
            if enemy_data[i]["IsImpervious"]:
                weak = 0
                strong = 0
                immune = 0xFFE0
                absorb = 0
            self.file.seek(int(enemy_content[i]["Resistances"]["Weak"], 16))
            self.file.write(weak.to_bytes(2, "little"))
            self.file.seek(int(enemy_content[i]["Resistances"]["Strong"], 16))
            self.file.write(strong.to_bytes(2, "little"))
            self.file.seek(int(enemy_content[i]["Resistances"]["Immune"], 16))
            self.file.write(immune.to_bytes(2, "little"))
            self.file.seek(int(enemy_content[i]["Resistances"]["Absorb"], 16))
            self.file.write(absorb.to_bytes(2, "little"))
            #Level
            self.file.seek(int(enemy_content[i]["Level"], 16))
            self.file.write(enemy_data[i]["Level"].to_bytes(2, "little"))
            #Experience
            experience = math.ceil(((enemy_data[i]["ExperienceLevel99"] - enemy_data[i]["ExperienceLevel1"])/98)*(enemy_data[i]["Level"]-1) + enemy_data[i]["ExperienceLevel1"])
            if experience < 0:
                experience = 0
            if experience > 0x8000:
                experience = 0x8000
            self.file.seek(int(enemy_content[i]["Experience"], 16))
            self.file.write(experience.to_bytes(2, "little"))
            #AttackDamage
            for e in range(len(enemy_content[i]["AttackDamage"])):
                damage = math.ceil(enemy_data[i]["AttackDamageMultiplier"][e]*strength)
                if damage < 0:
                    damage = 0
                if damage > 0x8000:
                    damage = 0x8000
                self.file.seek(int(enemy_content[i]["AttackDamage"][e], 16))
                if int(enemy_data[i]["AttackDamageType"][e], 16) % 16 == 5:
                    self.file.write(int(damage*(1 - config.getfloat("EnemyDamage", "fDamageMultiplier")/20)).to_bytes(2, "little"))
                else:
                    self.file.write(damage.to_bytes(2, "little"))
            #AttackDamageType
            for e in range(len(enemy_content[i]["AttackDamageType"])):
                self.file.seek(int(enemy_content[i]["AttackDamageType"][e], 16))
                self.file.write(int(enemy_data[i]["AttackDamageType"][e], 16).to_bytes(2, "little"))

    def write_equip(self):
        for i in equipment_content:
            #Attack
            if equipment_data[i]["Attack"] < -0x7FFF:
                equipment_data[i]["Attack"] = -0x7FFF
            if equipment_data[i]["Attack"] > 0x8000:
                equipment_data[i]["Attack"] = 0x8000
            if equipment_data[i]["Attack"] < 0:
                equipment_data[i]["Attack"] += 0x10000
            self.file.seek(int(equipment_content[i]["Attack"], 16))
            self.file.write(int(equipment_data[i]["Attack"]).to_bytes(2, "little"))
            #Defense
            if equipment_data[i]["Defense"] < -0x7FFF:
                equipment_data[i]["Defense"] = -0x7FFF
            if equipment_data[i]["Defense"] > 0x8000:
                equipment_data[i]["Defense"] = 0x8000
            if equipment_data[i]["Defense"] < 0:
                equipment_data[i]["Defense"] += 0x10000
            self.file.seek(int(equipment_content[i]["Defense"], 16))
            self.file.write(int(equipment_data[i]["Defense"]).to_bytes(2, "little"))
            #Strength
            if equipment_data[i]["Strength"] < -0x7F:
                equipment_data[i]["Strength"] = -0x7F
            if equipment_data[i]["Strength"] > 0x80:
                equipment_data[i]["Strength"] = 0x80
            if equipment_data[i]["Strength"] < 0:
                equipment_data[i]["Strength"] += 0x100
            self.file.seek(int(equipment_content[i]["Strength"], 16))
            self.file.write(int(equipment_data[i]["Strength"]).to_bytes(1, "little"))
            #Constitution
            if equipment_data[i]["Constitution"] < -0x7F:
                equipment_data[i]["Constitution"] = -0x7F
            if equipment_data[i]["Constitution"] > 0x80:
                equipment_data[i]["Constitution"] = 0x80
            if equipment_data[i]["Constitution"] < 0:
                equipment_data[i]["Constitution"] += 0x100
            self.file.seek(int(equipment_content[i]["Constitution"], 16))
            self.file.write(int(equipment_data[i]["Constitution"]).to_bytes(1, "little"))
            #Intelligence
            if equipment_data[i]["Intelligence"] < -0x7F:
                equipment_data[i]["Intelligence"] = -0x7F
            if equipment_data[i]["Intelligence"] > 0x80:
                equipment_data[i]["Intelligence"] = 0x80
            if equipment_data[i]["Intelligence"] < 0:
                equipment_data[i]["Intelligence"] += 0x100
            self.file.seek(int(equipment_content[i]["Intelligence"], 16))
            self.file.write(int(equipment_data[i]["Intelligence"]).to_bytes(1, "little"))
            #Luck
            if equipment_data[i]["Luck"] < -0x7F:
                equipment_data[i]["Luck"] = -0x7F
            if equipment_data[i]["Luck"] > 0x80:
                equipment_data[i]["Luck"] = 0x80
            if equipment_data[i]["Luck"] < 0:
                equipment_data[i]["Luck"] += 0x100
            self.file.seek(int(equipment_content[i]["Luck"], 16))
            self.file.write(int(equipment_data[i]["Luck"]).to_bytes(1, "little"))
            #Resistances
            weak = 0
            strong = 0
            immune = 0
            absorb = 0
            for e in Attributes:
                if equipment_data[i]["Resistances"][str(e).split(".")[1]] == 0:
                    weak += e.value
                elif equipment_data[i]["Resistances"][str(e).split(".")[1]] == 2:
                    strong += e.value
                elif equipment_data[i]["Resistances"][str(e).split(".")[1]] == 3:
                    immune += e.value
                elif equipment_data[i]["Resistances"][str(e).split(".")[1]] == 4:
                    absorb += e.value
            self.file.seek(int(equipment_content[i]["Resistances"]["Weak"], 16))
            self.file.write(weak.to_bytes(2, "little"))
            self.file.seek(int(equipment_content[i]["Resistances"]["Strong"], 16))
            self.file.write(strong.to_bytes(2, "little"))
            self.file.seek(int(equipment_content[i]["Resistances"]["Immune"], 16))
            self.file.write(immune.to_bytes(2, "little"))
            self.file.seek(int(equipment_content[i]["Resistances"]["Absorb"], 16))
            self.file.write(absorb.to_bytes(2, "little"))
    
    def write_item(self):
        for i in handitem_content:
            #Attack
            if handitem_data[i]["Attack"] < -0x7FFF:
                handitem_data[i]["Attack"] = -0x7FFF
            if handitem_data[i]["Attack"] > 0x8000:
                handitem_data[i]["Attack"] = 0x8000
            if handitem_data[i]["Attack"] < 0:
                handitem_data[i]["Attack"] += 0x10000
            self.file.seek(int(handitem_content[i]["Attack"], 16))
            self.file.write(int(handitem_data[i]["Attack"]).to_bytes(2, "little"))
            #Defense
            if handitem_data[i]["Defense"] < -0x7FFF:
                handitem_data[i]["Defense"] = -0x7FFF
            if handitem_data[i]["Defense"] > 0x8000:
                handitem_data[i]["Defense"] = 0x8000
            if handitem_data[i]["Defense"] < 0:
                handitem_data[i]["Defense"] += 0x10000
            self.file.seek(int(handitem_content[i]["Defense"], 16))
            self.file.write(int(handitem_data[i]["Defense"]).to_bytes(2, "little"))
            #Element
            total = 0
            for e in Attributes:
                if handitem_data[i]["Element"][str(e).split(".")[1]]:
                    total += e.value
            self.file.seek(int(handitem_content[i]["Element"], 16))
            self.file.write(total.to_bytes(2, "little"))
            #Sprite
            self.file.seek(int(handitem_content[i]["Sprite"], 16))
            self.file.write(int(handitem_data[i]["Sprite"], 16).to_bytes(1, "little"))
            #Special
            self.file.seek(int(handitem_content[i]["Special"], 16))
            self.file.write(int(handitem_data[i]["Special"], 16).to_bytes(1, "little"))
            #Spell
            self.file.seek(int(handitem_content[i]["Spell"], 16))
            self.file.write(int(handitem_data[i]["Spell"], 16).to_bytes(2, "little"))
            #ManaCost
            if handitem_data[i]["ManaCost"] < -0x7FFF:
                handitem_data[i]["ManaCost"] = -0x7FFF
            if handitem_data[i]["ManaCost"] > 0x8000:
                handitem_data[i]["ManaCost"] = 0x8000
            if handitem_data[i]["ManaCost"] < 0:
                handitem_data[i]["ManaCost"] += 0x10000
            self.file.seek(int(handitem_content[i]["ManaCost"], 16))
            self.file.write(int(handitem_data[i]["ManaCost"]).to_bytes(2, "little"))
            #StunFrames
            if handitem_data[i]["StunFrames"] < -0x7FFF:
                handitem_data[i]["StunFrames"] = -0x7FFF
            if handitem_data[i]["StunFrames"] > 0x8000:
                handitem_data[i]["StunFrames"] = 0x8000
            if handitem_data[i]["StunFrames"] < 0:
                handitem_data[i]["StunFrames"] += 0x10000
            self.file.seek(int(handitem_content[i]["StunFrames"], 16))
            self.file.write(int(handitem_data[i]["StunFrames"]).to_bytes(2, "little"))
            #Range
            if handitem_data[i]["Range"] < -0x7FFF:
                handitem_data[i]["Range"] = -0x7FFF
            if handitem_data[i]["Range"] > 0x8000:
                handitem_data[i]["Range"] = 0x8000
            if handitem_data[i]["Range"] < 0:
                handitem_data[i]["Range"] += 0x10000
            self.file.seek(int(handitem_content[i]["Range"], 16))
            self.file.write(int(handitem_data[i]["Range"]).to_bytes(2, "little"))
            #Extra
            self.file.seek(int(handitem_content[i]["Extra"], 16))
            self.file.write(int(handitem_data[i]["Extra"], 16).to_bytes(1, "little"))

    def write_shop(self):
        for i in shop_content:
            #Price
            if shop_data[i] < 0:
                shop_data[i] = 0
            if shop_data[i] > 0x80000000:
                shop_data[i] = 0x80000000
            self.file.seek(int(shop_content[i], 16))
            self.file.write(int(shop_data[i]).to_bytes(4, "little"))
    
    def write_spell(self):
        for i in spell_content:
            #ManaCost
            if spell_data[i]["ManaCost"] < -0x7F:
                spell_data[i]["ManaCost"] = -0x7F
            if spell_data[i]["ManaCost"] > 0x80:
                spell_data[i]["ManaCost"] = 0x80
            if spell_data[i]["ManaCost"] < 0:
                spell_data[i]["ManaCost"] += 0x100
            self.file.seek(int(spell_content[i]["ManaCost"], 16))
            self.file.write(int(spell_data[i]["ManaCost"]).to_bytes(1, "little"))
            #Element
            total = 0
            for e in Attributes:
                if spell_data[i]["Element"][str(e).split(".")[1]]:
                    total += e.value
            self.file.seek(int(spell_content[i]["Element"], 16))
            self.file.write(total.to_bytes(2, "little"))
            #Attack
            if spell_data[i]["Attack"] < -0x7FFF:
                spell_data[i]["Attack"] = -0x7FFF
            if spell_data[i]["Attack"] > 0x8000:
                spell_data[i]["Attack"] = 0x8000
            if spell_data[i]["Attack"] < 0:
                spell_data[i]["Attack"] += 0x10000
            self.file.seek(int(spell_content[i]["Attack"], 16))
            self.file.write(int(spell_data[i]["Attack"]).to_bytes(2, "little"))

    def write_stat(self):
        #StrConIntLck
        if stat_data["StrConIntLck"] < -0x7FFF:
            stat_data["StrConIntLck"] = -0x7FFF
        if stat_data["StrConIntLck"] > 0x8000:
            stat_data["StrConIntLck"] = 0x8000
        if stat_data["StrConIntLck"] < 0:
            stat_data["StrConIntLck"] += 0x10000
        self.file.seek(int(stat_content["StrConIntLck"], 16))
        self.file.write(int(stat_data["StrConIntLck"]).to_bytes(2, "little"))
        #Health
        if stat_data["Health"] < -0x7FFF:
            stat_data["Health"] = -0x7FFF
        if stat_data["Health"] > 0x8000 - 5:
            stat_data["Health"] = 0x8000 - 5
        if stat_data["Health"] < 0:
            stat_data["Health"] += 0x10000
        self.file.seek(int(stat_content["Health"], 16))
        self.file.write(int(stat_data["Health"]).to_bytes(2, "little"))
        #HealthFix
        self.file.seek(0x119CC4)
        self.file.write(int(stat_data["Health"] + 5).to_bytes(2, "little"))
        #Hearts
        if stat_data["Hearts"] < -0x7FFF:
            stat_data["Hearts"] = -0x7FFF
        if stat_data["Hearts"] > 0x8000:
            stat_data["Hearts"] = 0x8000
        if stat_data["Hearts"] < 0:
            stat_data["Hearts"] += 0x10000
        self.file.seek(int(stat_content["Hearts"], 16))
        self.file.write(int(stat_data["Hearts"]).to_bytes(2, "little"))
        #MaxHearts
        if stat_data["MaxHearts"] < -0x7FFF:
            stat_data["MaxHearts"] = -0x7FFF
        if stat_data["MaxHearts"] > 0x8000:
            stat_data["MaxHearts"] = 0x8000
        if stat_data["MaxHearts"] < 0:
            stat_data["MaxHearts"] += 0x10000
        self.file.seek(int(stat_content["MaxHearts"], 16))
        self.file.write(int(stat_data["MaxHearts"]).to_bytes(2, "little"))
        #Mana
        if stat_data["Mana"] < -0x7FFF:
            stat_data["Mana"] = -0x7FFF
        if stat_data["Mana"] > 0x8000:
            stat_data["Mana"] = 0x8000
        if stat_data["Mana"] < 0:
            stat_data["Mana"] += 0x10000
        self.file.seek(int(stat_content["Mana"], 16))
        self.file.write(int(stat_data["Mana"]).to_bytes(2, "little"))
    
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
        self.file.seek(0x4369E87)
        self.file.write(str.encode("KOJI  IGA"))
        self.file.seek(0x4369EE1)
        self.file.write(str.encode("KOJI  IGA"))
        self.file.seek(0x4369FBC)
        self.file.write(str.encode("KOJI  IGA"))
    
    def read_enemy(self):
        log = {}
        for i in enemy_content:
            log[i] = {}
            #Health
            self.file.seek(int(enemy_content[i]["Health"], 16))
            log[i]["Health"] = int.from_bytes(self.file.read(2), "little")
            #ContactDamage
            self.file.seek(int(enemy_content[i]["ContactDamage"], 16))
            log[i]["ContactDamage"] = int.from_bytes(self.file.read(2), "little")
            #ContactDamageType
            self.file.seek(int(enemy_content[i]["ContactDamageType"], 16))
            log[i]["ContactDamageType"] = "0x{:04x}".format(int.from_bytes(self.file.read(2), "little"))
            #Defense
            self.file.seek(int(enemy_content[i]["Defense"], 16))
            log[i]["Defense"] = int.from_bytes(self.file.read(2), "little")
            #Surface
            self.file.seek(int(enemy_content[i]["Surface"], 16))
            log[i]["Surface"] = "0x{:04x}".format(int.from_bytes(self.file.read(2), "little"))
            #Resistances
            log[i]["Resistances"] = {}
            for e in Attributes:
                log[i]["Resistances"][str(e).split(".")[1]] = 1
            self.file.seek(int(enemy_content[i]["Resistances"]["Weak"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 0
            self.file.seek(int(enemy_content[i]["Resistances"]["Strong"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 2
            self.file.seek(int(enemy_content[i]["Resistances"]["Immune"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 3
            self.file.seek(int(enemy_content[i]["Resistances"]["Absorb"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 4
            #Level
            self.file.seek(int(enemy_content[i]["Level"], 16))
            log[i]["Level"] = int.from_bytes(self.file.read(2), "little")
            #Experience
            self.file.seek(int(enemy_content[i]["Experience"], 16))
            log[i]["Experience"] = int.from_bytes(self.file.read(2), "little")
            #AttackDamage
            log[i]["AttackDamage"] = []
            for e in enemy_content[i]["AttackDamage"]:
                self.file.seek(int(e, 16))
                log[i]["AttackDamage"].append(int.from_bytes(self.file.read(2), "little"))
            #AttackDamageType
            log[i]["AttackDamageType"] = []
            for e in enemy_content[i]["AttackDamageType"]:
                self.file.seek(int(e, 16))
                log[i]["AttackDamageType"].append("0x{:04x}".format(int.from_bytes(self.file.read(2), "little")))
        
        with open("SpoilerLog\\Enemy.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def read_equip(self):
        log = {}
        for i in equipment_content:
            log[i] = {}
            #Attack
            self.file.seek(int(equipment_content[i]["Attack"], 16))
            log[i]["Attack"] = int.from_bytes(self.file.read(2), "little")
            if log[i]["Attack"] > 0x8000:
                log[i]["Attack"] = log[i]["Attack"] - 0x10000
            #Defense
            self.file.seek(int(equipment_content[i]["Defense"], 16))
            log[i]["Defense"] = int.from_bytes(self.file.read(2), "little")
            if log[i]["Defense"] > 0x8000:
                log[i]["Defense"] = log[i]["Defense"] - 0x10000
            #Strength
            self.file.seek(int(equipment_content[i]["Strength"], 16))
            log[i]["Strength"] = int.from_bytes(self.file.read(1), "little")
            if log[i]["Strength"] > 0x80:
                log[i]["Strength"] = log[i]["Strength"] - 0x100
            #Constitution
            self.file.seek(int(equipment_content[i]["Constitution"], 16))
            log[i]["Constitution"] = int.from_bytes(self.file.read(1), "little")
            if log[i]["Constitution"] > 0x80:
                log[i]["Constitution"] = log[i]["Constitution"] - 0x100
            #Intelligence
            self.file.seek(int(equipment_content[i]["Intelligence"], 16))
            log[i]["Intelligence"] = int.from_bytes(self.file.read(1), "little")
            if log[i]["Intelligence"] > 0x80:
                log[i]["Intelligence"] = log[i]["Intelligence"] - 0x100
            #Luck
            self.file.seek(int(equipment_content[i]["Luck"], 16))
            log[i]["Luck"] = int.from_bytes(self.file.read(1), "little")
            if log[i]["Luck"] > 0x80:
                log[i]["Luck"] = log[i]["Luck"] - 0x100
            #Resistances
            log[i]["Resistances"] = {}
            for e in Attributes:
                log[i]["Resistances"][str(e).split(".")[1]] = 1
            self.file.seek(int(equipment_content[i]["Resistances"]["Weak"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 0
            self.file.seek(int(equipment_content[i]["Resistances"]["Strong"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 2
            self.file.seek(int(equipment_content[i]["Resistances"]["Immune"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 3
            self.file.seek(int(equipment_content[i]["Resistances"]["Absorb"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Resistances"][str(e).split(".")[1]] = 4
        
        with open("SpoilerLog\\Equipment.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def read_item(self):
        log = {}
        for i in handitem_content:
            log[i] = {}
            #Attack
            self.file.seek(int(handitem_content[i]["Attack"], 16))
            log[i]["Attack"] = int.from_bytes(self.file.read(2), "little")
            if log[i]["Attack"] > 0x8000:
                log[i]["Attack"] = log[i]["Attack"] - 0x10000
            #Defense
            self.file.seek(int(handitem_content[i]["Defense"], 16))
            log[i]["Defense"] = int.from_bytes(self.file.read(2), "little")
            if log[i]["Defense"] > 0x8000:
                log[i]["Defense"] = log[i]["Defense"] - 0x10000
            #Element
            log[i]["Element"] = {}
            for e in Attributes:
                log[i]["Element"][str(e).split(".")[1]] = False
            self.file.seek(int(handitem_content[i]["Element"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Element"][str(e).split(".")[1]] = True
            #Sprite
            self.file.seek(int(handitem_content[i]["Sprite"], 16))
            log[i]["Sprite"] = "0x{:02x}".format(int.from_bytes(self.file.read(1), "little"))
            #Special
            self.file.seek(int(handitem_content[i]["Special"], 16))
            log[i]["Special"] = "0x{:02x}".format(int.from_bytes(self.file.read(1), "little"))
            #Spell
            self.file.seek(int(handitem_content[i]["Spell"], 16))
            log[i]["Spell"] = "0x{:04x}".format(int.from_bytes(self.file.read(2), "little"))
            #ManaCost
            self.file.seek(int(handitem_content[i]["ManaCost"], 16))
            log[i]["ManaCost"] = int.from_bytes(self.file.read(2), "little")
            #StunFrames
            self.file.seek(int(handitem_content[i]["StunFrames"], 16))
            log[i]["StunFrames"] = int.from_bytes(self.file.read(2), "little")
            #Range
            self.file.seek(int(handitem_content[i]["Range"], 16))
            log[i]["Range"] = int.from_bytes(self.file.read(2), "little")
            #Extra
            self.file.seek(int(handitem_content[i]["Extra"], 16))
            log[i]["Extra"] = "0x{:02x}".format(int.from_bytes(self.file.read(1), "little"))
        
        with open("SpoilerLog\\HandItem.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def read_shop(self):
        log = {}
        for i in shop_content:
            log[i] = {}
            #Price
            self.file.seek(int(shop_content[i]["Price"], 16))
            log[i]["Price"] = int.from_bytes(self.file.read(4), "little")
        
        with open("SpoilerLog\\Shop.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def read_spell(self):
        log = {}
        for i in spell_content:
            log[i] = {}
            #ManaCost
            self.file.seek(int(spell_content[i]["ManaCost"], 16))
            log[i]["ManaCost"] = int.from_bytes(self.file.read(1), "little")
            #Element
            log[i]["Element"] = {}
            for e in Attributes:
                log[i]["Element"][str(e).split(".")[1]] = False
            self.file.seek(int(spell_content[i]["Element"], 16))
            total = int.from_bytes(self.file.read(2), "little")
            for e in Attributes:
                if (total & e.value) != 0:
                    log[i]["Element"][str(e).split(".")[1]] = True
            #Attack
            self.file.seek(int(spell_content[i]["Attack"], 16))
            log[i]["Attack"] = int.from_bytes(self.file.read(2), "little")
        
        with open("SpoilerLog\\Spell.json", "w") as file_writer:
            file_writer.write(json.dumps(log, indent=2))
    
    def read_stat(self):
        log = {}
        #StrConIntLck
        self.file.seek(int(stat_content["StrConIntLck"], 16))
        log["StrConIntLck"] = int.from_bytes(self.file.read(2), "little")
        #Health
        self.file.seek(int(stat_content["Health"], 16))
        log["Health"] = int.from_bytes(self.file.read(2), "little")
        #Hearts
        self.file.seek(int(stat_content["Hearts"], 16))
        log["Hearts"] = int.from_bytes(self.file.read(2), "little")
        #MaxHearts
        self.file.seek(int(stat_content["MaxHearts"], 16))
        log["MaxHearts"] = int.from_bytes(self.file.read(2), "little")
        #Mana
        self.file.seek(int(stat_content["Mana"], 16))
        log["Mana"] = int.from_bytes(self.file.read(2), "little")
        
        with open("SpoilerLog\\Stat.json", "w") as file_writer:
            file_writer.write(json.dumps(entry, indent=2))
    
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