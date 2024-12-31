import sys
import os
import shutil
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QWidget,QLabel,QDialog, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QToolBar, QPushButton, QFileDialog
from PySide6.QtGui import QPalette, QColor, QAction
from app_logic import AppLogic

import helper

file_opened = False

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Get the directory where the current script is located
        self.project_directory = os.path.dirname(os.path.abspath(__file__))

        self.current_project = ""

        self.setWindowTitle("Midi Visualizer")
        self.resize(1280,720)

        # making a menu bar
        menu = self.menuBar()

        # making an option in the menu bar
        file_menu = menu.addMenu("&File")
        file_menu.addSeparator()
        
        # menu bar actions
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)

        # add open action to file option in menu bar
        file_menu.addAction(open_action)
       

        # Layout stuff
        self.main_window = QHBoxLayout()
        self.preview_panel = QVBoxLayout()
        #----------------------------------------------------

        ''' 
        scroll area -> instrument scroll container widget -> instrument panel
        '''
        self.instrument_scroll_container = QWidget()

        self.instruments_panel = QVBoxLayout(self.instrument_scroll_container)
        print(self.instrument_scroll_container.layout())
        # set allignment to top down 
        self.instruments_panel.setAlignment(Qt.AlignTop) 
        
        # parent area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.instrument_scroll_container.setLayout(self.instruments_panel)

        self.scroll_area.setWidget(self.instrument_scroll_container)
        

        # the other layouts in preview panel
        self.preview_layout = QVBoxLayout()
        self.control_layout = QHBoxLayout()
        

        self.bg_colour_button=QPushButton("bg colour")
    
        self.control_layout.addWidget(self.bg_colour_button)

        self.generate_button = QPushButton("generate")
        
        self.control_layout.addWidget(self.generate_button)
        self.preview_panel.addLayout(self.preview_layout)
        self.preview_panel.addLayout(self.control_layout)

        self.preview_layout.addWidget(Color('red'))

        self.preview_panel.addLayout(self.preview_layout)
        
        self.preview_panel.addLayout(self.control_layout)
        # self.preview_panel.setLayout(self.preview_panel)

        # self.instruments_panel.addWidget(Color('blue'))
        
        # self.main_window.addLayout(self.instruments_panel)
        self.main_window.addWidget(self.scroll_area)
        self.main_window.addLayout(self.preview_panel)

        self.widget = QWidget()
        self.widget.setLayout(self.main_window)
        self.setCentralWidget(self.widget)

    '''
    When we open a new file we are essentially starting the project so lots of things are in
    here

    I want to change where the Applogic is stored. Its connected to the mainwindow which i think is limitting.
    '''
    def open_file_dialog(self):
        '''File things'''
        # ", _" means to disregard the second item in the tuple
        source_file, _ = QFileDialog.getOpenFileName(self, "Open File")
        save_folder = "midi"
        project_directory = self.project_directory

        # get the file name without the directory paths
        file_basename = os.path.basename(source_file)
        destination_path = os.path.join(project_directory,save_folder)
        destination_path = os.path.join(destination_path, file_basename)


        print(source_file)
        print(destination_path)
        shutil.move(source_file, destination_path) #Moving the file to database

        
        if self.current_project == "":
            self.current_project = AppLogic(destination_path)
        else:
            self.current_project.merge_midi(destination_path)
            self.generate_button.clicked.disconnect()
        self.current_project.process_midi()
        
        '''
        ADDING instrument widgets to instrument_panel
        '''
        for instr in self.current_project.instruments:
            # self.instruments_panel.addLayout(QVBoxLayout())
            self.instruments_panel.addWidget(Instrument(instr.name, instr, self.current_project))


        '''Colour things'''
        # connect generate button to app logic generate code
        self.generate_button.clicked.connect(self.current_project.generate_vid)
        
        # setting the instrument scroll container colour!!
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(*self.current_project.colour))  #  grey background
        # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
        self.instrument_scroll_container.setPalette(palette)

        self.bg_colour_widget = Colour_Widget(self.current_project)
        self.bg_colour_button.clicked.connect(lambda: self.bg_colour_widget.show_colour_widget(self.instrument_scroll_container))
        
        # self.scroll_area.setWidget(self.instrument_scroll_container)
        
        file_opened = True
        # self.current_project.generate_vid()
        # self.instruments_panel.update()    
        # self.setLayout(self.instruments_panel)
            # self.instruments_panel.addWidget(Color('red'))
