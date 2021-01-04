from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from functools import partial
from kivy.config import Config
import sqlite3
import time
import random
import sys
import pyttsx3
from threading import Thread
from cj_helper import ChatBot
Config.set('kivy', 'window_icon', 'myicon.png')
def speak(word):
    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()


def logins(manager):
    con = sqlite3.connect('CJ.db')
    cur = con.cursor()
    cur.execute('SELECT previous FROM settings')
    pre = cur.fetchone()
    cur.execute('UPDATE settings SET previous=? WHERE previous=?', ('Login', pre[0],))
    con.commit()
    main = RelativeLayout(size=(300, 300))
    main.add_widget(Label(text="Login to get access to CJ", font_size=25,
                          size_hint=(.3, .3), pos_hint={'center_x': .5, 'center_y': .9}))
    main.add_widget(Label(text='Username:', size_hint=(.3, .3), font_size=25, pos_hint={'center_x': .3, 'center_y': .6}
                          ))

    def check(user, pw, instance):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        cur.execute('SELECT name, password FROM settings')
        name, passed = cur.fetchone()
        if user.text == '' or pw.text == '':
            false = RelativeLayout(size_hint=(.3, 2))
            false.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3, .3),
                                   pos_hint={'center_x': .5, 'center_y': .4}))
            close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
            false.add_widget(close)
            pop = Popup(title='Please fill out form', content=false, size_hint=(.4, .4))
            pop.open()
            close.bind(on_release=pop.dismiss)
            speak('Please fill out the form')
        elif user.text != name or pw.text != passed:
            false = RelativeLayout(size_hint=(.4, 2))
            false.add_widget(Label(text='Incorrect Name and Password', font_size=25, size_hint=(.3, .3),
                                   pos_hint={'center_x': .5, 'center_y': .4}))
            close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
            false.add_widget(close)
            poped = Popup(title='False Login', content=false, size_hint=(.5, .4))
            poped.open()
            close.bind(on_release=poped.dismiss)
            speak('Wrong login credentials')
        elif user.text == name and pw.text == passed:
            manager.current = 'Welcome'
            speak('Welcome Sir')
        con.close()

    main.add_widget(Label(
        text='Password:', size_hint=(.3, .3), font_size=25, pos_hint={'center_x': .3, 'center_y': .5}
    ))
    username = TextInput(
        multiline=False, readonly=False, halign="right", font_size=25, size_hint=(.3, .1),
        pos_hint={'center_x': .55, 'center_y': .6}
    )
    password = TextInput(
        multiline=False, readonly=False, halign="right", font_size=25, size_hint=(.3, .1),
        pos_hint={'center_x': .55, 'center_y': .5}, password=True
    )
    main.add_widget(username)
    main.add_widget(password)
    main.add_widget(Button(
        text='Login', size_hint=(.2, .1), pos_hint={'center_x': .6, 'center_y': .4},
        on_release=partial(check, username, password)
    ))
    con.close()
    speak("Login to get access to CJ")
    return main


def welcomes(manager):
    con = sqlite3.connect('CJ.db')
    cur = con.cursor()
    cur.execute('SELECT previous FROM settings')
    pre = cur.fetchone()
    cur.execute('UPDATE settings SET previous=? WHERE previous=?', ('Welcome', pre[0],))
    con.commit()
    box = RelativeLayout(size=(300, 300))

    def gotochat(instance):
        manager.current = 'Assitant'
        speak('Opening CJ Chat')

    def gotosetting(instance):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        cur.execute('SELECT previous FROM settings')
        pre = cur.fetchone()
        cur.execute('UPDATE settings SET previous=? WHERE previous=?', ('Welcome', pre[0],))
        con.commit()
        manager.current = 'Setting'
        speak('Opening Settings')

    box.add_widget(Image(
        source='Legacy-Tech.png', pos_hint={'center_x': .5, 'center_y': .7}, allow_stretch=True, keep_ratio=False
    ))
    box.add_widget(Label(
        text="Welcome Sir", font_size=50, pos_hint={'center_x': .5, 'center_y': .1}
    ))
    box.add_widget(Button(text='Chat', size_hint=(.2, .1), pos_hint={'center_x': .9, 'center_y': .1},
                          on_release=gotochat))
    box.add_widget(Button(text='settings', size_hint=(.2, .1), pos_hint={'center_x': .1, 'center_y': .1},
                          on_release=gotosetting))
    con.close()
    return box


