def __init__(self):
    super(MainWindow, self).__init__()
    # Get the directory where the current script is located
    self.project_directory = os.path.dirname(os.path.abspath(__file__))

    self.current_project = None

    self.setWindowTitle("Midi Visualizer")
    self.resize(1280,720)

    # Storing lists of dynamic parts of the app
    self.dynamic_widgets = []
    self.dynamic_buttons = []

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
    

    # Preview_layout holds the live player and player controls
    self.preview_layout = QVBoxLayout()

    self.preview_screen = Preview_Screen()
    self.preview_slider = Preview_Slider()

    self.preview_layout.addWidget(self.preview_screen)
    self.preview_layout.addWidget(self.preview_slider)

    # Control Layout holds easy access to more general song controls
    self.control_layout = QHBoxLayout()
    
    # BG COLOUR BUTTON
    self.bg_colour_button = QPushButton("bg colour")
    self.control_layout.addWidget(self.bg_colour_button)
    
    
    # GENERATE BUTTON
    self.generate_button = QPushButton("generate")
    self.control_layout.addWidget(self.generate_button)
    self.dynamic_buttons.append(self.generate_button)

    # CLEAR BUTTON
    self.clear_instruments_button = QPushButton("clear")
    self.control_layout.addWidget(self.clear_instruments_button)
    self.dynamic_buttons.append(self.clear_instruments_button)
    ###################################################################

    self.preview_panel.addLayout(self.preview_layout)
    self.preview_panel.addLayout(self.control_layout)

    # self.preview_layout.addWidget(Color('red'))
    # self.preview_layout.addWidget(Color('blue'))


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

