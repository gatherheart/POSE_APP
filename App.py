#!/usr/bin/env python3
from kivy.graphics import Color, Rotate, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from win10toast import ToastNotifier
from datetime import datetime
import webbrowser
import cv2
import requests

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0.3281, 0.3789, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:
        size: (420, 420)
        pos: (280, 0)

        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                # self here refers to the widget i.e BoxLayout
                pos: self.pos
                size: self.size

        Image:
            source: 'logo.png'
            pos: (-350, 0)
            size: (50, 50)

        Image:
            source: 'welcome.png'
            pos: (-100, 260)
            size: (15, 15)

        Label:
            text: 'Log in'
            color: (0.4023, 0.4023, 0.4023, 1)
            font_size: 30
            halign: 'left'
            text_size: root.width, 30
            pos_hint: {'x':0.3, 'y':0.3}

        Label:
            text: 'Email'
            color: (0.6016, 0.6016, 0.6016, 1)
            font_size: 18
            halign: 'left'
            text_size: root.width-20, 20
            pos_hint: {'x':0.11, 'y':0.18}

        TextInput:
            id: identification
            size_hint: (0.5, 0.1)
            multiline:False
            font_size: 18
            pos_hint: {'x':0.12, 'y':0.55}
            background_color: (1,1,1,1)

        Label:
            text: 'Password'
            color: (0.6016, 0.6016, 0.6016, 1)
            halign: 'left'
            font_size: 18
            text_size: root.width-20, 20
            pos_hint: {'x':0.11, 'y':-0.03}

        TextInput:
            id: password
            multiline:False
            size_hint: (0.5, 0.1)
            password:True
            font_size: 18
            pos_hint: {'x':0.12, 'y':0.33}
            background_color: (1,1,1,1)

        Button:
            id: loginBtn
            text: 'login'
            pos_hint: {'x':0.25, 'y':0.05}
            size_hint: (0.2, 0.1)


<SettingsScreen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    FloatLayout: 
        Image:
            id: imageView
            source: '<random>.jpg'
            allow_stretch: True
            size: (960, 480)
            pos: (0, 0)
        ImageButton:
            id: submit
            source: 'camera.png'
            size_hint: (.15, .15)
            pos: (415, 20)
        Button:
            text: 'Back'
            on_press: 
                root.terminateCam()
                root.manager.current = 'running'
            size_hint: (.075, .05)

<RunningScreen>:
    canvas.before:
        Color:
            rgba: 0.3281, 0.3789, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:

        RotateImageButton:
            source: 'running2.png'
            on_press: 
                root.terminateCam()
                root.manager.current = 'settings'
            pos_hint: {'x':0.35, 'y':0.58}
            size_hint: (0.3, 0.3)

            canvas.before:
                PushMatrix

            canvas.after:
                PopMatrix

        Image:
            source: 'logo.png'
            pos: (0, -0.5)
            size: (50, 50)

        Image:
            id: runningText
            source: 'runningText.png'
            pos_hint: {'x':0.35, 'y':0.16}
            size_hint: (0.3, 0.3)

        ImageButton:
            id: reportBtn
            source: 'goToReport.png'
            pos_hint: {'x':0.4, 'y':0}
            size_hint: (0.2, 0.2)
<P>:
    Label:
        id: contents
        text: "Nothing" 
        size_hint: 0.6, 0.2
        pos_hint: {"x":0.2, "top":1}

    Button:
        id: outPopup
        text: "Back"
        size_hint: 0.8, 0.2
        pos_hint: {"x":0.1, "y":0.1}