def settings(manager):
    con = sqlite3.connect('CJ.db')
    cur = con.cursor()
    cur.execute('SELECT previous FROM settings')
    pre = cur.fetchone()
    main = RelativeLayout(size=(300, 300))

    def back(instance):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        cur.execute('SELECT previous FROM settings')
        pre = cur.fetchone()
        manager.current = pre[0]

    def cp(instance):
        def done(old, new, instance):
            conn = sqlite3.connect('CJ.db')
            curr = conn.cursor()
            curr.execute('SELECT password FROM settings')
            current = curr.fetchone()
            if old.text == current[0]:
                curr.execute('UPDATE settings SET password=? WHERE password=?', (new.text, current[0],))
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(
                    text='Password has been rested\n Reopen CJ to see new password\n Log in with you new password',
                    font_size=18, size_hint=(.3, .3),
                    pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Password Changed', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                conn.commit()
                speak('Password has been changed')
            else:
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Old password was wrong try again', font_size=25, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                pull = Popup(title='Incorrect', content=final, size_hint=(.5, .4))
                pull.open()
                closed.bind(on_release=pull.dismiss)
                speak('Wrong old password')
            conn.close()

        false = RelativeLayout(size_hint=(.6, 2))
        false.add_widget(Label(text='Type in your old password, to be verified', font_size=25, size_hint=(.3, .3),
                               pos_hint={'center_x': .5, 'center_y': .4}))
        false.add_widget(Label(
            text='old password:', font_size=25, size_hint=(.3, .3), pos_hint={'center_x': .3, 'center_y': .3}
        ))
        old_pd = TextInput(
            multiline=False, readonly=False, halign="right", font_size=25, size_hint=(.3, .1),
            pos_hint={'center_x': .65, 'center_y': .3}, password=True
        )
        false.add_widget(old_pd)
        false.add_widget(Label(
            text='New password:', font_size=25, size_hint=(.3, .3), pos_hint={'center_x': .3, 'center_y': .2}
        ))
        new_pd = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.3, .1),
            pos_hint={'center_x': .65, 'center_y': .2}, password=True
        )
        false.add_widget(new_pd)
        close = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .4, 'center_y': .1})
        false.add_widget(close)
        false.add_widget(Button(
            text='Done', size_hint=(.2, .1), pos_hint={'center_x': .7, 'center_y': .1}, on_release=partial(done, old_pd,
                                                                                                           new_pd)
        ))
        pop = Popup(title='False Login', content=false, size_hint=(.6, .4))
        pop.open()
        close.bind(on_release=pop.dismiss)

    def cn(instance):
        def done(old_n, instance):
            cond = sqlite3.connect('CJ.db')
            cursed = cond.cursor()
            cursed.execute('SELECT name FROM settings')
            current = cursed.fetchone()
            if old_n.text != '':
                cursed.execute('UPDATE settings SET name=? WHERE name=?', (old_n.text, current[0],))
                cond.commit()
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Name has been changed.\nYou will have to reopen CJ to notice the change.\n'
                                            'Also you will have to log in with your new name',
                                       font_size=18, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Change Successful', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                cond.close()
                speak('Name has been changed')
            else:
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Incorrect', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                speak('Please input a name')

        inal = RelativeLayout(size_hint=(.4, 2))
        inal.add_widget(Label(text='Type in your new name', font_size=25, size_hint=(.3, .3),
                              pos_hint={'center_x': .5, 'center_y': .4}))
        losed = Button(text='Close', size_hint=(.3, .1), pos_hint={'center_x': .3, 'center_y': .1})
        inal.add_widget(losed)
        old = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.5, .1),
            pos_hint={'center_x': .5, 'center_y': .3}
        )
        inal.add_widget(old)
        inal.add_widget(Button(
            text='Change', size_hint=(.3, .1), pos_hint={'center_x': .7, 'center_y': .1},
            on_release=partial(done, old)
        ))
        oped = Popup(title='Change Name', content=inal, size_hint=(.5, .4))
        oped.open()
        losed.bind(on_release=oped.dismiss)
        speak('Type in your new name')
    def cm(instance):
        def done(old_n, instance):
            cond = sqlite3.connect('CJ.db')
            cursed = cond.cursor()
            cursed.execute('SELECT email FROM settings')
            current = cursed.fetchone()
            if old_n.text != '':
                cursed.execute('UPDATE settings SET email=? WHERE email=?', (old_n.text, current[0],))
                cond.commit()
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='email has been changed.\nYou will have to reopen CJ to notice the change.',
                                       font_size=18, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Change Successful', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                cond.close()
                speak('email has been changed')
            else:
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Incorrect', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                speak('Please input a email')

        inal = RelativeLayout(size_hint=(.7, 2))
        inal.add_widget(Label(text='Type in your new email, has to be @gmail.com', font_size=18, size_hint=(.3, .3),
                              pos_hint={'center_x': .5, 'center_y': .4}))
        losed = Button(text='Close', size_hint=(.3, .1), pos_hint={'center_x': .3, 'center_y': .1})
        inal.add_widget(losed)
        old = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.5, .1),
            pos_hint={'center_x': .5, 'center_y': .3}
        )
        inal.add_widget(old)
        inal.add_widget(Button(
            text='Change', size_hint=(.3, .1), pos_hint={'center_x': .7, 'center_y': .1},
            on_release=partial(done, old)
        ))
        oped = Popup(title='Change Email', content=inal, size_hint=(.5, .4))
        oped.open()
        losed.bind(on_release=oped.dismiss)
        speak('Type in your new Email')
    def cmp(instance):
        def done(old_n, instance):
            cond = sqlite3.connect('CJ.db')
            cursed = cond.cursor()
            cursed.execute('SELECT em_pass FROM settings')
            current = cursed.fetchone()
            if old_n.text != '':
                cursed.execute('UPDATE settings SET em_pass=? WHERE em_pass=?', (old_n.text, current[0],))
                cond.commit()
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Email Password has been changed.\nYou will have to reopen CJ to notice the change.',
                                       font_size=18, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Change Successful', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                cond.close()
                speak('Email Password has been changed')
            else:
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Incorrect', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                speak('Please input a Password')

        inal = RelativeLayout(size_hint=(.7, 2))
        inal.add_widget(Label(text='Type in your new Email Password', font_size=25, size_hint=(.3, .3),
                              pos_hint={'center_x': .5, 'center_y': .4}))
        losed = Button(text='Close', size_hint=(.3, .1), pos_hint={'center_x': .3, 'center_y': .1})
        inal.add_widget(losed)
        old = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.5, .1),
            pos_hint={'center_x': .5, 'center_y': .3}
        )
        inal.add_widget(old)
        inal.add_widget(Button(
            text='Change', size_hint=(.3, .1), pos_hint={'center_x': .7, 'center_y': .1},
            on_release=partial(done, old)
        ))
        oped = Popup(title='Change Name', content=inal, size_hint=(.5, .4))
        oped.open()
        losed.bind(on_release=oped.dismiss)
        speak('Type in your new Email Password')
    def cum(instance):
        def done(old_n, instance):
            cond = sqlite3.connect('CJ.db')
            cursed = cond.cursor()
            cursed.execute('SELECT user_email FROM settings')
            current = cursed.fetchone()
            if old_n.text != '':
                cursed.execute('UPDATE settings SET user_email=? WHERE user_email=?', (old_n.text, current[0],))
                cond.commit()
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Your Email has been changed.\nYou will have to reopen CJ to notice the change.',
                                       font_size=18, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Change Successful', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                cond.close()
                speak('Your email has been changed')
            else:
                final = RelativeLayout(size_hint=(.4, 2))
                final.add_widget(Label(text='Please fill out the form', font_size=25, size_hint=(.3, .3),
                                       pos_hint={'center_x': .5, 'center_y': .4}))
                closed = Button(text='Close', size_hint=(.2, .1), pos_hint={'center_x': .5, 'center_y': .1})
                final.add_widget(closed)
                poped = Popup(title='Incorrect', content=final, size_hint=(.5, .4))
                poped.open()
                closed.bind(on_release=poped.dismiss)
                speak('Please input a email address')

        inal = RelativeLayout(size_hint=(.7, 2))
        inal.add_widget(Label(text='Type in your new email, has to be @gmail.com', font_size=18, size_hint=(.3, .3),
                              pos_hint={'center_x': .5, 'center_y': .4}))
        losed = Button(text='Close', size_hint=(.3, .1), pos_hint={'center_x': .3, 'center_y': .1})
        inal.add_widget(losed)
        old = TextInput(
            multiline=False, readonly=False, halign='right', font_size=25, size_hint=(.5, .1),
            pos_hint={'center_x': .5, 'center_y': .3}
        )
        inal.add_widget(old)
        inal.add_widget(Button(
            text='Change', size_hint=(.3, .1), pos_hint={'center_x': .7, 'center_y': .1},
            on_release=partial(done, old)
        ))
        oped = Popup(title='Change Name', content=inal, size_hint=(.5, .4))
        oped.open()
        losed.bind(on_release=oped.dismiss)
        speak('Type in your new email address')
    cur.execute('SELECT name, password, email, em_pass, user_email FROM settings')
    old_name, old_pd, old_email, old_em_pass, user_email = cur.fetchone()
    main.add_widget(Label(
        text='Current Name: ' + old_name, pos_hint={'center_x': .4, 'center_y': .7}
    ))
    main.add_widget(Label(
        text='Current Password: ' + old_pd, pos_hint={'center_x': .4, 'center_y': .6}
    ))
    main.add_widget(Button(
        text='Change Name', size_hint=(.2, .01), pos_hint={'center_x': .7, 'center_y': .7}, on_release=cn
    ))
    main.add_widget(Button(
        text='Change Password', size_hint=(.3, .01), pos_hint={'center_x': .7, 'center_y': .6}, on_release=cp
    ))
    main.add_widget(Button(
        text='Go Back', on_release=back, size_hint=(.3, .1), pos_hint={'center_x': .1, 'center_y': .9}
    ))
    main.add_widget(Label(text='CJ Email: ' + old_email if old_email != 'blank' else 'Please give CJ a email', pos_hint={'center_x': .4, 'center_y': .5}))
    main.add_widget(Button(
        text='Change CJ email', size_hint=(.3, .01), pos_hint={'center_x': .7, 'center_y': .5}, on_release=cm
    ))
    main.add_widget(Label(text='CJ Email Password: '+ old_em_pass if old_em_pass != 'blank' else 'Please give CJ a email password', size_hint=(.2, .01), pos_hint={'center_x': .4, 'center_y': .4}))
    main.add_widget(Button(
        text='Change CJ email password', size_hint=(.3, .01), pos_hint={'center_x': .7, 'center_y': .4}, on_release=cmp))
    main.add_widget(Label(text='Your Email: ' + user_email if user_email != 'blank' else 'Please give CJ your email', size_hint=(.2, .01), pos_hint={'center_x': .4, 'center_y': .3}))
    main.add_widget(Button(text='Change you email address', size_hint=(.3, .01), pos_hint={'center_x': .7, 'center_y': .3}, on_release=cum))
    con.close()
    return main

