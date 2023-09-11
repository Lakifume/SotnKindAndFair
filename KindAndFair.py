import Manager
import Symphony
import Dissonance

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import json
import configparser
import sys
import random
import os
import shutil
import requests
import zipfile
import subprocess
import glob

#Get script name

script_name, script_extension = os.path.splitext(os.path.basename(__file__))

#Config

config = configparser.ConfigParser()
config.optionxform = str
config.read("Data\\config.ini")

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
        
        #Determine game
        if config.getboolean("Game", "bSymphony"):
            Manager.init(Symphony)
            folder = "Data\\Symphony\\ErrorRecalc"
            short_name = "Sotn"
        else:
            Manager.init(Dissonance)
            folder = "Data\\Dissonance"
            short_name = "Hod"
        
        shutil.copyfile(config.get("Misc", "s" + short_name + "InputFile"), folder + "\\rom")
        
        Manager.game.init()
        Manager.game.open_json()
        
        Manager.set_enemy_level_wheight(config.getint("EnemyRandomization", "iEnemyLevelsWheight"))
        Manager.set_enemy_tolerance_wheight(config.getint("EnemyRandomization", "iEnemyTolerancesWheight"))
        
        Manager.open_rom(folder + "\\rom")
        
        seed = Manager.game.get_seed()
        
        if Manager.game == Dissonance:
            #Apply patches first
            for i in os.listdir("Data\\Dissonance\\Patches"):
                name, extension = os.path.splitext(i)
                if name in ["InvisiblePazuzuWall", "NoPlayerOutline"]:
                    continue
                Manager.game.apply_ips_patch(name)
            if config.getboolean("Extra", "bNoPlayerOutline"):
                Manager.game.apply_ips_patch("NoPlayerOutline")
            #Randomize after
            Manager.game.read_room_data()
            Manager.game.gather_data()
            if config.getboolean("EnemyRandomization", "bEnemyPlacement"):
                random.seed(seed)
                Manager.game.randomize_enemies()
                random.seed(seed)
                Manager.game.randomize_bosses()
                Manager.game.rebalance_enemies()
                Manager.game.update_gfx_pointers()
        else:
            #Apply patches first
            for i in os.listdir("Data\\Symphony\\Patches"):
                name, extension = os.path.splitext(i)
                Manager.game.apply_ppf_patch(name)
            #Randomize after
            if config.getboolean("EnemyRandomization", "bEnemyLevels"):
                random.seed(seed)
                Manager.randomize_enemy_levels()
                Manager.game.keep_equipment()
            if config.getboolean("EnemyRandomization", "bEnemyLevels") or config.getboolean("EnemyRandomization", "bEnemyTolerances"):
                random.seed(seed)
                Manager.game.free_library()
            if config.getboolean("Extra", "bContinuousSmash"):
                Manager.game.infinite_wing_smash()
        
        if config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            random.seed(seed)
            Manager.randomize_enemy_resistances()
        
        Manager.multiply_damage(config.getfloat("EnemyDamage", "fDamageMultiplier"))
        
        if config.getboolean("Extra", "bScavengerMode"):
            Manager.game.remove_enemy_drops()
        if config.getboolean("Extra", "bBigtossOnly"):
            Manager.game.all_bigtoss()
        
        if Manager.game == Dissonance:
            Manager.game.write_room_data()
        Manager.game.write_simple_data()
        Manager.game.write_complex_data()
        Manager.game.create_enemy_log()
        
        Manager.close_rom()
        
        if Manager.game == Symphony:
            root = os.getcwd()
            os.chdir(folder)
            program = glob.glob("*.exe")[0]
            os.system("cmd /c " + program + " rom")
            os.chdir(root)
        
        self.signaller.progress.emit(1)
        
        if config.get("Misc", "s" + short_name + "OutputFolder") and os.path.isdir(config.get("Misc", "s" + short_name + "OutputFolder")):
            shutil.move(folder + "\\rom", config.get("Misc", "s" + short_name + "OutputFolder") + "\\" + config.get("Misc", "s" + short_name + "InputFile").split("\\")[-1])
        else:
            shutil.move(folder + "\\rom", config.get("Misc", "s" + short_name + "InputFile"))
        
        self.signaller.finished.emit()

