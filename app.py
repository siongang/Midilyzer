import sys
import os
import shutil
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSlider, QWidget,QLabel,QDialog, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QToolBar, QPushButton, QFileDialog
from PySide6.QtGui import QPalette, QColor, QAction, QPixmap, QImage
from app_logic import AppLogic
import numpy as np

import helper

file_opened = False

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Get the directory where the current script is located
        self.project_directory = os.path.dirname(os.path.abspath(__file__))

        self.current_project = ""

        # Storing lists of dynamic parts of the app
        self.dynamic_widgets = []
        self.dynamic_buttons = []

        # UI Set Up starts
        # self.main_window = None

        # self.instrument_scroll_container = None
        # self.tools_container = None

        self.setup_window()
        self.create_menu_bar()
        self.setup_layouts()
        self.setup_scroll_area(self.instrument_scroll_container)
        self.setup_preview_panel(self.tools_container)
        self.setup_control_panel(self.tools_container)

        self.setup_central_widget(self.main_window)

    # Window Properties
    def setup_window(self):
        self.setWindowTitle("Midi Visualizer")
        self.resize(1280,720)

    def create_menu_bar(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        
        self.file_menu.addAction(open_action)
        # file_menu.addSeperator()

    # Main and Relevent Layouts
    def setup_layouts(self):
        self.main_window = QHBoxLayout()
        self.instrument_scroll_container = QVBoxLayout()
        self.tools_container = QVBoxLayout()


    '''
    (L) {instrument_scroll_container} <- (W) scroll_area <- (W) scroll_contents [(L) instrument_content_layout]
    '''
    def setup_scroll_area(self, parent):

        self.instrument_scroll_contents = QWidget()

        self.instrument_content_layout = QVBoxLayout()
        self.instrument_content_layout.setAlignment(Qt.AlignTop)
        self.instrument_scroll_contents.setLayout(self.instrument_content_layout)


        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setWidget(self.instrument_scroll_contents)

        parent.addWidget(self.scroll_area)
    

    '''
    (L) {tools_container} <- (L) preview_panel <- [(W) preview_screen, (W) preview_slider]
    '''
    def setup_preview_panel(self, parent):
        self.preview_panel = QVBoxLayout() 
        
        self.preview_screen = Preview_Screen()
        self.preview_slider = Preview_Slider()

        self.preview_panel.addWidget(self.preview_screen)
        self.preview_panel.addWidget(self.preview_slider)

        parent.addLayout(self.preview_panel)

    '''
    (L) {tools_container} <- (L) control_panel <- [buttons]
    '''
    def setup_control_panel(self, parent):
        self.control_panel = QHBoxLayout()
        
        # BG COLOUR BUTTON
        self.bg_colour_button = QPushButton("bg colour")
        self.control_panel.addWidget(self.bg_colour_button)
                
        # GENERATE BUTTON
        self.generate_button = QPushButton("generate")
        self.control_panel.addWidget(self.generate_button)
        
        # CLEAR BUTTON
        self.clear_instruments_button = QPushButton("clear")
        self.control_panel.addWidget(self.clear_instruments_button)
        
        self.dynamic_buttons.append(self.generate_button)
        self.dynamic_buttons.append(self.clear_instruments_button)

        parent.addLayout(self.control_panel)


    def setup_central_widget(self, main_window):
        self.main_window.addLayout(self.instrument_scroll_container)
        self.main_window.addLayout(self.tools_container)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(main_window)
        self.setCentralWidget(self.central_widget)




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
        destination_path = os.path.join(project_directory, save_folder)
        destination_path = os.path.join(destination_path, file_basename)


        # print(source_file)
        # print(destination_path)
        shutil.move(source_file, destination_path) #Moving the file to database

        
        if self.current_project == "":
            self.current_project = AppLogic(destination_path)
        elif self.current_project.midi_data == None:
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
            instr_widget = Instrument(instr.name, instr, self.current_project)
            
            instr_widget.refreshPreview.connect(lambda: self.preview_screen.update_frame(
            self.current_project.generate_frame(self.preview_slider.value())
            ))

            self.instrument_content_layout.addWidget(instr_widget)
           

        '''Colour things'''
        # setting the instrument scroll container colour!!
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(*self.current_project.colour))  #  grey background
        # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
        self.instrument_scroll_contents.setPalette(palette)

        self.bg_colour_widget = Colour_Widget(self.current_project)
        self.dynamic_widgets.append(self.bg_colour_widget)
        self.bg_colour_button.clicked.connect(lambda: self.bg_colour_widget.show_colour_widget(self.instrument_scroll_contents))
       
        self.bg_colour_widget.colourChanged.connect(lambda: self.preview_screen.update_frame(
            self.current_project.generate_frame(self.preview_slider.value())
            )
        )
            
        self.dynamic_buttons.append(self.bg_colour_button)
        
        self.preview_screen.update_frame(self.current_project.generate_frame(30))

        self.preview_slider.valueChanged.connect(lambda pos:
            self.preview_screen.update_frame(
                self.current_project.generate_frame(pos),
             
            )
        )

        self.clear_instruments_button.clicked.connect(self.clear_clicked)
        self.dynamic_buttons.append(self.clear_instruments_button)

         # connect generate button to app logic generate code
        self.generate_button.clicked.connect(self.current_project.generate_vid)
        self.dynamic_buttons.append(self.generate_button)


        file_opened = True
    

    def clear_clicked(self):
        self.clear_instruments()
        self.preview_screen.clear()
        # Reset the palette to the default system-defined colors
        default_palette = self.style().standardPalette()  # Get the default system palette
        self.instrument_scroll_contents.setPalette(default_palette)

        for dyn_button in self.dynamic_buttons:
            try:
                dyn_button.clicked.disconnect()  # Disconnect the signal
            except TypeError:
                pass  # Ignore if already disconnected
        self.dynamic_buttons.clear()  # Clear the list after disconnecting

        
        for dyn_button in self.dynamic_buttons:
            try:    
                dyn_button.clicked.disconnect()
            except TypeError:
                pass
        self.dynamic_buttons.clear() 
        

    def clear_instruments(self):
        for i in reversed(range(self.instrument_content_layout.count())):
            print(i)
            widget = self.instrument_content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                print("deleted")

        self.current_project.reset()

