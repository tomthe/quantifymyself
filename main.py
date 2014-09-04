import kivy
from kivy.graphics import Rectangle,Line
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
from kivy.metrics import dp,sp
from kivy.app import App
from time import strftime, strptime
from random import randint
from datetime import datetime

from json import load, dump
from kivy.uix.textinput import TextInput
from pygame.gfxdraw import box

kivy.require('1.0.7')

__version__ = "0.2.7"

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
            # accept the touch.
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            timediffseconds =(datetime.now() - self.timeLastMove).total_seconds()
            if timediffseconds <0.01:
                timediffseconds =0.01
            elif timediffseconds >1.9:
                timediffseconds=1.9

            self.real_value = (self.real_value + 0.00002 * (self.max - self.min) * (touch.pos[1]-self.last_y) /timediffseconds)
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
            print "build EnterView --- dict:    ", self.dict

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
                print '----------slid',slid
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

        self.parent_button_view.log.append(new_log_entry)
        self.parent_button_view.log2.append(self.log_entry_2_log2(new_log_entry))
        print "log...  ", new_log_entry
        self.cancelf()

    def log_entry_2_log2(self,log1):
        #converts a dict-log-entry into a list-based log-entry
        log2=[]
        #button_id, entryname,type,note,timename1,time1,timename2,time2,timename3,time3,timename4,time4,valuename1,value1,valuename2,value2,valuename3,value3,valuename4,value4
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
            categories = categories[:-1]
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
                        log2.append("no_timename")
                        log2.append("no_time")
            if i<4:
                for j in xrange(i,4,1):
                    log2.append("no_timename")
                    log2.append("no_time")

        else:
            log2.append('no_timename1')
            log2.append('no_time1')
            log2.append('no_timename2')
            log2.append('no_time2')
            log2.append('no_timename3')
            log2.append('no_time3')
            log2.append('no_timename4')
            log2.append('no_time4')


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
                        log2.append("no_valname")
                        log2.append("no_value")
            if i<4:
                for j in xrange(i,4,1):
                    log2.append("no_valname")
                    log2.append("no_value")
        else:
            log2.append('no_valname1')
            log2.append('no_val1')
            log2.append('no_valname2')
            log2.append('no_val2')
            log2.append('no_valname3')
            log2.append('no_val3')
            log2.append('no_valname4')
            log2.append('no_val4')
        print log2
        return log2

class NewEnterView2(BoxLayout):
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

    def add_name_field(self):
        bl=BoxLayout()
        lab = Label(text='Button-Text')
        bl.add_widget(lab)
        self.ti_button_text = TextInput(text='')
        bl.add_widget(self.ti_button_text)
        self.add_widget(bl)

    def add_ok_cancel(self):
        bl= BoxLayout(orientation='horizontal')
        bt_ok = Button(text='OK2')
        bl.add_widget(bt_ok)
        bt_ok.bind(on_press=self.okay)
        bt_cancel = Button(text='Cancel2')
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
        textinput_def = TextInput(text='1')
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
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_name_field()
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
            print "on_cb2_startstop...",instance
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_type_choice(choice='startstop')
            self.add_name_field()

            self.add_text()
            #add calender and '+'-button
            self.add_cal(name='start')
            self.add_cal(name='stop')
            #add value-widget and +button
            self.add_val()
            self.add_ok_cancel()

    def on_cb3_4times(self,instance=None,value=None):
        if value:
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_type_choice(choice='4times')
            self.add_name_field()

            print "on_cb3_4times...",instance
            self.add_cal(name='start1')
            self.add_cal(name='start2')
            self.add_cal(name='stop1')
            self.add_cal(name='stop2')
            self.add_val()
            self.add_ok_cancel()

    def on_cb4_newSubmenu(self,instance=None,value=None):
        if value:
            print "on_cb4_newSubmenu...",instance
            self.clear_widgets()
            self.slider_list=[]
            self.calendar_list=[]
            self.add_name_field()
            self.add_type_choice(choice='newSubmenu')
            #
            self.add_ok_cancel()

    def okay(self,instance=None):
        newdict = {}
        print ".................................................................................."
        ID = randint(100,9999) #str(randint(100,9999))
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

    def cancel(self,instance=None):
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()

class ButtonView(StackLayout):
    button_dict =[]#[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
    categories =[]
    app = None
    log=[]
    log2=[]

    def __init__(self, **kwargs):
        super(ButtonView, self).__init__(**kwargs)
        self.button_dict=kwargs['button_dict']
        self.log = kwargs['log']
        self.log2 = kwargs['log2']
        self.app = kwargs['app']
        self.show_first_level()

    def show_first_level(self):
        print "show_first_level 1 ", self.button_dict,self.log
        self.categories = []
        self.clear_widgets()
        for button in self.button_dict:
            #print "show first level: ", button

            if 'children' in button:
                bt = QuantButton(text=button['text'],dict=button['children'],type='submenu')
            else:
                bt = QuantButton(text= button['text'],dict=button,type='log')
            bt.bind(on_press=self.buttonpress)
            bt.size_hint = (None,None)
            bt.size = [self.width/2-5, self.height /6-5]
            self.add_widget(bt)
        self.add_add_button(dict=self.button_dict)

    def show_button_dict(self,bdict,text):
        print " ButtonView...show_button_dict",text
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
        print "buttonpress..., ", instance, ";.. value: ", value, instance.dict, instance.text

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

    def on_size(self,instance,value):
        self.show_first_level()
        pass

