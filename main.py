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
from kivy.uix.scatterlayout import ScatterLayout
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
#from Allinonegraph import *

from json import load, dump
from kivy.uix.textinput import TextInput
#from traits.trait_types import self

import sqlite3

connlog = None

kivy.require('1.0.7')

__version__ = "0.3.19"


class AllInOneGraph(RelativeLayout):
    offset_x=sp(50)
    offset_y=sp(50)
    n_days=10
    n_seconds=24*60*60

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        self.size = (600,600)

        super(AllInOneGraph, self).__init__(**kwargs)
        self.conlog = kwargs['conlog']
        try:
            self.log_def=kwargs['log_def']
        except:
            try:
                self.n_days = kwargs['n_days']
            except:
                self.n_days = 6
            endday = datetime.now()
            #endday = datetime(2015,4,23)
            #endday = datetime(endday.year,endday.month,endday.day)
            self.log_def={'n_days':self.n_days, 'size':(1400,1200), 'endday':endday,'font_size':11}
        self.init_variables()
        #self.init_variables()

    def init_variables(self):
        self.h=self.height-2*self.offset_y
        self.w=self.width-2*self.offset_x
        self.day_height=self.h/self.n_days
        self.offset_yd=self.offset_y + self.day_height/2
        self.second_width=float(self.w)/self.n_seconds

        self.endday = self.log_def['endday']
        self.n_days = self.log_def['n_days']

        self.font_size = self.log_def['font_size']

    def paint_hour_axis_orig(self):
        hour0 = datetime(2010,1,1)
        for ihour in xrange(24):
            hour1 = hour0- timedelta(hours=ihour)
            label_date =Label(text=hour1.strftime("%H"),font_size=sp(12),size_hint=(None,None),size=(0,0))
            label_date.pos = (self.offset_x + hour1.hour*3600*self.second_width, self.offset_y)
            self.add_widget(label_date)

    def paint_hour_axis(self):
        for ihour in xrange(24):
            label_date =Label(text=str(ihour),font_size=sp(12),size_hint=(None,None),size=(0,0))
            label_date.pos = (self.get_pos_x_for_mainchart_from_hour(ihour),self.offset_y)#(self.offset_x + ihour*3600*self.second_width, self.offset_y)
            self.add_widget(label_date)


    def get_hours_from_2_dates(self,date1,date2):
        return (date2-date1).seconds / float(3600)

    def entry2hours(self,entry):
        if entry[2]=='startstop':
            date1 = datetime.strptime(str(entry[6]),"%Y-%m-%d %H:%M")
            date2 = datetime.strptime(str(entry[8]),"%Y-%m-%d %H:%M")
        elif entry[2]=='4times':
            date1 = datetime.strptime(str(entry[8]),"%Y-%m-%d %H:%M")
            date2 = datetime.strptime(str(entry[10]),"%Y-%m-%d %H:%M")
        else:
            return 0.1
        return self.get_hours_from_2_dates(date1,date2)


    def get_value_from_log2_entry(self,entry,valname):
        if valname=="_length":
            return self.entry2hours(entry)
        elif entry[13]==valname:
            return entry[14]
        elif entry[15]==valname:
            return entry[16]
        elif entry[17]==valname:
            return entry[18]
        elif entry[19]==valname:
            return entry[20]
        else:
            return entry[14]

    def test_paint_line_sql(self):
        try:
            sqltext = "SELECT * FROM lines " \
                      "WHERE prio > 0 " \
                      "ORDER BY prio DESC;"
            c = connlog.cursor() #self.conlog.cursor()
            c.execute(sqltext)
            result = c.fetchall()
            for linedef in result:
                if linedef['visible'] != 0:
                    self.paint_line_select(linedef)
        except:
            sqltext = '''CREATE TABLE IF NOT EXISTS `lines` (
                `lineID`	INTEGER PRIMARY KEY AUTOINCREMENT,
                `min`	INTEGER,
                `max`	INTEGER,
                `width`	INTEGER,
                `prio`	INTEGER,
                `zeroifnot`	INTEGER,
                `select_statement`	TEXT,
                `group`	INTEGER,
                `type`	TEXT,
                `name`	TEXT,
                `visible` INTEGER DEFAULT 1
                );'''
            c = connlog.cursor() # self.conlog.cursor()
            c.execute(sqltext)


    def paint_line_select(self,description):
        #button_id 0, 1entryname,type 2,note 3,categories 4, timename1 5,time1 6,timename2,time2 8,timename3,time3,timename4,time4 12, valuename1 13,value1 14,valuename2 15,value2 16,valuename3,value3 18 ,valuename4,value4 20

        endday = datetime.now()
        endday = datetime(endday.year,endday.month,endday.day)

        points = []
        offset_x = self.width
        offset_y = self.offset_y
        available_width= int(description['width'])
        min,max = description['min'], description['max']
        c = connlog.cursor() # self.conlog.cursor()
        #print "between paint_line....sql...."
        sqltext = description['select_statement'].replace('n_days',str(self.n_days)) # "SELECT * FROM log WHERE ((time1 between date('now', '-" + str(self.n_days) + " days') and date('now', '+1 days')) AND (button_id=" + str(description['button_id']) + "));"
        #print sqltext
        c.execute(sqltext)
        result = c.fetchall()
        last_date = datetime(2010, 1, 1)
        #print last_date, result
        for entry in result:
                #print "row:  ", entry
            try:
                #entry = entry[1:]
                #print "paint_line_select, entry: ", entry
                #print entry["value"]
                date1 = datetime.strptime(str(entry['time1']), "%Y-%m-%d %H:%M")
                if ((date1 - last_date).days > 1):
                    if (last_date != datetime(2010,1,1)):
                        #print "GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP",(date1 - last_date).days
                        if description['zeroifnot']:
                            for igapday in xrange((date1.day - last_date.day)-1):
                                last_date = last_date + timedelta(days=1)
                                points.extend((offset_x,self.get_pos_y_from_date(last_date,0.9)))
                last_date = date1
                value = entry['value'] # self.get_value_from_log2_entry(entry, entry['valuename1'])
                #print "minmax,value...:", min,max,value,entry
                x=offset_x + available_width / (max-min) * (value - min)
                #determine y: from the date. like in paint_all:
                y = self.get_pos_y_from_date(date1,date1.hour/24.0)
                #print (endday-date1).days,(endday-date1).seconds,"; s/24:", (float((endday-date1).seconds) / 60 / 60/24), "x,y: ", x,y, "entry: ", entry

                with self.canvas:
                    Rectangle(pos=(x,y),size=(sp(8),sp(8)))
                    #Line(circle=(x,y,2),width=1)
                txt = str(round(float(str(value)),2))
                txt = str(entry["text"])+":     " + txt
                y=y+sp(12)
                label_singleevent = Label(text=txt,font_size=sp(11),size_hint=(None,None),size=(0,0),pos=(x,y))
                self.add_widget(label_singleevent)
                #points.append((x,y))
                points.extend((x,y))

            except Exception, e:
                Logger.error("Paint-line-log-error" + str(e) + str(entry))
        label_linename = Label(text=description['name'],font_size=sp(16),size_hint=(None,None),size=(0,0),pos=(x,y-sp(26)))
        self.add_widget(label_linename)
        self.width += description['width']
        #print points, "points....<---"
        with self.canvas:
            Color(0.2,0.5,1.0,2)
            Line(points=points,width=1.6)
            Color(10,1.0,0.2,2.2)
            Line(bezier=points,width=1.9 )#,bezier_precision=100,cap='None')


    def paint_singleevent(self,entry,date,label_extra_offset_y):
        #paint circle and label
        x = self.get_pos_x_for_mainchart(date)
        y = self.get_pos_y_from_date(date)#self.offset_yd + (endday-date1).days * self.day_height
        #print "paint singleevent: x,y",x,y, entry[16], " - entry 18: ", entry[18]
        col = self.rgb_from_string(str(entry["entryname"]))
        with self.canvas:
            #Line(rectangle=(x,y,day_height,day_height),width=3)
            Color(col[0],col[1],col[2])
            Rectangle(pos=(x,y),size=(sp(10),sp(10)))
            #Line(circle=(x,y,sp(10)),width=sp(3))
        self.paint_event_label(date,entry,label_extra_offset_y)

    def paint_rectangle_for_two_datetimes(self,date1,date2,col):
        x1 = self.get_pos_x_for_mainchart(date1)
        y1 = self.get_pos_y_from_date(date1,relative_pos_on_day=0)
        if date2.day == date1.day:
            x2 = self.get_pos_x_for_mainchart(date2)#self.offset_x + (date2.hour*3600+date2.minute*60) * self.second_width
            y2 = y1 + self.day_height*0.87# self.get_pos_y_from_date(date2,0.75)#self.offset_yd+self.day_height/4 + (self.endday-date2).days * self.day_height

            with self.canvas.before:
                Color(col[0],col[1],col[2],0.4)
                Rectangle(pos=(x1,y1),size=(x2-x1,y2-y1))

    def paint_rectangle_for_several_days(self,date1,date2,col):
        if date2.day == date1.day:
            self.paint_rectangle_for_two_datetimes(date1,date2,col)
        else:
            date1x=date1
            #print "before-for ------ several_days...",date1,date2,range((date2-date1).days)
            for iday in xrange((date2-date1).days):
                #print "|| several_days...",iday,date1,date2
                date2x = datetime(date1x.year,date1x.month,date1x.day,23,58)
                self.paint_rectangle_for_two_datetimes(date1x,date2x,col)
                date1x = datetime(date1x.year,date1x.month,date1x.day+1, 0, 4)

    def paint_event_label(self,date1,entry,label_extra_offset_y):
        x1 = self.get_pos_x_for_mainchart(date1)
        y1 = self.get_pos_y_from_date(date1,relative_pos_on_day=0.0)
        txt=str(entry['entryname']+": " + str(entry['value1']) + " " + str(entry['value2']) + " " + str(entry['value3']) + str(entry['value4']))
        label_startstop = Label(text=txt, font_size=sp(12),size_hint=(None,None),size=(5,0),pos=(x1,y1+label_extra_offset_y))
        label_extra_offset_y += sp(self.font_size)
        self.add_widget(label_startstop)

    def paint_startstop_event(self,entry,date1,label_extra_offset_y):
        date2 = datetime.strptime(str(entry['time2']),"%Y-%m-%d %H:%M")
        #x1 = self.get_pos_x_for_mainchart(date1)
        #y1 = self.get_pos_y_from_date(date1)
        col = self.rgb_from_string(str(entry['entryname']))
        self.paint_rectangle_for_several_days(date1,date2,col)
        self.paint_event_label(date1,entry,label_extra_offset_y)


    def paint_4times(self, entry,date1,label_extra_offset_y):
        date2 = datetime.strptime(str(entry['time2']), "%Y-%m-%d %H:%M")
        date3 = datetime.strptime(str(entry['time3']),"%Y-%m-%d %H:%M")
        date4 = datetime.strptime(str(entry['time4']),"%Y-%m-%d %H:%M")
        #print "paint 4times: x,y,x2,y2...",x1,x2,x3,x4,x1,"x||y: ", y1,y2,y3,y4,(endday-date1).days,(endday-date2).days,(endday-date3).days,(endday-date4).days, "||||", date1.day

        col = self.rgb_from_string(str(entry['entryname']))
        #self.paint_rectangle_for_two_datetimes(date1,date4,col)
        #self.paint_rectangle_for_two_datetimes(date2,date3,col)
        self.paint_rectangle_for_several_days(date1,date4,col)
        self.paint_rectangle_for_several_days(date2,date3,col)
        #paint a rectangle from start to stop
        self.paint_event_label(date1,entry,label_extra_offset_y)
        #print str(entry[1]),sp(12),(x1,y1)


    def paintAll(self):
        log_def = self.log_def
        endday=self.endday
        self.paint_hour_axis()
        self.paint_date_axis()

        #extra-offset: so that the labels dont overlap
        label_extra_offset_y=0
        print "before paint_all...sql....1"
        c = connlog.cursor() # self.conlog.cursor()
        sqltext = "SELECT * FROM log WHERE time1 between date('now', '-" + str(self.n_days) + " days') and date('now', '+1 days');"
        c.execute(sqltext)
        #print "before paint_line...after execute.sql....",sqltext
        result = c.fetchall()
        for entry in result:
            #print "row:  ", entry
            #entry = entry[1:]
            try:
                #date1 = datetime.strptime(str(entry[6]),"%Y-%m-%d %H:%M")
                #print "oentry: ", entry
                date1 = datetime.strptime(entry["time1"],"%Y-%m-%d %H:%M")
                #print "date1: ", date1

                if (endday-date1).days >= self.n_days or (endday-date1).days < -1:
                    #print "too long ago or in the future...check next entry... ", (endday-date1).days; entry
                    continue

                #extra-offset: so that the labels dont overlap
                if label_extra_offset_y > self.day_height /2 + sp(self.font_size):
                    label_extra_offset_y=0
                else:
                    label_extra_offset_y += sp(self.font_size)

                if entry['type']=='singleevent':
                    self.paint_singleevent(entry,date1,label_extra_offset_y)
                elif entry['type']=='startstop':
                    #print entry
                    self.paint_startstop_event(entry,date1,label_extra_offset_y)
                elif entry['type']=='4times':
                    #print entry
                    self.paint_4times(entry,date1,label_extra_offset_y)
            except Exception,e:
                print "Error painting event:  ", str(e)
        print "................................................------------------------------------------------------------------------------------------------------------------------------"
        self.test_paint_line_sql()

    def get_pos_y_from_date(self,date,relative_pos_on_day=0.5):
        '''get the y-position on the widget from the date. realative_pos_on_day should be between 0..1'''
        #timedelta.days gives an integer
        return self.offset_yd + self.day_height + (self.endday.date() - date.date()).days * self.day_height + (relative_pos_on_day-0.5) * self.day_height

    def get_pos_x_for_mainchart(self,date):
        return self.offset_x + (date.hour*3600+date.minute*60) * self.second_width


    def get_pos_x_for_mainchart_from_hour(self,hour):
        return self.offset_x + (hour*3600) * self.second_width

    def paint_date_axis(self):
        for iday in xrange(self.n_days):
            date1 = self.endday - timedelta(days=iday)
            label_date = Label(text=date1.strftime("%m-%d"),font_size=sp(13),size_hint=(None,None),size=(0,0))
            label_date.pos = (20, self.get_pos_y_from_date(date1, 0.5))
            self.add_widget(label_date)

    def rgb_from_string(self,string):
        try:
            r = float( len(string) % 10 ) / 15.0 + 0.25
            g = float( ord(string[0]) % 30) / 40.0 + 0.2
            b = (ord(string[1]) + ord(string[2])) % 30 / 40.0 + 0.25
        except Exception, e:
            Logger.error("rgb_from_string failed... string: '" + str(string) + "'; " +str(e) )
            r,g,b = 0.6,0.5,0.6
        return [r, g, b]

    def on_touch_down(self,touch):
        pass
        #if self.collide_point(*touch.pos):
            #print self.width, self.size, self.painted_width
        #    if self.painted_width <=100:
        #        self.paintAll()
        #return True