'''
instrument_wrapper <- Name label widget + button_wrapper

'''
import re
class Instrument(QWidget):
    refreshPreview = Signal()
    def __init__(self, name, instrument, current_project):
        super().__init__()
        # Attributes
        self.instrument = instrument
        self.current_project = current_project
        self.name = name
        self.safe_name = re.sub(r'[^\x20-\x7E]', '', self.name)  # Remove invalid characters

        self.setup_ui()
        self.setup_signals()


    def setup_ui(self):
        # Instrument Wdiget Background Handling
        self.setAutoFillBackground(True)
        self.update_bg_colour()

        # Main Layout for each Instrument
        self.instrument_layout = QVBoxLayout()

        # Label for the instrument name
        self.instrument_name_label = QLabel(f"{self.safe_name.strip()}")
        self.instrument_layout.addWidget(self.instrument_name_label)

        # Button Layout
        self.button_layout = self.setup_button_layout()
        self.instrument_layout.addLayout(self.button_layout)

        # Set Layout for the Widget
        self.setLayout(self.instrument_layout)
        self.setFixedHeight(60)

        


    def update_bg_colour(self):
        self.palette = self.palette()
        self.palette.setColor(QPalette.Window, QColor(*self.instrument.colour))
        self.setPalette(self.palette)


    def setup_button_layout(self):
        """
        Creates a layout for buttons that alter instrument properties

        Parameters:
            - self: Instrument Widget

        Returns:
            -  button_layout: QHBoxLayout() 
        """
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)

        self.colour_button = self.create_button("colour", lambda: self.colour_widget.show_colour_widget(self))
        self.speed_button = self.create_button("speed", lambda: self.speed_slider.show_slider(self.speed_button))

        button_layout.addWidget(self.colour_button)
        button_layout.addWidget(self.speed_button)
        return button_layout
    
    def create_button(self, text, callback):
        
        """
        Creates a button

        Parameters:
            - self: Instrument Widget
            - text: Button text
            - callback: function to call when button is clicked
        Returns:
            -  button: QPushButton()
        """
        button = QPushButton(text)
        button.setMinimumWidth(70)
        button.setMaximumWidth(120)
        button.clicked.connect(callback)
        return button

    def setup_signals(self):       
        """
        Sets up signals 

        Parameters:
            - self: Instrument Widget
            - text: Button text
            - callback: function to call when button is clicked
        Returns:
            None
        """
        self.speed_slider = Speed_Slider(self.instrument)
        self.speed_slider.speedChanged.connect(self.refresh_preview)
        self.speed_slider.speedChanged.connect(self.update_speed_button_text)

        self.colour_widget = Colour_Widget(self.instrument)
        self.colour_widget.colourChanged.connect(self.refresh_preview)

    def update_speed_button_text(self):
        """Update the speed button text to show the current speed."""
        self.speed_button.setText(f"speed: {self.speed_slider.speed}")

    def refresh_preview(self):
        """
        Refreshes Preview by emitting a signal 

        Parameters:
            - self: Instrument Widget
        Returns:
            None
        """
        self.refreshPreview.emit()

    def mousePressEvent(self, event):
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
        # Add actions to menu
        instrument_menu.addAction(move_up)
        instrument_menu.addAction(move_down)
        instrument_menu.addAction(delete)
        # Render Menu at Mouse Position
        instrument_menu.exec(event.globalPos())
  
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
        
        
class Preview_Screen(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent) # initializes Label object
        self.setFixedSize(640,360)
        self.setScaledContents(True)

    def update_frame(self, raw_frame):
               
        """
        Updates Preview Screen with new image using qimage and pixmap

        Parameters:
            - self: Preview_Screen: QLabel()
            - raw_frame: pg.surfarray.array3d(frame_screen)
        Returns:
            None
        """     
        raw_frame = np.transpose(raw_frame, (1, 0, 2))
        raw_frame = np.ascontiguousarray(raw_frame, dtype=np.uint8)
        height, width, _ = raw_frame.shape

        qimage = QImage(
            raw_frame.data,
            width, 
            height,
            QImage.Format_RGB888
        )
        
        pixmap = QPixmap.fromImage(qimage)
        self.setPixmap(pixmap)
    

    def clear_screen(self):
        self.clear()



class Preview_Slider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMinimum(0)
        self.setMaximum(100)
       



class Colour_Widget(QtWidgets.QColorDialog):
    colourChanged = Signal(tuple)

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
            
            # Emit the colorChanged signal
            self.colourChanged.emit(rgb)

            # update whatever colour needs to be updated but I MIGHT DELETE THIS its messy 
            # and might not be wanted
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(*self.parent.colour))  #  grey background
            # palette.setColor(QPalette.Window, QColor("#C5C5C5"))  #  grey background
            change_colour.setPalette(palette)

            print(self.parent.colour)

class Speed_Slider(QWidget):
    speedChanged = Signal()
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

        self.speed_slider.valueChanged.connect(lambda p: self.set_slider(p, instrument)) # lambda function to take in multipel arguments still a bit confused

    def set_slider(self, p, instrument):
        self.speed = self.slider_values[p]
        instrument.speed = self.speed
        self.speedChanged.emit()
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
        

class Button(QPushButton):
    pass