class ListEntry(BoxLayout):

    def __init__(self, **kwargs):
        self.entry=kwargs['entry']
        super(ListEntry, self).__init__(**kwargs)
        #print self.entry

        for item,value in self.entry.viewitems():
            try:
                if type(value) is list:
                    for listitem in value:
                        bl = BoxLayout(orientation='vertical')
                        for iteminside,valueinside in listitem.viewitems():
                            lab = Label()
                            lab.text = str(valueinside)
                            bl.add_widget(lab)
                        self.add_widget(bl)
                else:
                    lab = Label()
                    lab.text = value
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
            label_index = Label(text=str(self.listindex),size_hint=(0.04,0.5), pos_hint={'x':.0, 'y':.5})
            self.add_widget(label_index)

            bl_date = BoxLayout(orientation='vertical',pos_hint={'x':.01, 'y':.0}, size_hint=(None,1),width=sp(100))
            date1 = datetime.strptime(str(self.entry[6]),"%Y-%m-%d %H:%M")
            date2 = datetime.strptime(str(self.entry[8]),"%Y-%m-%d %H:%M")
            label_date1 = Label(text=date1.strftime("%H:%M"))
            bl_date.add_widget(label_date1)
            if (date2-date1).seconds > 1:
                label_date2 = Label(text=str(self.entry[8])[10:])
                bl_date.add_widget(label_date2)

            self.add_widget(bl_date)
            label_name = Label(text=str(self.entry[1]),pos_hint={'x':.15, 'top':1}, size_hint=(None,0.4), size=(100,20))
            self.add_widget(label_name)
            label_categories = Label(text=str(self.entry[4]),pos_hint={'x':.15, 'top':0.75}, size_hint=(None,0.4), size=(100,20))
            self.add_widget(label_categories)

            bl_value = BoxLayout(orientation='vertical',pos_hint={'x':.55}, size_hint=(0.15,1))
            label_value1 = Label(text=str(self.entry[13]))
            label_value2 = Label(text=str(self.entry[15]))
            bl_value.add_widget(label_value1)
            bl_value.add_widget(label_value2)
            self.add_widget(bl_value)

            bl_value = BoxLayout(orientation='vertical',pos_hint={'x':.75}, size_hint=(0.15,1))
            try:
                label_value1 = Label(text=str(round(float(str(self.entry[14])),2)))
                bl_value.add_widget(label_value1)
            except:
                pass
            try:
                label_value2 = Label(text=str(round(float(str(self.entry[16])),2)))
                bl_value.add_widget(label_value2)
            except:
                pass
            self.add_widget(bl_value)

            if len(self.entry[3])>1:
                self.height +=300
                label_note = Label(text=self.entry[3],pos_hint={'x':0.1, 'y':0.0}, size_hint=(0.6,0.3),text_size=(300,None),color=(0.4,1,1,1))
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