def assitants(manager, helper):
    main = RelativeLayout(size=(300, 300))
    def go_home(instance):
        manager.current = 'Welcome'
    def go_setting(instance):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        cur.execute('SELECT previous FROM settings')
        pre = cur.fetchone()
        cur.execute('UPDATE settings SET previous=? WHERE previous=?', ('Assitant', pre[0],))
        con.commit()
        manager.current = 'Setting'
    c_view =Label(
        text='CJ: Hello Sir, what can I help you with today', pos_hint={'center_x': .5, 'center_y': .5}
    )
    text = TextInput(
        multiline=True, readonly=False, halign="left", font_size=25, size_hint=(.5, .1),
        pos_hint={'center_x': .5, 'center_y': .3}
    )
    def check_reminders():
        while True:
            if helper.end == False:
                if helper.is_it_reminder[0] == True:
                    c_view.text = helper.is_it_reminder[1]
                    helper.is_it_reminder[0] = False
                if helper._is_it_timer == True:
                    c_view.text = 'CJ: Your time is up'
                    helper._is_it_timer = False
            else:
                break
    def main_func(instance):
        answer = helper.chat(text.text, c_view.text)
        text.text =''
        c_view.text = 'CJ: ' + answer
        if answer == 'Alright sir have a good day':
            helper.end = True
            App.get_running_app().stop()
    Thread(target=helper.reminder_thread, args=(c_view.text,)).start()
    Thread(target=check_reminders).start()
    main.add_widget(c_view)
    main.add_widget(Button(text="Home", size_hint=(.15, .01), on_release=go_home, pos_hint={'center_x': .1, 'center_y': .95}, background_color='black'))
    main.add_widget(Button(text="Settings", size_hint=(.15, .01), on_release=go_setting, pos_hint={'center_x': .9, 'center_y': .95}, background_color='black'))
    send = Button(size_hint=(.1, .1), on_release=main_func, text='send', pos_hint={'center_x': .7, 'center_y': .3}, background_color='black')
    logo = Button(size_hint=(.2, .2), background_normal='Legacy-Tech.png', pos_hint={'center_x': .5, 'center_y': .1})
    main.add_widget(text)
    main.add_widget(send)
    main.add_widget(logo)
    return main

sm = ScreenManager()
sm.title = 'CJ'
helper = ChatBot()
login = Screen(name='Login')
login.add_widget(logins(sm))
welcome = Screen(name='Welcome')
setting = Screen(name='Setting')
assitant = Screen(name="Assitant")
assitant.add_widget(assitants(sm, helper))
setting.add_widget(settings(sm))
welcome.add_widget(welcomes(sm))
sm.add_widget(login)
sm.add_widget(welcome)
sm.add_widget(setting)
sm.add_widget(assitant)

class CJ(App):
    icon = 'myicon.png'
    def build(self):
        Window.bind(on_request_close=self.close_win)
        return sm
    def close_win(self, *args):
        self.textpopup(title="Exit", text='Are you sure?')
        return True
    def textpopup(self, title='', text=''):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        my_button = Button(text='Ok', size_hint=(1, .25))
        box.add_widget(my_button)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        my_button.bind(on_release=self.close_all_thanks)
        popup.open()
    def close_all_thanks(self, *args):
        helper.end = True
        App.get_running_app().stop()