class QuantButton(Widget):
    '''Button with some special properties: different colors for different type-variables; long-press-event after 1.2 seconds pressing'''
    color = ListProperty([0.4,0.5,0.5,1])
    #text = StringProperty(",")
    timeStartPress = None
    status = None

    def __init__(self, **kwargs):
        #print "init quantbutton",kwargs
        self.register_event_type('on_long_press')
        self.register_event_type('on_press')
        self.dict = kwargs['dict']
        if 'text' in kwargs:
            self.text = kwargs['text']
        #print 'children' in self.dict, len(self.dict), self.dict
        if 'type' in self.dict:
            #print "type ist drin",
            if self.dict['type']=="log":
                self.color =[0.5,0.4,0.4,1]
            elif self.dict['type']=="singleevent":
                self.color =[0.5,0.5,0.4,1]
            elif self.dict['type']=="startstop":
                self.color =[0.5,0.4,0.3,1]
            elif self.dict['type']=="4times":
                self.color =[0.5,0.3,0.3,1]
            if 'status' in self.dict:
                #if self.dict['status']=='started':
                self.status = self.dict['status']
                if self.dict['status']=='started':
                    self.color = [0.6,0.5,0.5,1]
                    if 'lasttime' in self.dict:
                        self.text += "\n"+ str(self.dict['lasttime'])
                elif self.dict['status']=='inactive':
                    self.color = [0.5,0.5,0.4,1]
        super(QuantButton, self).__init__(**kwargs)

    def on_touch_down(self,touch):
        #print "quantmove ",touch
        if self.collide_point(*touch.pos):
            self.color = [0.3,0.5,0.5,1]
            touch.grab(self)
            self.timeStartPress = datetime.now()
            # accept the touch.
            return True


    def on_touch_up(self, touch):
        # here, you don't check if the touch collides or things like that.
        # you just need to check if it's a grabbed touch event
        if touch.grab_current is self:
            # don't forget to ungrab ourself, or you might have side effects
            touch.ungrab(self)
            if ((datetime.now() - self.timeStartPress).total_seconds() > 1.2):
                print "long press!"
                self.dispatch('on_long_press',touch)
            else:
                self.dispatch('on_press',touch)
            # and accept the last up
            return True

    def on_long_press(self,instance):
        pass
        #print "on_long_press", instance


    def on_press(self,instance):
        pass
        #print "on_press",instance