class MainView(BoxLayout):
    bv = None
    app = None
    log =None
    log2=None
    button_dic =None

    def __init__(self, **kwargs):
        #self.entry=kwargs['entry']
        super(MainView, self).__init__(**kwargs)

        self.button_dict=kwargs['button_dict']
        self.log = kwargs['log']
        self.log2 = kwargs['log2']
        self.app = kwargs['app']

        self.bv = ButtonView(button_dict=self.button_dict,log=self.log,log2=self.log2,app=self.app)

        self.add_widget(self.bv)


    def list_log(self,instance=None):
        print "### the whole log: ", self.log
        self.bv.clear_widgets()
        scrollview= ScrollView()
        gridlayout = GridLayout(cols=1,spacing=5,size_hint_y =None)

        gridlayout.size_hint_y =None
        for entry in self.log:
            print "###entry  ", entry
            if type(entry) is list:
                pass
            else:
                entryp = ListEntry(entry=entry)
                entryp.height =100
                gridlayout.add_widget(entryp)
                gridlayout.height += entryp.height
                print "hhh: ", entryp.height, gridlayout.height
        scrollview.add_widget(gridlayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0

    def list_log2(self,instance=None):
        print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        scrollview= ScrollView()
        gridlayout = GridLayout(cols=1,spacing=5,size_hint_y =None)
        i=0
        lastdate = datetime(2010,1,1,0,0)
        print "lastdate:  ",lastdate
        for entry in self.log2:

            date1 = datetime.strptime(str(entry[6]),"%Y-%m-%d %H:%M")
            print date1, date1-lastdate, (date1-lastdate).days
            if (abs((date1-lastdate).days) > 1 ):
                lastdate = date1
                date_label = Label(text=date1.strftime("%A,    %Y-%m-%d"),color=(0.7,1,0.8,1),font_size=sp(16))
                gridlayout.add_widget(date_label)
                date_label.height = 33
                gridlayout.height += date_label.height
            entryp = ListEntry2(entry=entry,listindex=i)
            gridlayout.add_widget(entryp)
            gridlayout.height += entryp.height
            print "entryp-height: ", entryp.height, gridlayout.height
            i += 1
        scrollview.add_widget(gridlayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0

    def paint_log(self,instance=None):
        print "### the whole log2: ", self.log2
        self.bv.clear_widgets()
        scrollview= ScrollView()
        relatlayout = RelativeLayout()
        i=0
        lastdate = datetime(2010,1,1,0,0)
        print "lastdate:  ",lastdate
        for entry in self.log2:

            date1 = datetime.strptime(str(entry[6]),"%Y-%m-%d %H:%M")
            print date1, date1-lastdate, (date1-lastdate).days
            if (abs((date1-lastdate).days) > 1 ):
                lastdate = date1
                date_label = Label(text=date1.strftime("%A,    %Y-%m-%d"),color=(0.7,1,0.8,1),font_size=sp(16))
                relatlayout.add_widget(date_label)
                date_label.height = 33
                relatlayout.height += date_label.height
            entryp = ListEntry2(entry=entry,listindex=i)
            relatlayout.add_widget(entryp)
            relatlayout.height += entryp.height
            print "entryp-height: ", entryp.height, relatlayout.height
            i += 1
        scrollview.add_widget(relatlayout)
        self.bv.add_widget(scrollview )
        scrollview.scroll_y = 0


    def show_home_view(self):
        self.bv.show_first_level()

class QuantifyApp(App):
    button_dict = []
    log =[]
    filename_buttondict = 'buttons.json'
    filename_logdict = 'log.json'
    filename_log2dict = 'log2.json'
    def build(self):
        try:
            self.button_dict = self.loadJson(self.filename_buttondict)
        except Exception,e:
            Logger.error('failed to load button-db, e: ' + str(e))
            self.button_dict =[{"button_id": 1,"calendars": [ { "name": "start" },  { "name": "stop" }], "lasttime": "2014-09-04 16:09",                "note": True,                "sliders": [                    {                        "slider_def": "5.0",                        "slider_max": "10.0",                        "slider_min": "0.0",                        "slider_name": "productivity"                    }                ],                "status": "stopped",                "text": "Work start stop",                "type": "startstop"}]
        try:
            self.log = self.loadJson(self.filename_logdict)
        except Exception,e:
            Logger.error('failed to load log-db, e: ' + str(e))
            self.log = [{"datetimes": [{ "datetime": "2014-08-17 19:33", "timename": "time1" },  {"datetime": "2014-08-22 19:33",                "timename": "time1"            }        ],        "entryname": "bullo",        "note": "sdfw",        "type": "log",        "values": [            {                "valname": "produktivit\u00e4t",                "value": 5.666666666666665            },            {                "valname": "value",                "value": 5.683593749999999            },            {                "valname": "spass",                "value": 3.0598958333333326            }        ]    }]
        try:
            self.log2 = self.loadJson(self.filename_log2dict)
        except Exception,e:
            Logger.error('failed to load log-db, e: ' + str(e))
            self.log2 = [[1,        "4zeiten",        "log",        "",        "test|",        "tim1",        "2014-09-06 14:16",        "start1",        "2014-09-04 14:16",        "start2",        "2014-09-04 14:16",        "stop1",        "2014-09-04 14:16",        "slo1",        1.5,        "slo2",        2.0,        "vi1",        1.4,        "ve2",        2.0    ]]
        self.mainBL = MainView(button_dict=self.button_dict,log=self.log,log2=self.log2,app=self)
        return self.mainBL

    def on_pause(self):
        self.writeJson(self.filename_buttondict, self.button_dict)
        self.writeJson(self.filename_logdict, self.log)
        self.writeJson(self.filename_log2dict, self.log2)
        return True

    def save(self):
        self.on_pause()

    def on_stop(self):
        self.on_pause()

    def loadJson(self,filename):
        with open(filename, 'r') as input:
            data = load(input) #json.load
        print 'Read json from: ' + filename
        return data

    def writeJson(self,filename, data):
        with open(filename, 'w') as output:
            dump(data, output, sort_keys=True, indent=4, separators=(',', ': ')) #json.dump
        print 'Wrote json to: ' + filename


if __name__ == '__main__':
    QuantifyApp().run()
