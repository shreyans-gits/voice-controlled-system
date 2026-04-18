import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser as wb
import os
import smtplib
import pyautogui as pag
import tkinter as tk

#Extra
root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()
#Extra

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
#print(voices[0].id)
engine.setProperty('voice', voices[0].id)

my_dict = {"mom" : "shanta.sahu@gmail.com",
           "dad" : "ssubrat77@gmail.com",
           "srikar" : "reachsrikarb@gmail.com",
           "tashi" : "rai.tashi09@gmail.com",
           "mythili" : "mythiliganesh226@gmail.com"}


def speak (audio):
    engine.say(audio)
    engine.runAndWait()

def wishme():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning Sir")
    elif hour>=12 and hour<18:
        speak("Good Afternoon Sir")
    else:
        speak("Good Evening Sir")
    speak("I am the one and the only Jarvis")

def takeCommand():
    #takes command from user and returns a string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    
    except Exception as e:
        #print(e)
        print("Say that again please...")
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('shreyans.sahu07@gmail.com', password)
    server.sendmail('shreyans.sahu07@gmail.com', to, content)
    server.close()

#Extra
def takeScreenshot ():
    
    myScreenshot = pag.screenshot()
    myScreenshot.save('capture.png')
#Extra



if __name__ == "__main__":
    wishme()
    while True:
        query = takeCommand().lower()  
    
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to wikipedia")
            print(results)
            speak(results)

        elif 'search' in query:
            query = query.replace("search", ' ')
            wb.get().open_new('https://www.google.com/search?q='+query)

        elif 'watch' in query:
            query = query.replace("watch", ' ')
            wb.get().open_new('https://www.youtube.com/results?search_query='+query)

        # elif 'meet' in query:
        #     wb.get().open_new('https://meet.google.com/hdi-jsxp-rzu?authuser=0'+query)

        # elif 'smash' in query:
        #     wb.get().open_new('https://www.crazygames.com/game/smash-karts')

        # elif 'messages' in query:
        #     wb.get().open_new('https://mail.google.com/mail/u/0/#inbox')

        elif 'Google' in query:
            wb.get().open_new('google.com')

        elif 'play music' in query:
            music_dir = 'D:\\Deskfiles\\Shreyans\\Music'
            songs = os.listdir(music_dir)
            print(songs)
            os.startfile(os.path.join(music_dir, songs[0]))

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'photo' in query:
            wb.get().open_new('https://photos.google.com')


        # elif 'open class' in query:
        #     codePath = "C:\Program Files (x86)\Webex\Webex\Applications\ptoneclk.exe"
        #     os.startfile(codePath)

        # elif 'scratch' in query:
        #     codePath = "C:\Program Files (x86)\Scratch 2\Scratch 2.exe"
        #     os.startfile(codePath)

        # elif 'python' in query:
        #     codePath = "C:\Program Files\Python39\python.exe"
        #     os.startfile(codePath)

        # elif 'video' in query:
        #     codePath = "C:\Program Files\FlashIntegro\VideoEditor\VideoEditor.exe"
        #     os.startfile(codePath)

        elif "capture" in query:
            myButton = tk.Button(text='Take Screenshot', command=takeScreenshot, bg='green',fg='white',font= 10)
            canvas1.create_window(150, 150, window=myButton)

            root.mainloop()

        #Sia
        elif 'prototype' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Sia\\Sia.py"
            os.startfile(codePath)

        #Mark
        elif 'mark' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Mark\\Mark.py"
            os.startfile(codePath)

        #Screen
        elif 'screen recognition' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Edith\\Edith.py"
            os.startfile(codePath)

        #Friday
        elif 'friday' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Friday"
            os.startfile(codePath)

        #Viacc
        elif 'calculator' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Viacc\\Viacc.py"
            os.startfile(codePath)
            

        #Ultron
        elif 'reminder' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Ultron\\Ultron.py"
            os.startfile(codePath)

        #Map
        elif 'destination' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Maps\\Maps.py"
            os.startfile(codePath)

        #Shop
        elif 'shop' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Shop\\Shop.py"
            os.startfile(codePath)

        #Audiobook
        elif 'book' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Audiobook"
            os.startfile(codePath)

        #QRC
        elif 'code' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\QRcode\\QRcode.py"
            os.startfile(codePath)

        #FridayV2
        elif 'object' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\FridayV2\\FridayV2.py"
            os.startfile(codePath)

        #Timer
        elif 'timer' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\Timer\\Timer.py"
            os.startfile(codePath)

        #LanguageTranslator
        elif 'translator' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\LanguageTranslator\\LanguageTranslator.py"
            os.startfile(codePath)

        #Screen Recorder
        elif 'video capture' in query:
            codePath = "C:\\Users\\shrey\\Desktop\\Automated\\ScreenRecorder\\ScreenRec.py"
            os.startfile(codePath)          

        elif 'quit' in query:
            quit()
            

        elif 'send email' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                speak("Whom Should I send the email")
                query = input("Whom should I send the email")
                to = (my_dict[query])
                sendEmail(to, content)
                speak("Email has been sent")

            except Exception as e:
                print (e)
                speak("Sorry cannot send mail")  