class Update(QThread):
    def __init__(self, progressBar, api):
        QThread.__init__(self)
        self.signaller = Signaller()
        self.progressBar = progressBar
        self.api = api

    def run(self):
        progress = 0
        zip_name = "KindAndFair.zip"
        exe_name = script_name + ".exe"
        self.signaller.progress.emit(progress)
        
        #Download
        
        with open(zip_name, "wb") as file_writer:
            url = requests.get(self.api["assets"][0]["browser_download_url"], stream=True)
            for data in url.iter_content(chunk_size=4096):
                file_writer.write(data)
                progress += len(data)
                self.signaller.progress.emit(progress)
        
        self.progressBar.setLabelText("Extracting...")
        
        #Purge folders
        
        shutil.rmtree("Data")
        shutil.rmtree("Shaders")
        
        os.rename(exe_name, "delete.me")
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall("")
        os.remove(zip_name)
        
        #Carry previous config
        
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
        
        #Exit
        
        subprocess.Popen(exe_name)
        self.signaller.finished.emit()

#Interface

class DropFile(QObject):    
    def eventFilter(self, watched, event):
        if config.getboolean("Game", "bSymphony"):
            format = ".bin"
        else:
            format = ".gba"
        if event.type() == QEvent.DragEnter:
            md = event.mimeData()
            if md.hasUrls():
                if len(md.urls()) == 1:
                    if format in md.urls()[0].toLocalFile():
                        event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            watched.setText(md.urls()[0].toLocalFile().replace("/", "\\"))
            return True
        return super().eventFilter(watched, event)

