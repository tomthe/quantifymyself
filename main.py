import kivy
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.app import App
from json import loads
from time import strftime
from datetime import datetime

kivy.require('1.0.7')

class CustomSlider(BoxLayout):
    ltext = StringProperty()
    range = ListProperty()
    min,max = NumericProperty(0),NumericProperty(99)
    value = NumericProperty(1)
    sl = ObjectProperty()


    def on_value(self,instance,value):
        self.sl.value = value

    def change_value(self,val):
        self.value = val

    def on_range(self,instance,value):
        self.min = value[0]
        self.max = value[1]
        print self.range, self.min, self.sl.range, self.sl.min

class DateSlider(BoxLayout):
    syear = ObjectProperty()
    smonth = ObjectProperty()
    sday = ObjectProperty()
    shour = ObjectProperty()
    sminute = ObjectProperty()

    def __init__(self, **kwargs):
        super(DateSlider, self).__init__(**kwargs)
        now = datetime.now()
        print "build dateslider...now:", now
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
        self.shour.min = 1
        self.shour.max = 24

        self.sminute.step = 1
        self.sminute.value = now.minute
        self.sminute.min = 1
        self.sminute.max = 59

    def get_time_tuple(self):
        return [int(self.syear.value), int(self.smonth.value), int(self.sday.value), int(self.shour.value), int(self.sminute.value)]

    def get_datetime(self):
        return datetime(int(self.syear.value), int(self.smonth.value), int(self.sday.value), int(self.shour.value), int(self.sminute.value))

    def test(self):
        print self.syear,self.syear.value
        print self.get_datetime()

class EnterView(BoxLayout):
    dict={}
    parent_button_view =None
    val1 = NumericProperty()
    val1text = StringProperty("no String")
    val2 = NumericProperty()
    val2text = StringProperty("no string")


    def build(self):
        print "build EnterView --- dict:    ", self.dict

        self.clear_widgets()
        #----------
        #datetime...
        dsstart = DateSlider()
        self.add_widget(dsstart)
        #now.

#----------
        label_text= Label()
        if 'text' in self.dict:
            label_text.text = self.dict['text']
        self.add_widget(label_text)
        if 'val1range' in self.dict:
            cslider1 = CustomSlider()
            cslider1.range=self.dict['val1range']
            cslider1.ltext=self.dict['val1name']
            self.add_widget(cslider1)
        if 'val2range' in self.dict:
            cslider2 = CustomSlider()
            cslider2.range=self.dict['val2range']
            cslider2.ltext=self.dict['val2name']
            self.add_widget(cslider2)

        bt_ok = Button()
        bt_ok.text = "OK"
        bt_ok.bind(on_press=self.log_entry)
        self.add_widget(bt_ok)
        bt_cancel = Button()
        bt_cancel.text = "cancel"
        bt_cancel.bind(on_press=self.cancelf)
        self.add_widget(bt_cancel)

    def cancelf(self,instance):
        print "cancel..."
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()

    def log_entry(self,instance):
        new_log_entry = {}


        self.parent_button_view.log.append(new_log_entry)
        print "log..."

class NewEnterView(BoxLayout):
    dict =[] #Button_dict of the level where the button is shown
    parent_button_view = None

    ti_val1min = ObjectProperty()
    ti_val1max = ObjectProperty()
    ti_val1_text = ObjectProperty()
    ti_val2min = ObjectProperty()
    ti_val2max = ObjectProperty()
    ti_val2_text = ObjectProperty()
    ti_button_text = ObjectProperty()
    cb_type_log = ObjectProperty()
    cb_type_submenu = ObjectProperty()

    def create_new_button(self):
        newdict = {}
        newdict['text']=self.ti_button_text.text
        if self.cb_type_log.active:
            newdict['type']= 'log'
        elif self.cb_type_submenu.active:
            newdict['type']= 'submenu'

        if  newdict['type']=='log':
            newdict['val1name']=self.ti_val1_text.text
            newdict['val1range']=(float(self.ti_val1min.text),float(self.ti_val1max.text))
            newdict['val2name']=self.ti_val2_text.text
            newdict['val2range']=(float(self.ti_val2min.text),float(self.ti_val2max.text))
        elif newdict['type']=='submenu':
            newdict['children'] = []
        else:
            print "no availible type!"
        print self.parent_button_view
        print "pardict:          ", self.dict
        print "newdict:          ", newdict
        self.dict.append(newdict)
        print "pardict:          ", self.dict
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()

    def cancel(self):
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()


class ButtonView(BoxLayout):
    button_dict =[]#[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
    app = None
    log=[]

    def build(self):
        print "blabla"
        self.show_first_level()

    def show_first_level(self):
        print "show_first_level", self.button_dict,self.log
        for button in self.button_dict:
            print button
            bt = Button()
            bt.text= button['text']
            if 'children' in button:
                bt.dict=button['children']
            else:
                bt.dict = button
            bt.bind(on_press=self.buttonpress)
            self.add_widget(bt)
        self.add_add_button(dict=self.button_dict)

    def show_button_dict(self,bdict):
        self.clear_widgets()
        for button in bdict:
            print button
            bt = Button()
            bt.text = button['text']
            bt.dict = button
            bt.bind(on_press=self.buttonpress)
            self.add_widget(bt)
        self.add_add_button(dict=bdict)

    def add_add_button(self,dict):
        bt = Button(text="+")
        bt.dict = dict
        bt.parent_button_view = self
        bt.bind(on_press=self.add_button)
        self.add_widget(bt)


    def add_button(self,instance,value=None):
        self.clear_widgets()
        av = NewEnterView(parent_button_view=self,dict=instance.dict)
        av.parent_button_view = self
        av.dict = instance.dict
        self.add_widget(av)

    def buttonpress(self,instance,value =None):
        print "buttonpress..., ", instance, ";.. value: ", value, instance.dict

        if type(instance.dict)==list:
            #-->submenu
            self.show_button_dict(instance.dict)
        elif type(instance.dict)==dict:
            #-->entry
            self.clear_widgets()
            ev = EnterView()
            ev.dict=instance.dict
            ev.parent_button_view=self
            ev.build()
            print "ev..............", ev
            self.add_widget(ev)

class QuantifyApp(App):
    button_dict =[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','val1':'71','text':'sleep stop'}]},{'type':'log','text':'health','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
    log = [{'datestart':'2014-05-22-13:24:43','text':'sleep_start'}]

    def build(self):
        bv = ButtonView(button_dict=self.button_dict,log=self.log)
        bv.button_dict = self.button_dict
        bv.log = self.log
        bv.app=self
        print "build app...", self.button_dict
        bv.show_first_level()
        return bv

if __name__ == '__main__':
    QuantifyApp().run()