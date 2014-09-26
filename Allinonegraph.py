import kivy
from kivy.graphics import Rectangle,Line,Color
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.actionbar import ActionBar,ActionButton,ActionView
from kivy.uix.modalview import ModalView
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty,AliasProperty
from kivy.logger import Logger
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.metrics import dp,sp
from kivy.app import App
from kivy import platform
#from time import strftime, strptime
from random import randint
from datetime import datetime,timedelta

from json import load, dump
from kivy.uix.textinput import TextInput

kivy.require('1.0.7')

class hourAxis(RelativeLayout):

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(hourAxis, self).__init__(**kwargs)

        #self.log2=kwargs['log2']
        self.draw()


class AllInOneGraph(RelativeLayout):
    offset_x=sp(50)
    offset_y=sp(50)

    #h=600
    #w=600
    n_days=10
    n_seconds=24*60*60
    #day_height=h/n_days
    #offset_yd=offset_y + day_height/2
    #second_width=float(w)/n_seconds

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(AllInOneGraph, self).__init__(**kwargs)
        self.log2=kwargs['log2']
        #self.init_variables()

    def init_variables(self):
        self.h=self.height-2*self.offset_y
        self.w=self.width-2*self.offset_x
        self.day_height=self.h/self.n_days
        self.offset_yd=self.offset_y + self.day_height/2
        self.second_width=float(self.w)/self.n_seconds

    def paint_hour_axis(self):

        hour0 = datetime(2010,1,1)
        for ihour in xrange(24):
            hour1 = hour0- timedelta(hours=ihour)
            label_date =Label(text=hour1.strftime("%H"),font_size=sp(12),size_hint=(None,None),size=(0,0))
            label_date.pos = (self.offset_x + hour1.hour*3600*self.second_width, self.offset_y)
            self.add_widget(label_date)

    def paintAll(self):
        self.canvas.clear()
        self.init_variables()
        print self.n_seconds, "seconds; sec_w: ", self.second_width, self.day_height

        self.paint_hour_axis()

        with self.canvas:
            Color(0.8,0.3,0.1)
            #Line(rectangle=(offset_x,offset_y,w,day_height),width=1)
            #Line(rectangle=(offset_x,offset_y,w,h),width=1)
            #Line(rectangle=(offset_x,offset_y+2*day_height,12*60*60*second_width,h),width=1)

        endday = datetime.now()
        endday = datetime(endday.year,endday.month,endday.day)
        #position anhand der zeit bestimmen:
        #y = (day - startday)* dayheight
        #dayheight =
        #x = secondofday-startsecond )*secondwidth + x_offset
        for iday in xrange(self.n_days):
            date1 = endday - timedelta(days=iday)
            label_date =Label(text=date1.strftime("%m-%d"),font_size=sp(13),size_hint=(None,None),size=(0,0))
            label_date.pos = (20, self.offset_yd+ (endday-date1).days * self.day_height)
            self.add_widget(label_date)

        self.offset_yd +=self.day_height




        for entry in self.log2:
            try:
                date1 = datetime.strptime(str(entry[6]),"%Y-%m-%d %H:%M")
                col = self.rgb_from_string(str(entry[1]))

                print "paint: x,y, color: ", col,(endday-date1).days, entry[1]
                if (endday-date1).days >= self.n_days or (endday-date1).days <-1:
                    #print "too long ago or in the future...", (endday-date1).days; entry
                    continue
                if entry[2]=='singleevent':
                    #paint circle and label
                    x = self.offset_x + (date1.hour*3600+date1.minute*60) * self.second_width
                    y = self.offset_yd + (endday-date1).days * self.day_height
                    print "paint singleevent: x,y",x,y
                    with self.canvas:
                        #Line(rectangle=(x,y,day_height,day_height),width=3)
                        Color(col[0],col[1],col[2])
                        Line(circle=(x,y,10),width=2)
                    label_singleevent = Label(text=str(entry[1]),font_size=sp(12),size_hint=(None,None),size=(0,0),pos=(x,y))
                    self.add_widget(label_singleevent)
                elif entry[2]=='startstop':
                    date2 = datetime.strptime(str(entry[8]),"%Y-%m-%d %H:%M")
                    x1 = self.offset_x + (date1.hour*3600+date1.minute*60) * self.second_width
                    y1 = self.offset_yd-self.day_height/4 + (endday-date1).days * self.day_height

                    if date2.day == date1.day:
                        x2 = self.offset_x + (date2.hour*3600+date2.minute*60) * self.second_width
                        y2 = self.offset_yd+day_height/4 + (endday-date2).days * self.day_height
                    elif date2.day ==date1.day + 1:
                        x2 = self.offset_x + (23*3600+59*60) * self.second_width
                        y2 = self.offset_yd+self.day_height/4 + (endday-date1).days * self.day_height
                    print "paint startstop: x,y,x2,y2",x1,y1,x2,y2
                    with self.canvas.before:
                        Color(col[0],col[1],col[2])
                        Line(rectangle=(x1,y1,x2-x1,y2-y1),width=2)
                        Rectangle(pos=(x1,y1),size=(x2-x1,y2-y1))
                    #paint a rectangle from start to stop
                    label_startstop = Label(text=str(entry[1]),font_size=sp(12),size_hint=(None,None),size=(x2-x1,0),pos=(x1,y1))
                    self.add_widget(label_startstop)
                    #print str(entry[1]),sp(12),(x1,y1)


                elif entry[2]=='4times':
                    date2 = datetime.strptime(str(entry[8]), "%Y-%m-%d %H:%M")
                    date3 = datetime.strptime(str(entry[10]),"%Y-%m-%d %H:%M")
                    date4 = datetime.strptime(str(entry[12]),"%Y-%m-%d %H:%M")

                    x1 = self.offset_x + (date1.hour*3600+date1.minute*60) * self.second_width
                    y1 = self.offset_yd-self.day_height/4 + (endday-date1).days * self.day_height
                    x2 = self.offset_x + (date2.hour*3600+date2.minute*60) * self.second_width
                    y2 = self.offset_yd+self.day_height/4 + (endday-date2).days * self.day_height
                    x3 = self.offset_x + (date3.hour*3600+date3.minute*60) * self.second_width
                    y3 = self.offset_yd-self.day_height/4 + (endday-date3).days * self.day_height
                    x4 = self.offset_x + (date4.hour*3600+date4.minute*60) * self.second_width
                    y4 = self.offset_yd+self.day_height/4 + (endday-date4).days * self.day_height
                    print "paint 4times: x,y,x2,y2...",x1,x2,x3,x4,x1,"x||y: ", y1,y2,y3,y4,(endday-date1).days,(endday-date2).days,(endday-date3).days,(endday-date4).days, "||||", date1.day
                    with self.canvas.before:
                        Color(col[0],col[1],col[2],0.5)
                        Line(rectangle=(x1,y1,x4-x1,y4-y1),width=2)
                        Rectangle(pos=(x1,y1),size=(x4-x1,y4-y1))
                        Rectangle(pos=(x2,y2),size=(x3-x2,y3-y2))
                    #paint a rectangle from start to stop
                    label_startstop = Label(text=str(entry[1]),font_size=sp(12),size_hint=(None,None),size=(x2-x1,0),pos=(x1,y1))
                    self.add_widget(label_startstop)
                    #print str(entry[1]),sp(12),(x1,y1)
            except Exception, e:
                Logger.error("Paint-log-error" + str(e) + str(entry))
                print "errorororor"


    def rgb_from_string(self,string):
        try:
            r = float( len(string) % 12 ) / 12
            g = float( ord(string[0]) % 33) / 33
            b = float( ord(string[1]) % 24) / 24
        except Exception, e:
            Logger.error("rgb_from_string failed... string: '" + str(string) + "'; " +str(e) )
            r,g,b = 0.6,0.5,0.6
        return [r,g,b]


    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            self.paintAll()