class Knob(Label):
    value=NumericProperty()
    real_value = 0
    min,max = NumericProperty(0),NumericProperty(100)
    allow_out_of_range = False
    step=0.1
    last_y = 0
    touch_start_x = 0

    def __init__(self, **kwargs):
        #print "init quantbutton",kwargs
        #print 'children' in self.dict, len(self.dict), self.dict
        if 'value' in kwargs:
            print "value ist drin",
            self.value = kwargs['value']
            self.real_value = self.value
        super(Knob, self).__init__(**kwargs)
        self.real_value = self.value

    def on_value(self,instance,value):
        self.text = str(value)
        self.real_value = value
        #round(self.real_value/self.step,0)*self.step

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.timeLastMove=datetime.now()
            self.last_y =touch.pos[1]
            self.touch_start_x = touch.pos[0]
            # accept the touch.
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            timediffseconds =(datetime.now() - self.timeLastMove).total_seconds()
            if timediffseconds <0.01:
                timediffseconds =0.01
            elif timediffseconds >1.9:
                timediffseconds=1.9
            minsize = min(self.width,self.height)
            factor = 0.000007 + 0.00015 * (float(self.touch_start_x - touch.x) / minsize)
            if factor <0.000004: factor = 0.000004
            elif factor >0.00006: factor=0.00006

            self.real_value = (self.real_value + factor * (self.max - self.min) * (touch.pos[1]-self.last_y) /timediffseconds)
            if self.real_value < self.min:
                self.real_value = self.min
            elif self.real_value > self.max:
                self.real_value = self.max
            self.value = round(self.real_value/self.step,0)*self.step
            self.last_y = touch.pos[1]
            self.timeLastMove=datetime.now()
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # don't forget to ungrab ourself, or you might have side effects
            touch.ungrab(self)
            # and accept the last up
            return True

class CustomSlider(BoxLayout):
    ltext = StringProperty()
    range = ListProperty()
    min,max = NumericProperty(0),NumericProperty(99)
    value = NumericProperty(1)
    sl = ObjectProperty()

    step = NumericProperty(0.1)

    def on_value(self,instance,value):
        self.sl.value = value

    def change_value(self,val):
        self.value = val

    def on_range(self,instance,value):
        self.min = float(value[0])
        self.max = float(value[1])
        self.sl.step=0.1
        #print "customSlider - on_range:  ",instance,value,self.range, self.min, self.sl.range, self.sl.min

    def on_step(self,instance,value):
        self.sl.step = value

class CustomKnob(BoxLayout):
    ltext = StringProperty()
    range = ListProperty()
    min,max = NumericProperty(0),NumericProperty(99)
    value = NumericProperty(1)
    sl = ObjectProperty()

    step = NumericProperty(0.1)

    def on_value(self,instance,value):
        self.sl.value = value

    def change_value(self,val):
        self.value = val

    def on_range(self,instance,value):
        self.min = float(value[0])
        self.max = float(value[1])
        self.sl.step=self.step#0.1
        #print "customSlider - on_range:  ",instance,value,self.range, self.min, self.sl.range, self.sl.min

    def on_step(self,instance,value):
        self.sl.step = value

class DateSlider(BoxLayout):
    syear = ObjectProperty()
    smonth = ObjectProperty()
    sday = ObjectProperty()
    shour = ObjectProperty()
    sminute = ObjectProperty()
    text = StringProperty()

    def __init__(self, **kwargs):
        super(DateSlider, self).__init__(**kwargs)
        try:
            now = datetime.strptime(kwargs['timestring'],"%Y-%m-%d %H:%M")
        except Exception, e:
            now = datetime.now()
        #print "build dateslider...now:", now

        if 'text' in kwargs:
            self.text = kwargs['text']
        else:
            self.text = 'time'

        label_text= Label(text=self.text)
        self.add_widget(label_text, 6)

        self.syear.step = 1
        self.syear.value = now.year
        self.syear.min = now.year-2
        self.syear.max = now.year+2

        self.smonth.step = 1
        self.smonth.value = now.month
        self.smonth.min = 1
        self.smonth.max = 12

        self.sday.step = 1
        self.sday.value = now.day
        self.sday.min = 1
        self.sday.max = 31

        self.shour.step = 1
        self.shour.value = now.hour
        self.shour.min = 0
        self.shour.max = 23

        self.sminute.step = 1
        self.sminute.value = now.minute
        self.sminute.min = 0
        self.sminute.max = 59

    def get_time_tuple(self):
        return [int(self.syear.value), int(self.smonth.value), int(self.sday.value), int(self.shour.value), int(self.sminute.value)]

    def get_datetime(self):
        return datetime(int(self.syear.value), int(self.smonth.value), int(self.sday.value), int(self.shour.value), int(self.sminute.value))

    def get_datetime_string(self):
        return datetime(int(self.syear.value), int(self.smonth.value), int(self.sday.value), int(self.shour.value), int(self.sminute.value)).strftime("%Y-%m-%d %H:%M")


class ButtonMenuView(BoxLayout):
    '''Menu that pops up after a long-press on a tap-button.
    offers possibillities to:
    * change the button-dict -->what information can be stored...
    * change the plot-dict -->
    '''

    def __init__(self, **kwargs):
        pass
        print "kwargs:",kwargs
        #title =