class DropFolder(QObject):    
    def eventFilter(self, watched, event):
        if event.type() == QEvent.DragEnter:
            md = event.mimeData()
            if md.hasUrls():
                if len(md.urls()) == 1:
                    if not "." in md.urls()[0].toLocalFile():
                        event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            watched.setText(md.urls()[0].toLocalFile().replace("/", "\\"))
            return True
        return super().eventFilter(watched, event)

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setEnabled(False)
        self.initUI()
        self.check_for_updates()

    def initUI(self):
        
        #Main layout
        
        grid = QGridLayout()
        grid.setSpacing(10)

        #Groupboxes

        box_1_grid = QGridLayout()
        self.box_1 = QGroupBox("Enemy Randomization")
        self.box_1.setLayout(box_1_grid)
        grid.addWidget(self.box_1, 0, 0, 1, 2)

        box_2_grid = QGridLayout()
        self.box_2 = QGroupBox("Enemy Damage")
        self.box_2.setLayout(box_2_grid)
        grid.addWidget(self.box_2, 0, 2, 1, 2)

        box_4_grid = QGridLayout()
        self.box_4 = QGroupBox("Extra")
        self.box_4.setLayout(box_4_grid)
        grid.addWidget(self.box_4, 2, 0, 1, 4)

        box_7_grid = QGridLayout()
        self.box_7 = QGroupBox("Game")
        self.box_7.setLayout(box_7_grid)
        grid.addWidget(self.box_7, 3, 0, 1, 4)
        
        #Checkboxes

        self.check_box_1 = QCheckBox("Enemy Levels")
        self.check_box_1.setToolTip("Randomize the level of every enemy. Stats that scale with\nlevel include HP, attack, defense and EXP.\nPicking this option will disable the removal of your\nstarting equipment from Death's cutscene.")
        self.check_box_1.stateChanged.connect(self.check_box_1_changed)
        box_1_grid.addWidget(self.check_box_1, 0, 0)
        
        self.check_box_2 = QCheckBox("Enemy Tolerances")
        self.check_box_2.setToolTip("Randomize the resistance/weakness attributes of enemies.")
        self.check_box_2.stateChanged.connect(self.check_box_2_changed)
        box_1_grid.addWidget(self.check_box_2, 1, 0)
        
        self.check_box_3 = QCheckBox("Enemy Placement")
        self.check_box_3.setToolTip("Randomize where enemies are found. Their stats\nwill be rescaled to the order you encounter them.")
        self.check_box_3.stateChanged.connect(self.check_box_3_changed)
        box_1_grid.addWidget(self.check_box_3, 0, 0)
        
        self.check_box_7 = QCheckBox("Scavenger Mode")
        self.check_box_7.setToolTip("Enemies no longer drop items, you will have\nto rely on what you find in the overworld.")
        self.check_box_7.stateChanged.connect(self.check_box_7_changed)
        box_4_grid.addWidget(self.check_box_7, 0, 0)
        
        self.check_box_6 = QCheckBox("Continuous Wing Smash")
        self.check_box_6.setToolTip("Wing smashes will cost more MP to initially cast\nbut will no longer need to be chained.")
        self.check_box_6.stateChanged.connect(self.check_box_6_changed)
        box_4_grid.addWidget(self.check_box_6, 0, 1)
        
        self.check_box_5 = QCheckBox("Bigtoss Only")
        self.check_box_5.setToolTip("Getting hit will always cause extreme knockback.")
        self.check_box_5.stateChanged.connect(self.check_box_5_changed)
        box_4_grid.addWidget(self.check_box_5, 1, 0)
        
        self.check_box_4 = QCheckBox("No Player Outline")
        self.check_box_4.setToolTip("Remove all colored outlines from player characters\nand replace their trail by a dark shade of grey.")
        self.check_box_4.stateChanged.connect(self.check_box_4_changed)
        box_4_grid.addWidget(self.check_box_4, 0, 1)
        
        #SpinButtons
        
        self.spin_button_1 = QPushButton()
        self.spin_button_1.setToolTip("Level wheight. The higher the value the more extreme\nthe level differences.")
        self.spin_button_1.setStyleSheet("QPushButton{color: #ffffff; font-family: Impact}" + "QToolTip{color: #ffffff; font-family: Cambria}")
        self.spin_button_1.setFixedSize(28, 24)
        self.spin_button_1.clicked.connect(self.spin_button_1_clicked)
        self.spin_button_1.setVisible(False)
        box_1_grid.addWidget(self.spin_button_1, 0, 1)
        
        self.spin_button_2 = QPushButton()
        self.spin_button_2.setToolTip("Tolerance wheight. The higher the value the more extreme\nthe tolerance differences.")
        self.spin_button_2.setStyleSheet("QPushButton{color: #ffffff; font-family: Impact}" + "QToolTip{color: #ffffff; font-family: Cambria}")
        self.spin_button_2.setFixedSize(28, 24)
        self.spin_button_2.clicked.connect(self.spin_button_2_clicked)
        self.spin_button_2.setVisible(False)
        box_1_grid.addWidget(self.spin_button_2, 1, 1)
        
        #Radio buttons
        
        self.radio_button_1 = QRadioButton("Symphony of the Night")
        self.radio_button_1.toggled.connect(self.radio_button_group_1_checked)
        box_7_grid.addWidget(self.radio_button_1, 0, 0)
        
        self.radio_button_2 = QRadioButton("Harmony of Dissonance")
        self.radio_button_2.toggled.connect(self.radio_button_group_1_checked)
        box_7_grid.addWidget(self.radio_button_2, 1, 0)
        
        #SpinBoxes
        
        if config.getfloat("EnemyDamage", "fDamageMultiplier") < 0.0:
            config.set("EnemyDamage", "fDamageMultiplier", "0.0")
        if config.getfloat("EnemyDamage", "fDamageMultiplier") > 3.0:
            config.set("EnemyDamage", "fDamageMultiplier", "3.0")
        
        self.damage_box = QDoubleSpinBox()
        self.damage_box.setToolTip("Multiplier of damage received.\n(1.0 is beginner)")
        self.damage_box.setDecimals(1)
        self.damage_box.setRange(0.1, 3.0)
        self.damage_box.setSingleStep(0.1)
        self.damage_box.setValue(config.getfloat("EnemyDamage", "fDamageMultiplier"))
        self.damage_box.valueChanged.connect(self.new_damage)
        box_2_grid.addWidget(self.damage_box, 0, 0)
        
        #Init checkboxes
        
        if config.getboolean("EnemyRandomization", "bEnemyLevels"):
            self.check_box_1.setChecked(True)
        if config.getboolean("EnemyRandomization", "bEnemyTolerances"):
            self.check_box_2.setChecked(True)
        if config.getboolean("EnemyRandomization", "bEnemyPlacement"):
            self.check_box_3.setChecked(True)
        if config.getboolean("Extra", "bScavengerMode"):
            self.check_box_7.setChecked(True)
        if config.getboolean("Extra", "bContinuousSmash"):
            self.check_box_6.setChecked(True)
        if config.getboolean("Extra", "bBigtossOnly"):
            self.check_box_5.setChecked(True)
        if config.getboolean("Extra", "bNoPlayerOutline"):
            self.check_box_4.setChecked(True)
        
        #Text field

        self.input_field = QLineEdit()
        self.input_field.setToolTip("Path to your input rom.")
        self.input_field.textChanged[str].connect(self.new_input)
        self.input_field.installEventFilter(DropFile(self))
        grid.addWidget(self.input_field, 4, 0, 1, 1)
        
        self.output_field = QLineEdit()
        self.output_field.setToolTip("Path to your output folder.")
        self.output_field.textChanged[str].connect(self.new_output)
        self.output_field.installEventFilter(DropFolder(self))
        grid.addWidget(self.output_field, 4, 2, 1, 1)

        #Buttons
        
        button_1 = QPushButton("Patch")
        button_1.setToolTip("Patch rom with current settings.")
        button_1.clicked.connect(self.button_1_clicked)
        grid.addWidget(button_1, 5, 0, 1, 4)
        
        button_2 = QPushButton()
        button_2.setIcon(QPixmap("Data\\browse.png"))
        button_2.setToolTip("Browse input.")
        button_2.clicked.connect(self.button_2_clicked)
        grid.addWidget(button_2, 4, 1, 1, 1)
        
        button_3 = QPushButton()
        button_3.setIcon(QPixmap("Data\\browse.png"))
        button_3.setToolTip("Browse output.")
        button_3.clicked.connect(self.button_3_clicked)
        grid.addWidget(button_3, 4, 3, 1, 1)
        
        #Window
        
        self.setLayout(grid)
        self.setFixedSize(512, 432)
        self.setWindowTitle(script_name)
        self.show()
        
        if config.getboolean("Game", "bSymphony"):
            self.radio_button_1.setChecked(True)
        else:
            self.radio_button_2.setChecked(True)
        
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
        self.spin_button_1.setVisible(self.check_box_1.isChecked())

    def check_box_2_changed(self):
        if self.check_box_2.isChecked():
            config.set("EnemyRandomization", "bEnemyTolerances", "true")
        else:
            config.set("EnemyRandomization", "bEnemyTolerances", "false")
        self.spin_button_2.setVisible(self.check_box_2.isChecked())

    def check_box_3_changed(self):
        if self.check_box_3.isChecked():
            config.set("EnemyRandomization", "bEnemyPlacement", "true")
        else:
            config.set("EnemyRandomization", "bEnemyPlacement", "false")

    def check_box_7_changed(self):
        if self.check_box_7.isChecked():
            config.set("Extra", "bScavengerMode", "true")
        else:
            config.set("Extra", "bScavengerMode", "false")

    def check_box_6_changed(self):
        if self.check_box_6.isChecked():
            config.set("Extra", "bContinuousSmash", "true")
        else:
            config.set("Extra", "bContinuousSmash", "false")

    def check_box_5_changed(self):
        if self.check_box_5.isChecked():
            config.set("Extra", "bBigtossOnly", "true")
        else:
            config.set("Extra", "bBigtossOnly", "false")

    def check_box_4_changed(self):
        if self.check_box_4.isChecked():
            config.set("Extra", "bNoPlayerOutline", "true")
        else:
            config.set("Extra", "bNoPlayerOutline", "false")

    def spin_button_1_clicked(self):
        index = int(self.spin_button_1.text())
        index = index % 3 + 1
        index = str(index)
        self.spin_button_1.setText(index)
        config.set("EnemyRandomization", "iEnemyLevelsWheight", index)

    def spin_button_2_clicked(self):
        index = int(self.spin_button_2.text())
        index = index % 3 + 1
        index = str(index)
        self.spin_button_2.setText(index)
        config.set("EnemyRandomization", "iEnemyTolerancesWheight", index)
    
    def radio_button_group_1_checked(self):
        if self.radio_button_1.isChecked():
            config.set("Game", "bSymphony", "true")
            config.set("Game", "bDissonance", "false")
            self.check_box_1.setVisible(True)
            self.check_box_3.setVisible(False)
            self.check_box_6.setVisible(True)
            self.check_box_4.setVisible(False)
            self.spin_button_1.setVisible(self.check_box_1.isChecked())
            self.input_field.setText(config.get("Misc", "sSotnInputFile"))
            self.output_field.setText(config.get("Misc", "sSotnOutputFolder"))
            self.reset_visuals("Symphony", "#1d150f")
        else:
            config.set("Game", "bSymphony", "false")
            config.set("Game", "bDissonance", "true")
            self.check_box_1.setVisible(False)
            self.check_box_3.setVisible(True)
            self.check_box_6.setVisible(False)
            self.check_box_4.setVisible(True)
            self.spin_button_1.setVisible(False)
            self.input_field.setText(config.get("Misc", "sHodInputFile"))
            self.output_field.setText(config.get("Misc", "sHodOutputFolder"))
            self.reset_visuals("Dissonance", "#340d0d")
    
    def reset_visuals(self, game, color):
        self.setStyleSheet("QWidget{background:transparent; color: #ffffff; font-family: Cambria; font-size: 18px}"
        + "QLabel{border: 1px}"
        + "QMessageBox{background-color: " + color + "}"
        + "QDialog{background-color: " + color + "}"
        + "QProgressDialog{background-color: " + color + "}"
        + "QPushButton{background-color: " + color + "}"
        + "QDoubleSpinBox{background-color: " + color + "}"
        + "QLineEdit{background-color: " + color + "}"
        + "QMenu{background-color: " + color + "}"
        + "QToolTip{border: 0px; background-color: " + color + "; color: #ffffff; font-family: Cambria; font-size: 18px}")
        self.setWindowIcon(QIcon("Data\\" + game + "\\icon.png"))
        background = QPixmap("Data\\" + game + "\\background.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, background)
        self.setPalette(palette)
    
    def new_damage(self):
        config.set("EnemyDamage", "fDamageMultiplier", str(round(self.damage_box.value(),1)))
    
    def new_input(self, input):
        if config.getboolean("Game", "bSymphony"):
            config.set("Misc", "sSotnInputFile", input)
        else:
            config.set("Misc", "sHodInputFile", input)
    
    def new_output(self, output):
        if config.getboolean("Game", "bSymphony"):
            config.set("Misc", "sSotnOutputFolder", output)
        else:
            config.set("Misc", "sHodOutputFolder", output)
    
    def set_progress(self, progress):
        self.progressBar.setValue(progress)
    
    def patch_finished(self):
        box = QMessageBox(self)
        box.setWindowTitle("Done")
        box.setText("Rom patched !")
        box.exec()
        self.setEnabled(True)
    
    def update_finished(self):
        sys.exit()

    def button_1_clicked(self):
        self.setEnabled(False)
        QApplication.processEvents()
        
        if config.getboolean("Game", "bSymphony"):
            name, extension = os.path.splitext(config.get("Misc", "sSotnInputFile"))
            if not os.path.isfile(config.get("Misc", "sSotnInputFile")) or extension != ".bin":
                self.no_path()
                self.setEnabled(True)
                return
        else:
            name, extension = os.path.splitext(config.get("Misc", "sHodInputFile"))
            if not os.path.isfile(config.get("Misc", "sHodInputFile")) or extension != ".gba":
                self.no_path()
                self.setEnabled(True)
                return
        
        if not os.path.isdir("SpoilerLog"):
            os.makedirs("SpoilerLog")
        
        self.progressBar = QProgressDialog("Patching...", None, 0, 1, self)
        self.progressBar.setWindowTitle("Status")
        self.progressBar.setWindowModality(Qt.WindowModal)
        
        self.worker = Patch()
        self.worker.signaller.progress.connect(self.set_progress)
        self.worker.signaller.finished.connect(self.patch_finished)
        self.worker.start()
    
    def button_2_clicked(self):
        if config.getboolean("Game", "bSymphony"):
            format = "*.bin"
        else:
            format = "*.gba"
        file = QFileDialog.getOpenFileName(parent=self, caption="File", filter=format)[0]
        if file:
            self.input_field.setText(file.replace("/", "\\"))
    
    def button_3_clicked(self):
        path = QFileDialog.getExistingDirectory(self, "Folder")
        if path:
            self.output_field.setText(path.replace("/", "\\"))
    
    def no_path(self):
        box = QMessageBox(self)
        box.setWindowTitle("Path")
        box.setIcon(QMessageBox.Critical)
        box.setText("Input path invalid.")
        box.exec()
    
    def check_for_updates(self):
        if os.path.isfile("delete.me"):
            os.remove("delete.me")
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
                self.worker.signaller.finished.connect(self.update_finished)
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