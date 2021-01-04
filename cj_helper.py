from collections import Counter
from cj_fun import preprocess, compare_overlap, pos_tag, extract_nouns, compute_similarity
import spacy
import urllib.request
import webbrowser
import turtle
import pyttsx3
import random
import time
from datetime import datetime, date
from threading import Thread
import re
import sqlite3
import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4.element import PageElement
import requests
from bs4 import BeautifulSoup
import statistics
def speek(word):
    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()


class ChatBot:
    def __init__(self):
        self.word2vec = spacy.load('en_core_web_sm')
        self.exit_commands = ('quit', 'goodbye', 'exit', 'no', 'end', 'close', 'bye')
        self.what_can_do = ["FIll out later"]
        self.commands = open('cj_commands.text', 'r', encoding='utf-8').readlines()
        self.user_message = ''
        self.entity = ''
        self.defualts = ['windows-default', 'linus-default', 'macOs-default']
        self.end = False
        self.is_it_reminder = [False, 'nothing']
        self._is_it_timer =False
        self.jokes = open('cj_jokes.text', 'r', encoding='utf-8').readlines()
        self.blank_spots = ["action", 'Sir', 'CJ', 'translate en to pig', 'translate pig to en', 'timer',
                            'joke', 'reminder', 'delete reminder', 'browser',
                            'website', 'app', 'sunset', 'sunrise', 'weather']
        self.responses = ["I can {}", 'Hello {} what can I do for you?',
                          'My name is {}, named after my creator Chidozie John Nnaji',
                          'My creator {} is a handsome young man, which is a lot coming from me since I am not '
                          'attracted to humans. But he is also a genius and a young prodigy',
                          'The word {} in english is {}',
                          'The word {} in pig latin is {}', 'Your timer is set for {}',
                          'Here is a joke, {}', 'Your reminder {} has been set for {}', 'I will delete your reminder {}',
                          'The reminders you have are {}', 'Opening {} browser', "Going to {}'s website", 'The time is {}', 'The weather is {}'
                          ]
        

    # define .make_exit() below:
    def make_exit(self, user_message):
        self.user_message = user_message
        for exits in self.exit_commands:
            if exits in user_message:
                self.end = True
                return True
        return False
        # define .chat() below:

    def chat(self, user_message, text):
        self.user_message = user_message
        if not self.make_exit(self.user_message):
            self.user_message = self.respond(self.user_message, text)
            return self.user_message
        return 'Alright sir have a good day'

    # define .find_intent_match() below:
    def find_intent_match(self, responses, user_message):
        result = Counter(preprocess(user_message))
        respon = [Counter(preprocess(response)) for response in responses]
        similarity_list = [compare_overlap(result, res) for res in respon]
        return responses[similarity_list.index(max(similarity_list))]

    # define .find_entities() below:
    def find_entities(self, user_message):
        tag = pos_tag(preprocess(user_message))
        print('tag', tag)
        nouns = extract_nouns(tag)
        print('nouns', nouns)
        tokens = self.word2vec(' '.join(nouns))
        category = self.word2vec(" ".join(self.blank_spots))
        word2vec_result = compute_similarity(tokens, category)
        word2vec_result.sort(key=lambda x: x[2])
        if word2vec_result:
            return word2vec_result[-1][0]
        return self.blank_spots

    # define .respond() below:
    def respond(self, user_message, text):
        best_response = self.find_intent_match(self.responses, user_message)
        response = self.make_connection(best_response, user_message, text)
        return response

    def pun(self):
        return random.choice(self.jokes)

    def isletters(self, word):
        for i in word:
            lowercasechar = i.lower()
            if 'a' > lowercasechar > 'z':
                return False
        return True

    def to_pig_latin(self, entity):
        if len(entity) > 0 and self.isletters(entity):
            for i in entity.split(' '):
                fl = i[0]
                new_word = i + fl + 'ay'
            translated = new_word[1:].lower()
            return translated
        else:
            return ''

    def pig_to_english(self, entity):
        if len(entity) > 0 and self.isletters(entity):
            try:
                res = entity.index('y')
            except:
                return ', '.join(entity) + ' is not a pig latin word'
            s = res - 1
            firs = s - 1
            sec = firs
            first = entity[firs]
            second = entity[0:sec]
            bot_reply = first + second
            return bot_reply
        else:
            return ''

    def command(self):
        return random.choice(self.commands)

    def timer(self, minute, text):
        time.sleep(minute * 60)
        speek("Your time is up")
        text='CJ: Your time is up'
        self._is_it_timer = True

    def create_timer_thread(self, minute, text):
        Thread(target=self.timer, args=(minute, text)).start()

    def create_reminder(self, dates, reminder):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        cur.execute("INSERT INTO reminders (date,reminder) VALUES (?,?);", (dates, reminder,))
        con.commit()
        con.close()
    def find_files(self, filename, search_path):
        result = []
        for root, dir, files in os.walk(search_path):
            if filename in files:
                result.append(os.path.join(root, filename))
        return result
    def send_email(self, subject, message, email, emailer, emailer_pass):
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = emailer
        receiver_email = email
        password = emailer_pass
        message = """
        Subject: """ + subject + """

        """+message
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

    # Sending a text
    def send_text(self, subject, emailer, emailer_pass, number, number_provider, bod):
        email = emailer
        pas = emailer_pass
        sms_gateway = number
        sms_gateway = sms_gateway + number_provider #'@tmomail.net'
        smtp = 'smtp.gmail.com'
        port = 587
        server = smtplib.SMTP(smtp, port)
        server.starttls()
        server.login(email, pas)
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = sms_gateway
        msg['Subject'] = subject
        body = bod
        msg.attach(MIMEText(body, 'plain'))
        sms = msg.as_string()
        server.sendmail(email, sms_gateway, sms)
        server.quit()
    def reminder_thread(self, text):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        while True:
            if self.end == False:
                dates = date.today()
                cur.execute('SELECT * FROM reminders')
                all_reminders = cur.fetchall()
                cur.execute('SELECT email, em_pass, user_email FROM settings')
                email, em_pass, user_email = cur.fetchone()
                for remind in all_reminders:
                    if remind[1] == str(dates):
                        speek("It is time for your reminder " + remind[2])
                        text = "CJ: It is time for your reminder " + remind[2]
                        self.is_it_reminder[1] = text
                        self.is_it_reminder[0] = True
                        if ((email != None) and (em_pass != None)) and user_email != None:
                            self.send_email('CJ Reminder', "It is time for your reminder " + remind[2], user_email, email, em_pass)
                        cur.execute("DELETE FROM reminders WHERE date=? and reminder=?;", (remind[1], remind[2]))
                        con.commit()
            else:
                con.close()
                break

    def del_reminder(self, reminder):
        con = sqlite3.connect('CJ.db')
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM reminders WHERE reminder=?;", (reminder,))
            con.commit()
            return 'good'
        except:
            return "failed"

    def make_connection(self, best, user_message, text):
        if best == "I can {}":
            term = best.format(self.command())
            speek(term)
            return term
        elif best == 'Hello {} what can I do for you?':
            speek(best.format('Sir'))
            return best.format('Sir')
        elif best == 'My name is {}, named after my creator Chidozie John Nnaji':
            speek(best.format('CJ'))
            return best.format('CJ')
        elif best == 'My creator {} is a handsome young man, which is a lot coming from me since I am not attracted ' \
                     'to humans. But he is also a genius and a young prodigy':
                    speek(best.format("Chidozie"))
                    return best.format("Chidozie")
        elif best == 'The word {} in pig latin is {}':
            tag = pos_tag(preprocess(user_message))
            nouns = extract_nouns(tag)
            tokens = self.word2vec(' '.join(nouns))
            category = self.word2vec(user_message)
            word2vec_result = compute_similarity(tokens, category)
            word2vec_result.sort(key=lambda x: x[2])
            if word2vec_result:
                self.entity = word2vec_result[-1][0]
                translated = best.format(self.entity, self.to_pig_latin(self.entity))
                if self.to_pig_latin(self.entity) != '':
                    return translated
                else:
                    speek("I do not understand")
                    return 'I do not understand'
            speek('I do not understand please repeat')
            return 'I do not understand please repeat'
        elif best == 'The word {} in english is {}':
            tag = pos_tag(preprocess(user_message))
            nouns = extract_nouns(tag)
            real_nouns = list()
            for i in nouns:
                if i != 'english':
                    real_nouns.append(i)
            tokens = self.word2vec(' '.join(real_nouns))
            category = self.word2vec(user_message)
            word2vec_result = compute_similarity(tokens, category)
            word2vec_result.sort(key=lambda x: x[2])
            if word2vec_result:
                self.entity = word2vec_result[-1][0]
                translated = best.format(self.entity, self.pig_to_english(self.entity))
                if self.pig_to_english(self.entity) != '':
                    return translated
                else:
                    speek('I do not understand')
                    return 'I do not understand'
            speek('I do not understand please repeat')
            return "I do not understand please repeat"
        elif best == 'Your timer is set for {}':
            self.entity = re.search(r'(\d+)', user_message)
            self.create_timer_thread(int(self.entity.group(0)), text)
            return best.format(self.entity.group(0) + ' minutes')
        elif best == 'Here is a joke, {}':
            joke = best.format(self.pun())
            speek(joke)
            return joke
        elif best == 'Your reminder {} has been set for {}':
            date = re.search(r'\d{2}-\d{2}-\d{4}', user_message)
            reminder = re.search(r'to.*', user_message)
            try:
                dates = datetime.strptime(date.group(), '%d-%m-%Y').date()
                self.create_reminder(str(dates), reminder.group(0))
                return best.format(reminder.group(0), dates)
            except:
                return "I did not understand. Please repeat."
        elif best == 'I will delete your reminder {}':
            reminder = re.search(r'to.*', user_message)
            try:
                result = self.del_reminder(reminder.group(0))
                if result == 'good':
                    speek(best.format(reminder.group(0)))
                    return best.format(reminder.group(0))
                else:
                    speek('Reminder {} does not exist'.format(reminder.ground(0)))
                    return "Reminder {} does not exist".format(reminder.group(0))
            except:
                speek("I did not understand. Please repeat.")
                return "I did not understand. Please repeat."
        elif best == 'The reminders you have are {}':
            con = sqlite3.connect('CJ.db')
            cur = con.cursor()
            cur.execute("SELECT * FROM reminders")
            all_reminders = cur.fetchall()
            reminders = [remind[2] for remind in all_reminders]
            remin = " ,".join(reminders)
            if len(remin) > 0:
                speek(best.format(remin))
                return best.format(remin)
            else:
                speek('You have no reminders set')
                return 'You have no reminders set'
        elif best == 'Opening {} browser':
            correct = []
            for defaut in self.defualts:
                try:
                    correct.append(defaut)
                except:
                    continue
            deffed = str(type(webbrowser.get(correct[0]))).replace("<class 'webbrowser.",'')
            deffed = deffed.replace("'>",'')
            webbrowser.get(correct[0]).open('http://www.google.com')
            speek(best.format(deffed))
            return best.format(deffed)
        elif best == "Going to {}'s website":
            tag = pos_tag(preprocess(user_message))
            nouns = extract_nouns(tag)
            print(nouns)
            tokens = self.word2vec(' '.join(nouns))
            category = self.word2vec(" ".join(user_message))
            word2vec_result = compute_similarity(tokens, category)
            word2vec_result.sort(key=lambda x: x[2])
            if word2vec_result:
                word_not_to_look_for = word2vec_result[-1][0]
            else:
                return "I did not understand. Please repeat."
            for n in nouns:
                if n != word_not_to_look_for:
                    webbrowser.open('http://www.'+n+'.com')
                    print(best.format(n))
            speek("Done opening your websites")
            return 'Done'
        elif best == 'The time is {}':
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            return best.format(str(current_time))
        elif best == 'The weather is {}':
            URL = 'https://www.google.com/search?q=whats+the+weather+today'
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            result = soup.find_all('a')
            q = list()
            alls = []
            for res in result:
                find = re.search('/url\?q=https://weather.com(.*)><h3', str(res))
                try:
                    actual = str(find.group(0))
                    actual = actual.replace('"><h3', '')
                    q.append(actual)
                except Exception as e:
                    continue
            for query in q:
                qr = BeautifulSoup(requests.get('https://www.google.com'+query).content, 'html.parser').find_all('a')
                new_qr = str(qr[0].text)
                alls.append(BeautifulSoup(requests.get(new_qr).content, 'html.parser').find_all('span', class_="DailyContent--temp--_8DL5"))
            first = alls[0][0]
            try:
                second = alls[1][0]
                print(first, '-', second)
                fir = re.search('>\d.*span', str(first))
                seco = re.search('>\d.*span', str(second))
                fir = str(fir.group(0)).replace('>', '')
                fir = fir.replace('</span', '')
                seco = str(seco.group(0)).replace('>', '')
                secon = seco.replace('</span', '')
                fi = fir + '-' + secon
            except:
                fi = re.search('>\d.*span', str(first))
                fi = str(fi.group(0)).replace('>', '')
                fi = fi.replace('</span', '')
            speek(best.format(fi))
            return best.format(fi + '  degrees')
        else:
            speek("I am sorry, I don't understand please repeat")
            return "I am sorry, I don't understand please repeat"