""")


class ImageButton(ButtonBehavior, Image):
    def on_press(self):
        print('pressed')


class P(FloatLayout):
    def __init__(self, contents, **kwargs):
        super(P, self).__init__(**kwargs)
        self.ids.contents.text = contents


class RotateImageButton(ButtonBehavior, Image):

    def __init__(self, **kwargs):
        super(RotateImageButton, self).__init__(**kwargs)
        self.angle = 0
        self.evn = Clock.schedule_interval(self.update, 0.3)

    def on_press(self):
        print('pressed')

    def update(self, dt):
        with self.canvas.before:
            Rotate(origin=(490, 424.6), angle=self.angle)
        self.angle += dt * 1


# Declare both screens
class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.ids.loginBtn.on_press = self.login
        toaster = ToastNotifier()
        toaster.show_toast("Posture Notification", "Welcome to POSE!",
                           icon_path="./wrongPosture.ico",
                           duration=0)

    def on_enter(self, *args):
        print("Start")

    def login(self):
        payload = {"username": self.ids.identification.text, "password": self.ids.password.text}
        response = requests.post(url + '/userLogin', json=payload)
        global token
        try:
            token = response.json()['access_token']
            print(token)
            sm.transition.direction = 'right'
            sm.current = 'running'
        except Exception as e:
            print(e)
            show = P(contents="Wrong ID or Password")  # Create a new instance of the P class
            self.popupWindow = Popup(title="Popup Window", content=show, size_hint=(None, None), size=(200, 200))
            print(self.popupWindow)
            show.ids.outPopup.on_press = self.popupWindow.dismiss
            self.show_popup()

    def show_popup(self):
        self.popupWindow.open()  # show the popup

    def exit(self):
        exit(0)


class ReportScreen(Screen):

    def __init__(self, **kwargs):
        super(ReportScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        print("running")


class RunningScreen(Screen):

    def __init__(self, **kwargs):
        super(RunningScreen, self).__init__(**kwargs)
        self.ids.reportBtn.on_press = self.goToReport

    def on_enter(self, *args):
        print("running")
        self.count = 1
        self.capture = cv2.VideoCapture(0)  # init the camera
        self.cam = Clock.schedule_interval(self.send, 1.0)
        self.result = Clock.schedule_interval(self.recv, 30.0)
        pass

    def send(self, dt):
        try:
            grabbed, frame = self.capture.read()  # grab the current frame

            now = datetime.now()
            frame = cv2.resize(frame, (640, 480))  # resize the frame
            cv2.imshow('frame', frame)
            encoded, buffer = cv2.imencode('.jpg', frame)
            img_bytes = buffer.tobytes()
            files = {'image': img_bytes}

            r = requests.post(
                url + '/upload/' + now.strftime("%d-%m-%Y-%H:%M:%S") + "_" + str(self.count) + '_' + '.jpg',
                files=files,
                headers={'Authorization': 'Bearer ' + token})

            self.count += 1

        except Exception as e:
            print(e)

    def recv(self, dt):
        try:
            self.ids.runningText.source = "waitingText.png"

            res = (requests.get(url + '/parse', headers={'Authorization': 'Bearer ' + token}).json())
            if res['MFP'] != '0':
                toaster = ToastNotifier()
                toaster.show_toast("Posture Notification", "Wrong Posture detected!",
                           icon_path="./wrongPosture.ico",
                           duration=0)

            self.ids.runningText.source = "runningText.png"
        except Exception as e:
            print(e)

    def terminateCam(self):
        print("Terminate")
        cv2.destroyAllWindows()
        self.cam.cancel()
        self.capture.release()

    def goToReport(self):
        targetUrl = url.split(':')[1]+":8020/admin/"+token
        print(targetUrl)
        webbrowser.get('chrome').open('http:'+targetUrl)

    def callback(self):
        print('The button is being pressed {}'.format(1))
        self.show_popup()


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        print("SetInit")
        print(self.ids)

        self.img1 = Image()
        self.ids.imageView.texture = self.img1.texture
        self.ids.submit.on_press = self.callback

        show = P(contents="Successfully Set")  # Create a new instance of the P class
        self.popupWindow = Popup(title="Popup Window", content=show, size_hint=(None, None), size=(200, 200))
        print(self.popupWindow)
        show.ids.outPopup.on_press = self.popupWindow.dismiss

    def on_enter(self, *args):
        self.capture = cv2.VideoCapture(0)
        cv2.namedWindow("CV2 Image")
        self.cam = Clock.schedule_interval(self.update, 1.0 / 33.0)
        pass

    def update(self, dt):
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        self.image = frame
        overlay = cv2.resize(cv2.imread('human_line.png'), (frame.shape[1], frame.shape[0]))
        added_image = cv2.addWeighted(frame, 1, overlay, 1, 0)
        cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(added_image, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.ids.imageView.texture = texture1

    def terminateCam(self):
        print("Terminate")
        cv2.destroyAllWindows()
        self.cam.cancel()
        self.capture.release()

    def callback(self):
        print('The button is being pressed {}'.format(1))
        cv2.imwrite('image.jpg', self.image)
        encoded, buffer = cv2.imencode('.jpg', self.image)
        img_bytes = buffer.tobytes()
        files = {'image': img_bytes}

        r = requests.post(
            url + '/initialSet',
            files=files,
            headers={'Authorization': 'Bearer ' + token})

        self.show_popup()
        print(r.json())

    def show_popup(self):
        self.popupWindow.open()  # show the popup


# Create the screen manager
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(RunningScreen(name='running'))

# Configuration
url = 'http://52.69.0.213:8000'
chrome_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome_path),1)

class TestApp(App):
    def build(self):
        return sm

if __name__ == '__main__':
    Window.size = (980, 580)
    TestApp().run()

