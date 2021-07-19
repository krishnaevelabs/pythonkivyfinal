# from kivy.core.window import Window
# Window.size = (1280,720)

# importing required libraries

import threading
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.audio import SoundLoader
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IconLeftWidget, OneLineAvatarListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.stacklayout import MDStackLayout
from buttonclass import button
from serialclass import serialClass

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUZZER=18
buzzState = False
GPIO.setup(BUZZER, GPIO.OUT)

# Initialise Required Variables

buttons = {}
messageData = []
card_dict = {}
queue = []
c_stat = "123"

# Read data from CSV and creates objects of button class and saving to buttons dictionary.

buttonRawDatas = serialClass.readcsv(serialClass)
for buttonRawData in buttonRawDatas:
    buttonDataStr = str(buttonRawData)
    parsedButtonData = buttonDataStr.split("-")
    d = button(parsedButtonData[1], parsedButtonData[2], parsedButtonData[3])
    d1 = {d.id: d}
    buttons.update(d1)

# Print buttons objects

#for obj in buttons.values():
   # print(obj.id, obj.bedName, obj.location)

# Connect USB for Serial Communication

serialClass.ports(serialClass)


class Test1(MDStackLayout):
    spacing = dp(10), dp(10)
    padding = dp(10), dp(10), dp(10), dp(10)

    con_stat = StringProperty("First Value")
    con_color = StringProperty("f5433d")

    def __init__(self, *args, **kwargs):
        super(Test1, self).__init__(*args, **kwargs)
        # Start thread to read incoming serial data


        th = threading.Thread(target=serialClass.readIncomingMessage, args=(serialClass, buttons, queue, self), daemon=True)
        th.start()

        # Set the timer for redrawing the screen

        refresh_time = 0.1
        Clock.schedule_interval(self.timer, refresh_time)

    def timer(self, dt):
        self.card_print()

    def update_conn_status(self, val):
        self.con_stat = val
        if val == "Connected":
            self.con_color = "#6cc26b"
        else:
            self.con_color = "#f5433d"
        return


    def card_print(self):

        if queue:
            beep = SoundLoader.load('beep_sound.ogg')
            message_data = queue[0]
            #print(message_data)
            queue.pop(0)
            for item in buttons.values():
                if item.id == message_data[0]:
                    widget_id = item
                    if item.id not in card_dict:
                        if message_data[1] == "C":
                            item.call("Called", "Alerted", message_data[3])
                            l = MDCard(orientation="vertical",
                                       padding=(dp(8)),
                                       size_hint=(None, None),
                                       size=(dp(350), dp(280))
                                       )
                            self.add_widget(l)

                            l1 = MDLabel(text="PATIENT CALL",
                                         halign="center",
                                         theme_text_color="Secondary",
                                         size_hint_y=None,
                                         height=dp(40)
                                         )
                            l2 = MDSeparator(height=dp(5)
                                             )
                            l3 = IconLeftWidget(icon="map-marker",
                                                size=("60sp", "60sp")
                                                )
                            l4 = OneLineAvatarListItem(text=f"[size=20]{item.location}[/size]")
                            l4.add_widget(l3)

                            l5 = MDLabel(text=item.bedName,
                                         halign="center",
                                         theme_text_color="Custom",
                                         text_color=(1, 0, 0, 1),
                                         font_style='H3'
                                         )

                            l6 = MDFillRoundFlatButton(text=f"[size=20]ACKNOWLEDGE[/size]",
                                                       theme_text_color='Custom',
                                                       text_color=(0, 0, 0, 1),
                                                       pos_hint={"center_x": .5, "center_y": .5},
                                                       size_hint=(1, 0.35),
                                                       height=dp(100),
                                                       md_bg_color=(1, 0, 0, 1),
                                                       on_press=lambda x: self.ack_b(l6, widget_id, beep)
                                                       )

                            l.add_widget(l1)
                            l.add_widget(l2)
                            l.add_widget(l4)
                            l.add_widget(l5)
                            l.add_widget(l6)

                            # Add the card widget to card_dict
                            card_dict[item.id] = l

                            # Play beep sound
                            GPIO.output(BUZZER,True)
                            time.sleep(1)
                            GPIO.output(BUZZER,False)
                          #  beep.play()

                    else:
                        if message_data[1] == "D":
                            item.sendAck = 'ack'
                            self.remove_widget(card_dict[item.id])
                            card_dict.pop(item.id)
                        elif message_data[1] == "A":
                            item.sendAck = 'ack'
                            self.remove_widget(card_dict[item.id])
                            card_dict.pop(item.id)
                        elif message_data[1] == "C" and message_data[2] == "1":
                            item.sendAck = 'ack'
                            #beep.play()
                            GPIO.output(BUZZER,True)
                            time.sleep(1)
                            GPIO.output(BUZZER,False)
                            #print(card_dict[item.id].children[0])
                            card_dict[item.id].children[0].text = f"[size=20]ACKNOWLEDGE[/size]"
                            card_dict[item.id].children[0].md_bg_color = (1, 0, 0, 1)

    @staticmethod
    def ack_b(widget, item, beep):
        #beep.stop()
        item.sendAck = 'ackT'
        widget.text = "[color=#000000][size=20]ACKNOWLEDGED[/size][/color]"
        widget.md_bg_color = (1, 1, 0, 1)


class front_screen(MDScreen):
    def __init__(self, **kwargs):
        super(front_screen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        #print(self.ids)
        pass



# Main App class
class SerialDataApp(MDApp):

    def build(self):
        # sv = ScrollView()
        # ml = Test1()
        screen_manager = ScreenManager()
        screen_manager.add_widget(front_screen())

        # sv = ScrollView(size_hint=(1, None), height= self.minimum_height)
        # f = front_screen()
        # sv.add_widget(ml)
        # f.add_widget(sv)
        # scr.add_widget(f)

        return screen_manager


# Main program
if __name__ == '__main__':
    # Launch the app
    SerialDataApp().run()