'''
instrument_wrapper <- Name label widget + button_wrapper

'''
class Instrument(QWidget):
    def __init__(self, name, instrument, current_project):
        super().__init__()
        
        self.instrument = instrument
        self.current_project = current_project
        # Setting Background Colour
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(*instrument.colour))  #  grey background

        # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
        self.setPalette(palette)

        

        # initialize speed_slider for instrument
        self.speed_slider = Speed_Slider(self.instrument)

        # initialize colour_widget for instrument
        self.colour_widget = Colour_Widget(self.instrument)

        self.instrument_wrapper = QVBoxLayout()
        

        # the label for the instrument name        
        self.name_label = QLabel(f"{name.strip()}")
        self.instrument_wrapper.addWidget(self.name_label)

        # wrapper for all the buttons and aligning them to the left
        self.button_wrapper = QHBoxLayout()
        self.button_wrapper.setAlignment(Qt.AlignLeft)

        '''
        Make a class for buttons
        '''

        # colour button
        self.colour_button = QPushButton("colour")
        self.colour_button.setFixedWidth(70)
        self.colour_button.clicked.connect(lambda: self.colour_widget.show_colour_widget(self))
        
        self.button_wrapper.addWidget(self.colour_button)
        # speed button
        self.speed_button = QPushButton("speed")
        self.speed_button.setMinimumWidth(70)
        self.speed_button.setMaximumWidth(120)
        self.speed_button.clicked.connect(lambda: self.speed_slider.show_slider(self.speed_button)) # another lambda function
        self.button_wrapper.addWidget(self.speed_button)




        # add button wrapper to instrument wrapper
        self.instrument_wrapper.addLayout(self.button_wrapper)
        self.setLayout(self.instrument_wrapper)
        self.setFixedHeight(60)
        
    def mousePressEvent(self, event):
        # Check if the left mouse button was clicked
        if event.button() == Qt.RightButton:
            self.instrument_right_click_menu(event)

    def instrument_right_click_menu(self, event):
        instrument_menu = QMenu()
        move_up = QAction("Move Up", self)
        move_down = QAction("Move Down", self)
        delete = QAction("Delete", self)

        # Connect actions to functions
        move_up.triggered.connect(lambda: self.move_up())
        move_down.triggered.connect(lambda: self.move_down() )
        delete.triggered.connect(lambda: self.delete())
        instrument_menu.addAction(move_up)
        instrument_menu.addAction(move_down)
        instrument_menu.addAction(delete)
        instrument_menu.exec(event.globalPos())
        pass
    


    def move_up(self):
        parent_widget = self.parentWidget()
        parent_layout = parent_widget.layout()
        current_instrument_index = parent_layout.indexOf(self)

        if current_instrument_index > 0:
            widget_above = parent_layout.itemAt(current_instrument_index-1).widget()

            # Remove both widgets temporarily
            parent_layout.removeWidget(self)
            parent_layout.removeWidget(widget_above)
            
            parent_layout.insertWidget(current_instrument_index-1, self) 
            parent_layout.insertWidget(current_instrument_index, widget_above) 
           

            #---------------- the other stuff
            instrument_above = self.current_project.instruments[current_instrument_index-1] 
            self.current_project.instruments[current_instrument_index-1] = self.current_project.instruments[current_instrument_index]
            self.current_project.instruments[current_instrument_index] = instrument_above

            # helper.instrument_move_up(current_instrument_index)
        else:
            print("can't move up")



        
    
    
    def move_down(self):
        parent_widget = self.parentWidget()
        parent_layout = parent_widget.layout()
        current_instrument_index = parent_layout.indexOf(self)

        if current_instrument_index < parent_layout.count()-1:
            widget_below = parent_layout.itemAt(current_instrument_index+1).widget()

            # Remove both widgets temporarily
            parent_layout.removeWidget(self)
            parent_layout.removeWidget(widget_below)
            
            parent_layout.insertWidget(current_instrument_index, widget_below)
            parent_layout.insertWidget(current_instrument_index+1, self)


            # helper.instrument_move_down(current_instrument_index)

               #---------------- changing the app_logic insturments
            instrument_below = self.current_project.instruments[current_instrument_index+1] 
            self.current_project.instruments[current_instrument_index+1] = self.current_project.instruments[current_instrument_index]
            self.current_project.instruments[current_instrument_index] = instrument_below


        else:
            print("can't move down")
    
    def delete(self):
        # self.current_project.instruments.
        self.current_project.instruments.remove(self.instrument)
        self.deleteLater()
        
        
        pass
        




            
