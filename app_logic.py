import pygame as pg
import random
import utils
import vid
import pretty_midi as pm
import numpy as np

display_width = 1280
display_height = 720
vid.constructor(display_width,display_height)

note_colours1 = [
    (255, 105, 180),  # Hot Pink
    (255, 165, 0),    # Orange
    (144, 169, 255),    # periwinkle
    (127, 196, 212),  # nice blue
    (219, 89, 96),    # Tomato
    (138, 43, 226),   # Blue Violet
    (255, 69, 0),     # Red Orange
    (50, 189, 50),    # Lime Green
    (255, 215, 0),    # Gold
    (147, 112, 219),  # Medium Purple
    
]
note_colours2 = [
    (102, 51, 0),      # Dark brown
    (205, 133, 63),    # Copper
    (128, 0, 0),       # Dark red
    (34, 139, 34),     # Forest green
    (75, 0, 130),      # Purple
    (0, 191, 255),     # Bright blue
    (51, 25, 0),      # Darker brown
    (139, 69, 19),     # Darker copper
    (85, 42, 10),     # Deep brown
    (46, 139, 87),     # Darker green
    (105, 105, 105),    # Dark gray
    (178, 34, 34),     # Crimson
    (0, 100, 0),      # Dark green
    (128, 0, 128),     # Purple
    (0, 0, 139)       # Navy blue
]
bg_colour = (220, 230, 240)
bg_colour_2 = (245, 222, 179)