class EnterView2(BoxLayout):
    #dict={}
    categories = []
    parent_button_view =None
    calendars = []
    value_sliders = []
    text_input = None
    note_input = None

    def __init__(self, **kwargs):
        self.calendars=[]
        self.value_sliders=[]
        self.categories=[]
        try:
            self.dict=kwargs['dict']
            if 'categories' in kwargs:
                self.categories = kwargs['categories']
            if 'parent_button_view' in kwargs:
                self.parent_button_view=kwargs['parent_button_view']
            self.orientation='vertical'
            super(EnterView2, self).__init__(**kwargs)

            self.clear_widgets()
            #print "build EnterView --- dict:    ", self.dict

            label_text= Label()
            if 'text' in self.dict:
                label_text.text = self.dict['text']
            else:
                label_text.text = '_no text available_'
            self.add_widget(label_text)

            i = 0
            for date in self.dict['calendars']:
                lasttime=None
                if i ==0:
                    i +=1
                    if self.dict['type'] in ['startstop', '4times']:
                        if 'status' in self.dict:
                            if self.dict['status']=='started':
                                if 'lasttime' in self.dict:
                                    lasttime = self.dict['lasttime']
                                else:
                                    self.dict['lasttime'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                self.dict['status']='stopped'
                            else:
                                self.dict['status']='started'
                                self.dict['lasttime'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                self.cancelf()
                                return None
                        else:
                            self.dict['status']='started'
                            self.dict['lasttime'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            self.cancelf()
                            return None

                if 'name' in date:
                    print ", yes"
                    cal = DateSlider(text=date['name'],timestring=lasttime)
                else:
                    print ", no"
                    cal = DateSlider()
                self.add_widget(cal)
                self.calendars.append(cal)


            for slid in self.dict['sliders']:
                #print '----------slid',slid
                slider_wid = CustomKnob() #CustomSlider()
                slider_wid.value = float(slid['slider_def'])
                slider_wid.ltext=slid['slider_name']
                slider_wid.min = float(slid['slider_min'])
                slider_wid.max = float(slid['slider_max'])
                self.add_widget(slider_wid)
                self.value_sliders.append(slider_wid)

            #if 'textfield' in self.dict:
            #    if self.dict['textfield']:
            self.note_input=TextInput()
            self.add_widget(self.note_input)
            #----------

            bt_ok = Button()
            bt_ok.text = "OK"
            bt_ok.bind(on_press=self.log_entry)
            self.add_widget(bt_ok)
            bt_cancel = Button()
            bt_cancel.text = "cancel"
            bt_cancel.bind(on_press=self.cancelf)
            self.add_widget(bt_cancel)
        except Exception, e:
            Logger.error("couldn't create enterView - delete button? " + str(e)+ str(self.dict))
            label = Label(text="couldn't create enterView - delete button? " + str(e) + str(self.dict))
            self.add_widget(label)

    def cancelf(self,instance=None):
        try:
            self.parent_button_view.clear_widgets()
            self.parent_button_view.show_first_level()
        except:
            self.parent.clear_widgets()
            self.parent.show_first_level()

    def log_entry(self,instance=None):
        new_log_entry = {}
        #ID = randint(0,999999) #str(randint(100,9999))
        #new_log_entry['log_id']=ID
        datetimes=[]
        for datetime in self.calendars:
            datetimes_new = {}
            datetimes_new['timename']=datetime.text
            datetimes_new['datetime']=datetime.get_datetime_string()
            datetimes.append(datetimes_new)
        new_log_entry['datetimes'] = datetimes

        values=[]
        for val in self.value_sliders:
            val_new = {}
            val_new['valname']=val.ltext
            val_new['value']=val.value
            values.append(val_new)
        new_log_entry['values'] = values
        new_log_entry['categories']=self.categories

        if 'text' in self.dict:
            new_log_entry['entryname'] = str(self.dict['text'])
        else:
            new_log_entry['text'] = "None"
        if 'type' in self.dict:
            new_log_entry['type'] = str(self.dict['type'])
        if 'button_id' in self.dict:
            new_log_entry['button_id']=self.dict['button_id']

        new_log_entry['note'] = self.note_input.text

        catstring=''
        for category in self.categories:
            catstring += category + '|'

        log2_entry = self.log_entry_2_log2(new_log_entry)
        self.add_line_to_db_from_log2_entry(log2_entry)

        #self.parent_button_view.log.append(new_log_entry)
        #self.parent_button_view.log2.append(log2_entry)
        #print "log...  ", new_log_entry
        self.cancelf()

    def log_entry_2_log2(self,log1):
        #converts a dict-log-entry into a list-based log-entry
        log2=[]
        #button_id, entryname,type,note,categories,timename1,time1,timename2,time2,timename3,time3,timename4,time4,valuename1,value1,valuename2,value2,valuename3,value3,valuename4,value4
        if 'button_id' in log1:
            log2.append(log1['button_id'])
        else:
            log2.append(0)
        if 'entryname' in log1:
            log2.append(log1['entryname'])
        else:
            log2.append('no_name')
        if 'type' in log1:
            log2.append(log1['type'])
        else:
            log2.append('no_type')
        if 'note' in log1:
            log2.append(log1['note'])
        else:
            log2.append('no_note')
        categories = ""
        if 'categories' in log1:
            for cat in log1['categories']:
                categories += cat + "|"
            #categories = categories[:-1]
            categories += log1['entryname']
        else:
            categories = "root"
        log2.append(categories)

        if 'datetimes' in log1:
            log1time = log1['datetimes']
            i=0
            for time in log1time:
                i += 1
                if i <=4:
                    try:
                        log2.append(time['timename'])
                        log2.append(time['datetime'])
                    except Exception, e:
                        print "Error, couldnt add time1 " +str(i)+ str(e) + ";  " + time
                        log2.append("")
                        log2.append("")
            if i<4:
                for j in xrange(i,4,1):
                    log2.append("")
                    log2.append("")

        else:
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')


        if 'values' in log1:
            log1values = log1['values']
            i=0
            for value in log1values:
                i += 1
                if i <=4:
                    try:
                        log2.append(value['valname'])
                        log2.append(value['value'])
                    except Exception, e:
                        print "Error, couldnt add value "+str(i) + str(e) + ";  " + value
                        log2.append("")
                        log2.append("")
            if i<4:
                for j in xrange(i,4,1):
                    log2.append("")
                    log2.append("")
        else:
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
            log2.append('')
        Logger.info("new entry: " + str(log2))
        #self.add_line_to_db_from_log2_entry(log2)
        return log2

    def add_line_to_db_from_log2_entry(self,entry):
        print "add..line: ",entry
        print len(entry), "---", entry.insert(0,randint(0,999999))
        connlog.execute("INSERT INTO log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",entry)
        #Clock.schedule_once(lambda dt: self.parent.app.connlog.commit())
        #self.parent.app.connlog.commit()
        #self.convert_db()

    def convert_db(self, log2=None):
        """
        :param log2:
        :return:
        """
        #" (entryname, type     ,note   , categories , timename1 , time1, timename2, time2,
        #           timename3, time3 , timename4 ,  time4, valuename1, value1, valuename2,
        #           value2, valuename3, value3, valuename4 , value4"
        print len(self.parent_button_view.log2[2]), self.parent_button_view.log2[2:5]
        for line in self.parent_button_view.log2:
            try:
                connlog.execute(
                    """INSERT INTO log (button_id,entryname, type,note, categories, timename1 , time1, timename2, time2,
                           timename3, time3 , timename4 ,  time4, valuename1, value1, valuename2,
                           value2, valuename3, value3, valuename4 , value4) VALUES (?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?, ?,?,?,?, ?);""", line)
                print "funktioniert.....", line
            except:
                print "error....", line, len(line)
        print "jo"
        connlog.commit()

class NewEnterView2(BoxLayout):
    '''add a new button to the button-view'''

    ti_button_text = ObjectProperty()
    cb_type_log = ObjectProperty()
    cb_type_submenu = ObjectProperty()
    dict =[] #Button_dict of the level where the button is shown
    parent_button_view = None
    index_cal=0
    index_val=2
    slider_list=[]
    calendar_list=[]

    def __init__(self, **kwargs):
        super(NewEnterView2, self).__init__(**kwargs)
        self.parent_button_view=kwargs['parent_button_view']
        self.dict=kwargs['dict']
        self.slider_list=[]
        self.calendar_list=[]
        #self.parent_button_view.clear_widgets()
        #self.clear_widgets()
        self.on_cb4_newSubmenu(value=True)

    def add_name_field(self,buttontext=""):
        bl=BoxLayout()
        lab = Label(text='Button-Text')
        bl.add_widget(lab)
        self.ti_button_text = TextInput(text=buttontext)
        bl.add_widget(self.ti_button_text)
        self.add_widget(bl)

    def add_ok_cancel(self):
        bl= BoxLayout(orientation='horizontal')
        bt_ok = Button(text='OK')
        bl.add_widget(bt_ok)
        bt_ok.bind(on_press=self.okay)
        bt_cancel = Button(text='Cancel')
        bl.add_widget(bt_cancel)
        bt_cancel.bind(on_press=self.cancel)
        self.add_widget(bl)

    def add_type_choice(self,choice='newSubmenu'):
        bl = BoxLayout(orientation='horizontal')

        label1 = Label(text='single event')
        bl.add_widget(label1)
        self.cb1_singleEvent = CheckBox(group='type')
        if choice=='singleevent':
            self.cb1_singleEvent.active = True
        bl.add_widget(self.cb1_singleEvent)
        self.cb1_singleEvent.bind(active=self.on_cb1_singleEvent)

        label2 = Label(text='start stop')
        bl.add_widget(label2)
        self.cb2_startstop = CheckBox(group='type')
        if choice=='startstop':
            self.cb2_startstop.active = True
        bl.add_widget(self.cb2_startstop)
        self.cb2_startstop.bind(active=self.on_cb2_startstop)

        label3 = Label(text='4 times')
        bl.add_widget(label3)
        self.cb3_4times = CheckBox(group='type')
        if choice=='4times':
            self.cb3_4times.active = True
        bl.add_widget(self.cb3_4times)
        self.cb3_4times.bind(active=self.on_cb3_4times)

        label4 = Label(text='new submenu')
        bl.add_widget(label4)
        self.cb4_newSubmenu = CheckBox(group='type')
        if choice=='newSubmenu':
            self.cb4_newSubmenu.active = True
        bl.add_widget(self.cb4_newSubmenu)
        self.cb4_newSubmenu.bind(active=self.on_cb4_newSubmenu)

        self.add_widget(bl)

    def add_cal(self,instance=None,name='time1'):
        bl1_cal = BoxLayout(orientation='horizontal')
        lab1_cal = Label(text='DateTime-Slider')
        textinput_cal_name = TextInput(text=name)
        #but1_cal = Button(text='+',size_hint_x=0.2)
        #but1_cal.bind(on_press=self.add_cal)
        bl1_cal.add_widget(lab1_cal,0)
        bl1_cal.add_widget(textinput_cal_name,0)
        #bl1_cal.add_widget(but1_cal,0)
        self.add_widget(bl1_cal, self.index_val)
        self.index_cal +=1

        cal_dict1 = {'name':textinput_cal_name}
        self.calendar_list.append(cal_dict1)

    def add_val(self,instance=None):
        bl1_val = BoxLayout(orientation='horizontal')

        lab1_val = Label(text='Value-Slider')
        bl1_val.add_widget(lab1_val,0)

        lab11_val = Label(text='Name')
        bl1_val.add_widget(lab11_val,0)
        textinput_name = TextInput(text='value')
        bl1_val.add_widget(textinput_name,0)
        lab2_val = Label(text='Min')
        bl1_val.add_widget(lab2_val,0)
        textinput_min = TextInput(text='0')
        bl1_val.add_widget(textinput_min,0)
        lab3_val = Label(text='Max')
        bl1_val.add_widget(lab3_val,0)
        textinput_max = TextInput(text='10')
        bl1_val.add_widget(textinput_max,0)
        lab4_val = Label(text='default')
        bl1_val.add_widget(lab4_val,0)
        textinput_def = TextInput(text='5')
        bl1_val.add_widget(textinput_def,0)

        butplus_val = Button(text='+')
        butplus_val.bind(on_press=self.add_val)
        bl1_val.add_widget(butplus_val,0)
        self.add_widget(bl1_val, 1)#self.index_val)
        self.index_val +=1

        slide_dict1 = {'name':textinput_name,'min':textinput_min,'max':textinput_max,'default':textinput_def}
        self.slider_list.append(slide_dict1)
        print "sliderlist..... ",self.slider_list

    def add_text(self):
        bl1 = BoxLayout(orientation='horizontal')

        label1 = Label(text='Text-Input')
        bl1.add_widget(label1,0)

        checkbox1 = CheckBox(active=True)
        bl1.add_widget(checkbox1)

        self.add_widget(bl1,1)

    def on_cb1_singleEvent(self,instance=None,value=None):
        if value:
            buttontext=self.ti_button_text.text
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_name_field(buttontext)
            self.add_type_choice(choice='singleevent')

            print "on_cb1_singleEvent...",instance
            self.add_text()
            #add calender and '+'-button
            self.add_cal()
            #add value-widget and +button
            self.add_val()

            self.add_ok_cancel()

    def on_cb2_startstop(self,instance=None,value=None):
        if value:
            buttontext=self.ti_button_text.text
            print "on_cb2_startstop...",instance
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_type_choice(choice='startstop')
            self.add_name_field(buttontext)

            self.add_text()
            #add calender and '+'-button
            self.add_cal(name='start')
            self.add_cal(name='stop')
            #add value-widget and +button
            self.add_val()
            self.add_ok_cancel()

    def on_cb3_4times(self,instance=None,value=None):
        if value:
            buttontext=self.ti_button_text.text
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_type_choice(choice='4times')
            self.add_name_field(buttontext)

            print "on_cb3_4times...",instance
            self.add_cal(name='start1')
            self.add_cal(name='start2')
            self.add_cal(name='stop1')
            self.add_cal(name='stop2')
            self.add_val()
            self.add_ok_cancel()

    def on_cb4_newSubmenu(self,instance=None,value=None):
        if value:
            try:
                buttontext=self.ti_button_text.text
            except:
                buttontext=""
            print "on_cb4_newSubmenu...",instance
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_name_field(buttontext)
            self.add_type_choice(choice='newSubmenu')
            #
            self.add_ok_cancel()

    def okay(self,instance=None):
        try:
            newdict = {}
            print ".................................................................................."
            ID = randint(100,999999) #str(randint(100,9999))
            newdict['button_id']=ID
            newdict['text']=self.ti_button_text.text
            if self.cb1_singleEvent.active:
                newdict['type']= 'singleevent'
            elif self.cb2_startstop.active:
                newdict['type']= 'startstop'
            elif self.cb3_4times.active:
                newdict['type']= '4times'
            elif self.cb4_newSubmenu.active:
                newdict['type']= 'submenu'

            if  newdict['type'] in ['log','singleevent','startstop','4times']:
                sliders=[]
                print "sliderlist:  ", self.slider_list
                for slider in self.slider_list:
                    slid_={}
                    slid_['slider_name'] = slider['name'].text
                    slid_['slider_min'] =str(float(slider['min'].text))
                    slid_['slider_max'] =str(float(slider['max'].text))
                    slid_['slider_def'] =str(float(slider['default'].text))
                    sliders.append(slid_)
                newdict['sliders'] = sliders
                print "sliders:  ", sliders
                calendars=[]
                for dateentry in self.calendar_list:
                    cal_={}
                    cal_['name'] = str(dateentry['name'].text)
                    calendars.append(cal_)
                newdict['calendars']=calendars

                newdict['note']=True

            elif newdict['type']=='submenu':
                newdict['children'] = []
            else:
                print "no availible type!"
                return 0
            self.dict.append(newdict)
            print "newdict:   ", newdict
            self.cancel()
        except Exception, e:
            Logger.error("couldnt create new Button. " + str(e))

    def cancel(self,instance=None):
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()

class ButtonOptionsView(BoxLayout):
    '''Menu that shows options like: show entries from this button in the paint-log1 or 2... draw a graph...
        saves these options in: definitions.json and (maybe) in button_dict

    '''
    def __init__(self, **kwargs):
        super(ButtonOptionsView, self).__init__(**kwargs)
        self.button_dict=kwargs['button_dict']
        self.app = kwargs['app']
        self.size= sp(500),sp(800)
        print kwargs, "kwargs "
        #self.show_first_level()
        self.build_view()
        self.do_layout()

    def build_view(self):
        '''build the menu....'''

        print "build view....."
        #options:




class ButtonView(StackLayout):
    button_dict =[]#[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
    categories =[]
    app = None

    def __init__(self, **kwargs):
        super(ButtonView, self).__init__(**kwargs)
        self.button_dict=kwargs['button_dict']
        self.app = kwargs['app']
        self.size= sp(700),sp(700)
        #self.show_first_level()
        self.do_layout()
        self.show_first_level()
        #Clock.schedule_once(self.show_first_level,0.5)

    def show_first_level(self,instance=None):
        #Logger.info( "show_first_level 1 " + str(self.button_dict) + str(self.log2))
        self.categories = []
        self.clear_widgets()
        for button in self.button_dict:
            #print "show first level: ", button

            if 'children' in button:
                bt = QuantButton(text=button['text'],dict=button['children'],type='submenu')
            else:
                bt = QuantButton(text= button['text'],dict=button,type='log')
            bt.bind(on_press=self.buttonpress)
            bt.bind(on_long_press=self.edit_button)
            bt.size_hint = (None,None)
            bt.size = [self.width/2-5, self.height /6-5]
            self.add_widget(bt)
        self.add_add_button(dict=self.button_dict)

    def edit_button(self,instance,value=None):
        print "edit_button....",instance,value
        self.clear_widgets()
        bov = ButtonOptionsView(button_dict=self.button_dict,app=self.app)
        self.add_widget(bov)


    def show_button_dict(self,bdict,text):
        #print " ButtonView...show_button_dict",text
        self.clear_widgets()
        self.categories.append(text)
        categoryname_Label = Label()
        categoryname_Label.text = text
        categoryname_Label.size_hint = (None,None)
        categoryname_Label.size = [self.width -5, self.height /6-5]
        self.add_widget(categoryname_Label)
        for button in bdict:
            #print "buttondict - one button: ", button
            if 'children' in button:
                bt = QuantButton(text=button['text'],dict=button['children'],type='submenu')
            else:
                bt = QuantButton(text= button['text'],dict=button,type='log')
            bt.bind(on_press=self.buttonpress)
            bt.size_hint = (None,None)
            bt.size = [self.width/2-5, self.height /6-5]
            self.add_widget(bt)
        self.add_add_button(dict=bdict)

    def add_add_button(self,dict):
        bt = Button(text="+")
        bt.size_hint = (None,None)
        bt.size  = (self.width /2-5, self.height/6-5)
        bt.dict = dict
        bt.parent_button_view = self
        bt.bind(on_press=self.add_button)
        self.add_widget(bt)


    def add_button(self,instance,value=None):
        self.clear_widgets()
        av = NewEnterView2(parent_button_view=self,dict=instance.dict)
        #av.parent_button_view = self
        av.dict = instance.dict
        self.add_widget(av)

    def buttonpress(self,instance,value =None):
        #print "buttonpress..., ", instance, ";.. value: ", value, instance.dict, instance.text

        if type(instance.dict)==list:
            #-->submenu
            self.show_button_dict(instance.dict,instance.text)
        elif type(instance.dict)==dict:
            #-->entry
            #print "buttonview-buttonpress-instance.dict : ", instance.dict
            self.clear_widgets()
            ev = EnterView2(dict=instance.dict,categories=self.categories,parent_button_view=self)
            #ev.parent_button_view=self
            self.add_widget(ev)

class ListEntry(BoxLayout):

    def __init__(self, **kwargs):
        self.entry=kwargs['entry']
        super(ListEntry, self).__init__(**kwargs)
        #print self.entry

        for item in self.entry:
            try:
                lab = Label()
                lab.text = str(item)
                self.add_widget(lab)
                self.height = lab.texture_size[1]
            except Exception,e:
                Logger.error("error when showing the log...  " + str(e))


class ListEntry2(RelativeLayout):

    def __init__(self, **kwargs):
        #button_id, entryname,type,note,timename1,time1,timename2,time2,timename3,time3,timename4,time4,valuename1,value1,valuename2,value2,valuename3,value3,valuename4,value4
        self.entry=kwargs['entry']
        self.listindex = kwargs['listindex']
        #self.orientation = 'horizontal'
        super(ListEntry2, self).__init__(**kwargs)
        #print self.entry
        try:
            self.height=sp(75)
            #label_index = Label(text=str(self.listindex),size_hint=(0.04,0.5), pos_hint={'x':.0, 'y':.5})
            #self.add_widget(label_index)

            bl_date = BoxLayout(orientation='vertical',pos_hint={'x':.0, 'y':.0}, size_hint=(None,1),width=sp(40))
            try:
                date1 = datetime.strptime(str(self.entry['time1']),"%Y-%m-%d %H:%M")
                label_date1 = Label(text=date1.strftime("%H:%M"))
                bl_date.add_widget(label_date1)
                date2 = datetime.strptime(str(self.entry['time2']),"%Y-%m-%d %H:%M")
                if (date2-date1).seconds > 1:
                    label_date2 = Label(text=str(self.entry['time2'])[10:])
                    bl_date.add_widget(label_date2)
            except Exception, e:
                pass#Logger.error("Show Log- date-error" + str(e))
            self.add_widget(bl_date)

            label_name = Label(text=str(self.entry['entryname']),pos_hint={'x':.25, 'top':1}, size_hint=(None,0.4), size=(100,20))
            self.add_widget(label_name)
            label_categories = Label(text=str(self.entry['categories']),pos_hint={'x':.25, 'top':0.75}, size_hint=(None,0.4), size=(100,20))
            self.add_widget(label_categories)

            bl_value = BoxLayout(orientation='vertical',pos_hint={'x':.7}, size_hint=(0.15,1))
            label_value1 = Label(text=str(self.entry['valuename1']))
            label_value2 = Label(text=str(self.entry['valuename2']))
            bl_value.add_widget(label_value1)
            bl_value.add_widget(label_value2)
            self.add_widget(bl_value)

            bl_value = BoxLayout(orientation='vertical',pos_hint={'x':.89}, size_hint=(0.15,1))
            try:
                label_value1 = Label(text=str(round(float(str(self.entry['value1'])),2)))
                bl_value.add_widget(label_value1)
            except:
                pass
            try:
                label_value2 = Label(text=str(round(float(str(self.entry['value2'])),2)))
                bl_value.add_widget(label_value2)
            except:
                pass
            self.add_widget(bl_value)

            if len(self.entry['note'])>1:
                self.height +=sp(14)
                for row in self.entry['note'].split("\n"):
                    self.height +=sp(14)
                label_note = Label(text=self.entry['note'],pos_hint={'x':0.2, 'y':0.5}, size_hint=(0.6,0.3),text_size=(300,None),color=(0.4,1,1,1))
                self.add_widget(label_note)
                #print "label-size: ", label_note.size, label_note.texture_size,"self.x,y,w,h,pos,self...",(self.x,self.y,self.width,self.height), self.pos,self


        except Exception, e:
            Logger.error("couldn't create log-entry... "+ str(e))

    def on_touch_down(self,touch):
        if self.collide_point(*touch.pos):
            #print "touch list-entry ",touch, self.listindex
            #print "on_touch...pos listentry", self.pos,self.size, self.entry,self.size,touch
            return True

    def on_pos(self,instance=None,value=None):
        pass
        #print "on_pos listentry", self.entry, instance,value, self.pos,self.size
        #self.height = 66
        #with self.canvas:
        #    Line(rectangle=(self.x,self.y,self.parent.parent.width,3))

    def on_size(self,instance=None,value=None):
            pass
            #print "on_size...pos listentry", self.pos,self.size, self.entry,self.size
            # self.height = 66

class TestScrollableAllInOneGraph(RelativeLayout):

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(TestScrollableAllInOneGraph, self).__init__(**kwargs)
        self.log2=kwargs['log2']
        self.conlog=kwargs['conlog']
        try:
            self.n_days = kwargs['n_days']
        except:
            self.n_days = 10
        self.graph = ScrollableAllInOneGraph(log2=self.log2, conlog=self.conlog, size=(400,400),size_hint=(None,None),n_days=self.n_days)
        self.add_widget(self.graph)

        self.graph.paintAll()

    def paintAll(self):
        pass#self.graph.paintAll()

class ScrollableAllInOneGraph(ScrollView):
    conlog=None

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(ScrollableAllInOneGraph, self).__init__(**kwargs)
        self.conlog=kwargs['conlog']
        self.scroll_x = 0.0
        self.scroll_y = 0
        try:
            self.n_days = kwargs['n_days']
        except:
            self.n_days = 10
        try:
            size = (sp(kwargs['size_inside'][0]),sp(kwargs['size_inside'][1]))
        except:
            size = (sp(1000),sp(1400))

        self.graph = AllInOneGraph(conlog=self.conlog, size=size,size_hint=(None,None),n_days=self.n_days)
        self.add_widget(self.graph)

        self.graph.paintAll()

    def paintAll(self):
        self.graph.paintAll()



class MainView(BoxLayout):
    bv = None
    app = None
    log =None
    log2=None
    connlog=None
    button_dic =None
    n_days=8

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(MainView, self).__init__(**kwargs)
        self.button_dict=kwargs['button_dict']
        #connlog = kwargs['connlog']
        self.app = kwargs['app']
        self.bv = ButtonView(button_dict=self.button_dict,app=self.app,connlog=connlog)
        self.add_widget(self.bv)


    def list_log(self,instance=None):
        #print "### the whole log: ", self.log
        self.bv.clear_widgets()
        scrollview= ScrollView()
        gridlayout = GridLayout(cols=1,spacing=5,size_hint_y =None)

        gridlayout.size_hint_y =None
        sqltext = "SELECT * FROM log WHERE time1 between date('now', '-5 days') and date('now', '+1 days') ORDER BY time1;"
        c = connlog.cursor()
        c.execute(sqltext)
        result = c.fetchall()
        for entry in result:
            #entry = entry[1:]
            if type(entry) is list:
                print "is list??!?!", entry
                pass
            else:
                entryp = ListEntry(entry=entry)
                entryp.height =100
                gridlayout.add_widget(entryp)
                gridlayout.height += entryp.height
                #print "hhh: ", entryp.height, gridlayout.height
        scrollview.add_widget(gridlayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0

    def list_log_txt(self,instance=None):
        #print "### the whole log: ", self.log
        self.bv.clear_widgets()
        scrollview= ScrollView()
        gridlayout = GridLayout(cols=1,spacing=5,size_hint_y =None)

        gridlayout.size_hint_y =None
        sqltext = "SELECT categories, entryname, note, valuename1,value1, valuename2,value2, valuename3,value3, valuename4,value4,timename1,time1,timename2,time2,timename3,time3,timename4,time4 FROM log WHERE time1 between date('now', '-14 days') and date('now', '+1 days') ORDER BY time1;"
        c = connlog.cursor()
        c.execute(sqltext)
        result = c.fetchall()
        for entry in result:
            txt = ""
            print entry
            for col in entry:
                print col
                txt += str(col) + "  "
            entryp = Label(text=txt,color=(0.8,1,0.8,1),font_size=sp(16),size_hint=(1,None))
            entryp.height = sp(20)
            gridlayout.add_widget(entryp)
            gridlayout.height += entryp.height + sp(5)
            #print "hhh: ", entryp.height, gridlayout.height
        scrollview.add_widget(gridlayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0

    def list_log2(self,instance=None):
        #print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        scrollview= ScrollView()
        stacklayout = StackLayout(cols=1,spacing=5,size_hint_y =None)
        i=0
        lastdate = datetime(2010,1,1,0,0)
        sqltext = "SELECT * FROM log WHERE time1 between date('now', '-4 days') and date('now', '+1 days') ORDER BY time1;"
        c = connlog.cursor()
        c.execute(sqltext)
        result = c.fetchall()
        for entry in result:
            #entry = entry[1:]
            try:
                date1 = datetime.strptime(str(entry['time1']),"%Y-%m-%d %H:%M")
                #print date1, date1-lastdate, (date1-lastdate).days
                if (abs((date1-lastdate).days) >= 1 ):
                    lastdate = datetime(date1.year,date1.month,date1.day)
                    date_label = Label(text=date1.strftime("%A,    %Y-%m-%d"),color=(0.7,1,0.8,1),font_size=sp(16),size_hint=(1,None))
                    stacklayout.add_widget(date_label)
                    date_label.height = sp(38)
                    stacklayout.height += date_label.height + 4
                entryp = ListEntry2(entry=entry,listindex=i,size_hint=(1,None), height = sp(80))
                stacklayout.add_widget(entryp)
                stacklayout.height += entryp.height + 4
                #print "entryp-height: ", entryp.height, stacklayout.height
                i += 1
            except Exception, e:
                pass#Logger.error("ListLog2 - couldn't create entry number " + str(i) + str(entry) + str(e))
        scrollview.add_widget(stacklayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0

    def entry2rst(self,entry,listindex=1):
        txt= "\n\n"
        #print entry
        #print "linex:   " + str(entry[1]).encode('utf8', 'replace') + " | " + str(entry[2]).encode('utf8', 'replace')
        #
        txt += "" + str(entry['type']) + " "+ (" " * (max(0,14-(len(str(entry['type']))))))
        txt += " " + str(entry['entryname']) + "     " + (" " * (max(0,14-(len(str(entry['entryname']))))))
        txt += " " + str(entry[4+1]) + "     " + (" " * (max(0,14-(len(str(entry['entryname']))))))
        txt += " " + str(entry[3+1]) + "     " + (" " * (max(0,14-(len(str(entry['entryname']))))))
        txt += "\n\n"

        txt += "  " + str(entry[13+1]) + "  : "+ (" " * (max(0,14-(len(str(entry[13+1]))))))
        txt += " " + str(entry[14+1]) + "  ;     "+ (" " * (max(0,14-(len(str(entry[14+1]))))))
        txt += "  " + str(entry[15+1]) + "  : "+ (" " * (max(0,14-(len(str(entry[15+1]))))))
        txt += " " + str(entry[16+1]) + "  ;     "+ (" " * (max(0,14-(len(str(entry[16+1]))))))
        txt += "  " + str(entry[17+1]) + "  : "+ (" " * (max(0,14-(len(str(entry[17+1]))))))
        txt += " " + str(entry[18+1]) + "  ;     "+ (" " * (max(0,14-(len(str(entry[18+1]))))))
        txt += "  " + str(entry[19+1]) + "  : "+ (" " * (max(0,14-(len(str(entry[19+1]))))))
        txt += " " + str(entry[20+1]) + "  ;     "+ (" " * (max(0,14-(len(str(entry[20+1]))))))

        txt += "\n\n"
        txt += "" + str(entry[5+1]) + ":  "+ (" " * (max(0,14-(len(str(entry[6+1]))))))
        txt += " " + str(entry[6+1]) + " ;     "+ (" " * (max(0,14-(len(str(entry[7+1]))))))
        txt += "" + str(entry[7+1]) + ": "+ (" " * (max(0,14-(len(str(entry[8+1]))))))
        txt += " " + str(entry[8+1]) + " ;      "+ (" " * (max(0,14-(len(str(entry[9+1]))))))
        txt += "" + str(entry[9+1]) + ": "+ (" " * (max(0,14-(len(str(entry[10+1]))))))
        txt += " " + str(entry[10+1]) + " ;      "+ (" " * (max(0,14-(len(str(entry[11+1]))))))
        txt += "" + str(entry[11+1]) + ": "+ (" " * (max(0,14-(len(str(entry[10+1]))))))
        txt += " " + str(entry[12+1]) + " ;      "+ (" " * (max(0,14-(len(str(entry[11+1]))))))
        txt += "\n\n-----------------------------\n\n"
        return txt

    def list_log3_rst(self,instance=None):
        try:
            from kivy.uix.rst import RstDocument
            #print "### the whole log2: ", self.log2
            self.bv.clear_widgets()
            rst_text="""QuantifyMyself-Log
====================
"""
            i=0
            lastdate = datetime(2010,1,1,0,0)
            #print "lastdate:  ",lastdate
            sqltext = "SELECT * FROM log WHERE time1 between date('now', '-4 days') and date('now', '+1 days') ORDER BY time1;"
            c = connlog.cursor()
            c.execute(sqltext)
            result = c.fetchall()
            for entry in result:
                try:
                    date1 = datetime.strptime(str(entry['time1']),"%Y-%m-%d %H:%M")
                    #print date1, date1-lastdate, (date1-lastdate).days
                    if (abs((date1-lastdate).days) >= 1 ):
                        lastdate = datetime(date1.year,date1.month,date1.day)
                        rst_text += "\n \n" + date1.strftime("%A,    %Y-%m-%d") + "\n-------------------------\n \n"
                    rst_text += self.entry2rst(entry=entry,listindex=i)
                    i += 1
                except Exception, e:
                    Logger.error(rst_text)
                    Logger.error("couldn't create entry number " + str(i) + str(entry) + str(e))
            #Logger.info(" ##.,:   " + rst_text)
            rst_doc = RstDocument(text = rst_text)
            self.bv.add_widget(rst_doc)
            rst_doc.scroll_y=0
        except Exception, e:
            Logger.error("couldnt show the reStructuredText-Log!  " + str(e))

    def paint_log_static(self,instance=None):
        #print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        relatlayout = AllInOneGraph(conlog = connlog,n_days=7)
        self.bv.add_widget(relatlayout )
        relatlayout.paintAll()

    def paint_log(self,instance=None):
        #print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        self.n_days = 4
        size = self.height,self.width
        relatlayout = ScrollableAllInOneGraph(conlog = connlog,size_hint=(None,None),size=self.size,size_inside=size, n_days=self.n_days )#(500,500))
        relatlayout.pos=self.bv.pos
        relatlayout.size=self.bv.size
        self.bv.add_widget(relatlayout)
        self.bv.do_layout()
        #relatlayout.paintAll()

    def paint_log_scroll(self,instance=None):
        #print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        self.n_days += 14
        relatlayout = ScrollableAllInOneGraph(conlog = connlog,size_hint=(None,None),size=self.size, n_days=self.n_days )#(500,500))
        relatlayout.pos=self.bv.pos
        relatlayout.size=self.bv.size
        self.bv.add_widget(relatlayout )
        self.bv.do_layout()
        #relatlayout.paintAll()

    def start_service(self):
        self.app.start_service()

    def export_all(self):
        self.app.export_all()

    def import_all(self):
        self.app.import_all()


    def show_home_view(self):
        self.bv.show_first_level()

class QuantifyApp(App):
    button_dict = []
    log =[]
    filename_buttondict = 'buttons.json'
    filename_logdict = 'log.json'
    filename_log2dict = 'log2.json'
    filename_log2csv = 'log2.csv'
    filename_db = 'quantlog.db'
    connlog = None

    def build(self):
        self.load_files()
        self.mainBL = MainView(button_dict=self.button_dict,app=self,connlog=connlog)
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        #self.start_service()
        return self.mainBL

    def start_service(self):
        if platform == 'android':
            from android import AndroidService
            service = AndroidService('QuantifyService', 'collecting data')
            service.start('service started')
            Logger.info("Service started at: " + str(datetime.now()))
            self.service = service

    def load_files(self):
        try:
            self.button_dict = self.loadJson(self.filename_buttondict)
        except Exception,e:
            Logger.error('failed to load button-db, e: ' + str(e))
            self.button_dict =[{"button_id": 1,"calendars": [ { "name": "start" },  { "name": "stop" }], "lasttime": "2014-09-04 16:09",                "note": True,                "sliders": [                    {                        "slider_def": "5.0",                        "slider_max": "10.0",                        "slider_min": "0.0",                        "slider_name": "productivity"                    }                ],                "status": "stopped",                "text": "Work start stop",                "type": "startstop"}]
        try:
            global connlog
            connlog = sqlite3.connect(self.filename_db)
            connlog.execute('''CREATE TABLE IF NOT EXISTS log
                       (ID INT PRIMARY KEY,
                       button_id    INT,
                       entryname    TEXT, type         TEXT,
                       note         TEXT, categories TEXT, timename1 TEXT,
                       time1 VARCHAR(20), timename2 TEXT, time2 VARCHAR(20),
                       timename3 TEXT, time3 VARCHAR(20), timename4 TEXT,  time4 VARCHAR(20), valuename1 TEXT,
                       value1 NUMERIC, valuename2 VARCHAR(21),value2 NUMERIC,valuename3 VARCHAR(21), value3 NUMERIC,
                       valuename4 VARCHAR(21), value4 NUMERIC
                       );''')
            print "squlito", connlog, self.filename_db
            connlog.row_factory = sqlite3.Row
        except Exception,e:
            Logger.error('failed to load sqlite database, e: ' + str(e) + "creating datatable...")
            #self.log2 = [[1,        "4zeiten",        "log",        "",        "test|",        "tim1",        "2014-09-06 14:16",        "start1",        "2014-09-04 14:16",        "start2",        "2014-09-04 14:16",        "stop1",        "2014-09-04 14:16",        "slo1",        1.5,        "slo2",        2.0,        "vi1",        1.4,        "ve2",        2.0    ]]

    def on_pause(self):
        self.save()
        return True



    def save(self):
        Logger.info("save files...")
        self.writeJson(self.filename_buttondict, self.button_dict)
        connlog.commit()
        #self.log2csv(self.filename_log2csv)

    def on_stop(self):
        self.on_pause()
        connlog.close()

    def loadJson(self,filename):
        Logger.info("load Json. Filename: " + filename)
        with open(filename, 'r') as input:
            data = load(input) #json.load
        print 'Read json from: ' + filename
        return data

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
           # do what you want, return True for stopping the propagation
           self.mainBL.bv.show_first_level()
           return True

    def export_all(self):
        try:
            self.save()
            # get export-directory:
            export_dir = "/storage/sdcard1/quantifyMyself/"
            if platform =="android":
                export_dir = "/storage/sdcard1/quantifyMyself/"
            elif platform == "win":
                export_dir = "C:/quantifyMyself/"
            Logger.info("export... platform: " + str(platform) + "; dir: " + str(export_dir))

            from os.path import exists
            if not exists(export_dir):
                from os import makedirs
                makedirs(export_dir)

            random_number = str(randint(0,999))
            exportpathfile_button = export_dir + random_number + self.filename_buttondict
            exportpathfile_quantlog = export_dir + random_number + self.filename_db
            Logger.info("export-filenames: " + exportpathfile_button + "; " + exportpathfile_quantlog)

            from shutil import copyfile
            copyfile(self.filename_db,exportpathfile_quantlog)
            copyfile(self.filename_buttondict,exportpathfile_button)
            Logger.info("exported to: " + exportpathfile_button + "; " + exportpathfile_quantlog)

        except Exception, e:
            Logger.error("export failed! "+ export_dir + ";   " + str(e))

    def import_all(self):
        connlog.close()
        try:
            export_dir = "/storage/sdcard1/quantifyMyself/"
            if platform =="android":
                export_dir = "/storage/sdcard1/quantifyMyself/"
            elif platform == "win":
                export_dir = "C:/quantifyMyself/"
            Logger.info("import... platform: " + str(platform) + "; dir: " + str(export_dir))
            from os.path import exists
            if not exists(export_dir):
                Logger.error("import failed! No import-directory! "+ export_dir)
            else:
                from shutil import copyfile
                from glob import iglob
                from os.path import getctime
                latest_quantlog_filename = max(iglob(export_dir + '*' + self.filename_db), key=getctime)
                latest_buttonlog_filename = max(iglob(export_dir + '*' + self.filename_buttondict), key=getctime)
                Logger.info("import from: " + latest_quantlog_filename + " ; " + latest_buttonlog_filename )
                Logger.info("import   to: " + self.filename_db + " ; " + self.filename_buttondict )
                copyfile(latest_quantlog_filename, self.filename_db)
                copyfile(latest_buttonlog_filename,self.filename_buttondict)

                #self.mainBL.bv.button_dict = self.mainBL.bv.button_dict = self.button_dict = self.loadJson(self.filename_buttondict)
                self.load_files()
                self.mainBL.bv.show_first_level()
                Logger.info("import successfull: " + latest_buttonlog_filename + "; imported quantlog: " + latest_quantlog_filename)
                Logger.info("db: " + str(connlog))
        except Exception, e:
            Logger.error("import failed! "+ export_dir + ";   " + str(e))
        finally:
            pass

    def log2csv(self,filename="log2.csv"):
        try:
            f = open(filename, "w")
            f.writelines("button_id; entryname;type;note;categories;timename1;time1;timename2;time2;timename3;time3;timename4;time4;valuename1;value1;valuename2;value2;valuename3;value3;valuename4;value4")
            for log_entry in self.log2:
                csv_string = ""

                for item in log_entry:
                    if item=="no_timename" or item=="no_time" or item=="no_valname" or item=="no_value":
                        item =""
                    if type(item) is unicode:
                        item = item.encode('utf-8')
                    csv_string += str(item) + ";"
                csv_string = '/n'.join(csv_string.splitlines())
                #csv_string.replace("\n", "/n")
                f.write("\n" + csv_string)

            print "end csv formatting...  ", filename

            f.close()
            print "end csv formatting2...  ", filename
            Logger.info("exported to csv: " + filename)
            print "end csv formatting3..  ", filename
        except Exception, e:
            Logger.error("Writing CSV-file didn't work... " + str(e))
            print "end csv formatting.4..  ", filename
        print "end csv formatting...6  ", filename

    def writeJson(self,filename, data):
        with open(filename, 'w') as output:
            dump(data, output, sort_keys=True, separators=(',',':')) #json.dump
        print 'Wrote json to: ' + filename

if __name__ == '__main__':
    QuantifyApp().run()