'''
2024 -08-25 i made a colour class 

    def set_instrument_colour(self):
        dlg = QtWidgets.QColorDialog(self)
        if self.instrument.colour:
            print(self.instrument.colour)
            dlg.setCurrentColor(QtGui.QColor(*self.instrument.colour)) #* is for unpacking into seperate arguments
        if dlg.exec(): # returns true when user confirms selection
            colour = dlg.currentColor()
            rgb = (colour.red(), colour.green(), colour.blue())
            self.instrument.colour = rgb
            print(self.instrument.colour)

        # updates bg colour for instrument wrapper    
        self.update_bg()
        

    def update_bg(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(*self.instrument.colour))  #  grey background

        # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
        self.setPalette(palette)
'''
class Colour_Widget(QtWidgets.QColorDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def set_colour(self, colour, parent):
        self.colour = colour
        parent.colour = colour    

    def show_colour_widget(self, change_colour):
        if self.parent.colour:
            print(self.parent.colour)
            self.setCurrentColor(QtGui.QColor(*self.parent.colour)) #* is for unpacking into seperate arguments
        if self.exec(): # returns true when user confirms selection
            colour = self.currentColor()
            rgb = (colour.red(), colour.green(), colour.blue())
            self.parent.colour = rgb
            self.colour = rgb
            
            # update whatever colour needs to be updated but I MIGHT DELETE THIS its messy 
            # and might not be wanted
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(*self.parent.colour))  #  grey background
            # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
            change_colour.setPalette(palette)

            print(self.parent.colour)

class Speed_Slider(QWidget):
    def __init__(self, instrument):
        super().__init__()


        self.speed_popup = QWidget(self, Qt.Popup) # making the popup widget
        self.speed_popup.setWindowFlags(self.speed_popup.windowFlags() | Qt.Popup)
        self.speed_popup.setLayout(QVBoxLayout())
        self.speed_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.speed_popup.layout().addWidget(self.speed_slider) # you can only add widgets to layouts


        self.slider_values = [0.4, 0.6, 0.8, 1, 2, 3, 4]

        # setting range of the slider [indices]
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(len(self.slider_values) - 1)
        
        # default value is 1
        self.speed_slider.setValue(self.slider_values.index(1))
        self.speed = 1
        instrument.speed = self.speed

        self.speed_slider.sliderMoved.connect(lambda p: self.set_slider(p, instrument)) # lambda function to take in multipel arguments still a bit confused
    
    def set_slider(self, p, instrument):
        self.speed = self.slider_values[p]
        instrument.speed = self.speed
        print(self.speed)
        

    def show_slider(self, button):
        # print("show slider")
        self.speed_slider.value = self.speed
        slider_pos = button.mapToGlobal(button.rect().bottomLeft())
        self.speed_popup.move(slider_pos)
        self.speed_popup.show()



class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        self.layout = QHBoxLayout()

        self.name_label = QLabel("f{name}")
      
        self.layout.addWidget(self.name_label)
        self.setLayout(self.layout)
        
       

# app = QApplication(sys.argv)

# # window = MainWindow()
# # window.show()

# app.exec()