'''Changes to do: Make applogic not dependent on midi path, only midi data'''
class AppLogic():

    def __init__(self, midi_path):
        self.midi_path = midi_path
        self.midi_data = pm.PrettyMIDI(midi_path)
        self.instruments = self.midi_data.instruments
        # print(len(self.instruments))
        self.set_default_settings()
        self.process_midi() # processing midi
        self.set_total_duration( max(note.end for instrument in self.instruments for note in instrument.notes)) # generator expression, gets the max val of note.end
        
        pg.init()
        # self.

    def reset(self):
        self.midi_path = ''
        self.midi_data = None
        self.instruments = []
        
    
    def set_display_width(self, display_width):
        self.display_width = display_width
    def set_display_height(self, display_height):
        self.display_height = display_height
    def set_starting_position(self, starting_position):
        self.starting_position = starting_position
    def set_note_length(self, note_length):
        self.note_length = note_length
    def set_bpm(self, bpm):
        self.bpm = bpm
    def set_total_duration(self, total_duration):
        self.total_duration = total_duration

    def set_instrument_colour(instrument, colour):
        pass    

    def set_colour(self, bg_colour):
        self.colour = bg_colour    
    def set_default_settings(self):
        # default
        self.set_display_width(1280)
        self.set_display_height(720)
        self.set_starting_position(1000)
        self.set_note_length(120)
        self.set_line_x(600)
        self.set_colour(bg_colour_2)

    #P
    def process_midi(self):
        
        #setting initial bpm, its just for note generation not too important
        tempo_times, tempo_bpm = self.midi_data.get_tempo_changes()
        self.set_bpm(tempo_bpm[0])
        min_pitch = 1000
        max_pitch = -1000
        
        # getting info about the song, in this case right now its just the max and min pitch
        for index, instrument in enumerate(self.instruments):
                
                # adding new attributes to instrument and notes objects
                setattr(instrument, "colour", None)
                setattr(instrument, "speed", None)
                setattr(instrument, "icon", None)

                '''
                layer may be useful, but i will be using index and enumerate for now. 
                '''
                # setattr(instrument, "layer", index) 
                # setattr(instrument.notes, "is_clicked", None)

                instrument_name = instrument.name
                # instrument_colour = input(f"what colour should the {instrument_name} be? ")
                instrument_colour = note_colours2[index]
                print(instrument_colour)
                # input_colour = instrument_colour.split(',')
                # instrument_colour = tuple(map(int, input_colour))
                # instrument_speed = float(input(f"what speed should the {instrument_name} be? "))
                # instrument_icon =input(f"what icon should the {instrument_name} be? ")
                instrument.colour = instrument_colour
                # instrument.speed = instrument_speed
                

                '''
                Code to switch around order of instrument layers, will probably need to update when integrating
                with gui. Nevermind, its a pain to do it now, ill just wait till gui 
                '''
                # temp_instrument = instruments[index]
                # new_index = int(input(f"what layer should the {instrument_name} be? "))
                # instruments[index] = instruments[new_index]
                # instruments[new_index] = temp_instrument

                # instrument.icon = instrument_icon
                # pitches
                
                for note in instrument.notes:
                    setattr(note, "click_status", 0)
                    setattr(note, "y_pos", 0)
                    if max_pitch < note.pitch:
                        max_pitch = note.pitch
                    if min_pitch > note.pitch:
                        min_pitch = note.pitch

    # Merging new midi files to current project
    def merge_midi(self, new_midi_path):
        
        new_midi_data = pm.PrettyMIDI(new_midi_path)
        new_instruments = new_midi_data.instruments
        print(len(new_instruments))
        # self.set_default_settings()
        for instrument in new_midi_data.instruments:
            self.instruments.append(instrument)


    def set_line_x(self, line_x):
        self.line_x = line_x


    def generate_vid(self):
        pg.quit()
        pg.init()
        position = 0
        num_pitches = 110
        clock = pg.time.Clock()
        screen = pg.display.set_mode((self.display_width, self.display_height))
        running = True
        line_x = self.line_x
        bpm = self.bpm
        note_length = self.note_length
        starting_position = self.starting_position
        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    vid.video.release()

        
            # clean screen with bg colour
            screen.fill(self.colour)

            # DELAY if i want to use it ever. "w key"
            keys = pg.key.get_pressed()
            if keys[pg.K_w]:
                pg.time.delay(1000)
        
            # iterating through each note
            for instrument in self.instruments:
                # print(instrument)
                instrument_colour = instrument.colour
                instrument_speed = instrument.speed
                # speed
                temp_length = note_length*instrument_speed

                
                # instrument_icon = instrument.icon
                for note in instrument.notes:
                    start = note.start
                    end = note.end
                    pitch = note.pitch
                    velocity = note.velocity
                    note_colour = instrument_colour
                    note_tempo = bpm # place holder, i can make a more dynamic way of getting the accurate tempo for tempo changes

                    # note properties
                    rect_width = (end-start)*temp_length * (note_tempo/60)*0.9 # - 4 or soemthing for aesthetic reasons
                    rect_height = display_height/num_pitches
                    rect_x = line_x + (starting_position-line_x)*instrument_speed+ start*temp_length * (note_tempo/60) - position*instrument_speed
                    rect_y = (num_pitches - pitch - 1) * rect_height
            
                    # print(note.click_status)

                    if rect_x < line_x + 5 and rect_x > line_x-rect_width - 500:
                        if note.click_status != 4: # 4 = done clicking

                            if note.click_status == 3: # 3 = clicked
                                note.y_pos -= 1
                                rect_y += note.y_pos    
                                if note.y_pos <= 2:
                                    note.click_status = 4
                                

                            elif note.click_status == 2: # 2=  clicking
                                rect_y += note.y_pos
                                if rect_x <line_x-rect_width *1.2:
                                    note.click_status = 3
                                    
                        

                            elif note.click_status == 1: # 1= clicked
                                note.y_pos += 1
                                rect_y += note.y_pos    
                                if note.y_pos >= 7:
                                    note.click_status = 2
                                
                            
                            elif note.click_status == 0: # 0 = not clicked
                                if rect_x <= line_x: 
                                    note.click_status = 1 
                                    
                    if note.click_status in [1,2,3]: # if note in process of getting clicked
                        note_colour = utils.lighten_colour(instrument_colour,0.2) # lighten the colour
                    else:
                        note_colour = instrument_colour 

                    # rect_color = (204, 51, 51)  # Red color
                    rect_color = note_colour

                    pg.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
                    pg.display.update(pg.Rect(rect_x, rect_y, rect_width, rect_height))
                    
                    # pg.time.delay(10)
                    # print("rectangle")
                    # print(note)
        
            pg.display.update()
            
            # the line
            line_start = (self.line_x,0)
            line_end = (self.line_x,720)
            line_width = 5
            line_colour = (225,225,225)
            pg.draw.line(screen, line_colour, line_start, line_end, line_width)



            vid.vid_generator(screen)
            clock.tick(60) 
            # beat_per_pixels = (bpm/60)/note_length    
            position += note_length*(bpm/60) * (1/60) 
        pg.quit()            # Quit Pygame
    
            
    def generate_frame(self, stamp):
        
        # do some errotrapping in case pg is already running

        pg.init()
        num_pitches = 110
        clock = pg.time.Clock()
        # frame_screen = pg.display.set_mode((self.display_width, self.display_height))
        frame_screen = pg.Surface((self.display_width, self.display_height))

        line_x = self.line_x
        bpm = self.bpm
        note_length = self.note_length
        starting_position = self.starting_position

        frame_screen.fill(self.colour)

        # print(f"{self.total_duration} totla duration ")

        total_duration_sec = self.total_duration*60
        current_time = (stamp/100)*total_duration_sec
        # print(f"{current_time} is current time")


        # multiply algo by the time stamp in percentage * total duration of song
        position = note_length*(bpm/60) * current_time/40

        # print(f"{position} POSITION")
        for instrument in self.instruments:
            instrument_colour = instrument.colour
            instrument_speed = instrument.speed
            temp_length = note_length*instrument_speed
            
            for note in instrument.notes:
                start = note.start
                end = note.end
                pitch = note.pitch
                velocity = note.velocity
                note_colour = instrument_colour
                note_tempo = bpm
                # note properties
                rect_width = (end-start)*temp_length * (note_tempo/60)*0.9 # - 4 or soemthing for aesthetic reasons
                rect_height = display_height/num_pitches
                rect_x = line_x + (starting_position-line_x)*instrument_speed+ start*temp_length * (note_tempo/60) - position*instrument_speed
                rect_y = (num_pitches - pitch - 1) * rect_height
            
                if note.click_status in [1,2,3]: # if note in process of getting clicked
                    note_colour = utils.lighten_colour(instrument_colour,0.2) # lighten the colour
                else:
                    note_colour = instrument_colour 

                # rect_color = (204, 51, 51)  # Red color
                rect_color = note_colour

                pg.draw.rect(frame_screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
                # pg.display.update(pg.Rect(rect_x, rect_y, rect_width, rect_height))

        # raw_frame = pg.image.tostring(frame_screen, "RGB")
        raw_frame = pg.surfarray.array3d(frame_screen)
           

        return raw_frame

        