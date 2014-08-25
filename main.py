import kivy
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.actionbar import ActionBar,ActionButton,ActionView
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.app import App
from time import strftime
from datetime import datetime

from json import load, dump

kivy.require('1.0.7')


class QuantButton(Widget):
    '''Button with some special properties: different colors for different type-variables; long-press-event after 1.2 seconds pressing'''
    color = ListProperty([0.4,0.5,0.5,1])
    text = StringProperty(",")
    timeStartPress = None

    def __init__(self, **kwargs):
        print "init quantbutton",kwargs
        self.register_event_type('on_long_press')
        self.register_event_type('on_press')
        self.dict = kwargs['dict']
        print 'children' in self.dict, len(self.dict), self.dict
        if 'type' in self.dict:
            print "type ist drin",
            if self.dict['type']=="log":
                self.color =[0.5,0.4,0.4,1]
        super(QuantButton, self).__init__(**kwargs)

    def on_touch_down(self,touch):
        print "quantmove ",touch
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
        print "on_long_press", instance


    def on_press(self,instance):
        print "on_press",instance


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
        print "customSlider - on_range:  ",instance,value,self.range, self.min, self.sl.range, self.sl.min

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


class EnterView(BoxLayout):
    #dict={}
    categories = []
    parent_button_view =None
    val1 = NumericProperty()
    val1text = StringProperty("no String")
    val2 = NumericProperty()
    val2text = StringProperty("no string")
    dsstart = ObjectProperty()
    dsend = ObjectProperty()

    def __init__(self, **kwargs):
        self.dict=kwargs['dict']
        super(EnterView, self).__init__(**kwargs)
        self.build()

    def build(self):
        self.clear_widgets()
        print "build EnterView --- dict:    ", self.dict

        label_text= Label()
        if 'text' in self.dict:
            label_text.text = self.dict['text']
        self.add_widget(label_text)

        #----------
        #datetime...
        self.dsstart = DateSlider()
        self.add_widget(self.dsstart)

        self.dsend = DateSlider()
        self.add_widget(self.dsend)

#----------
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

    def cancelf(self,instance=None):
        print "cancel...", self.dsstart.get_datetime(),self.dsend.get_datetime()
        self.parent_button_view.clear_widgets()
        self.parent_button_view.show_first_level()

    def log_entry(self,instance=None):
        new_log_entry = {}
        new_log_entry['starttime'] = str(self.dsstart.get_datetime())
        new_log_entry['endtime'] = str(self.dsend.get_datetime())

        new_log_entry['value1'] = str(self.val1)
        new_log_entry['value2'] = str(self.val2)

        if 'text' in self.dict:
            new_log_entry['text'] = str(self.dict['text'])
        if 'type' in self.dict:
            new_log_entry['type'] = str(self.dict['type'])
        i=1
        for category in self.categories:
            new_log_entry['cat' + str(int(i))] = category
            i+=1
        self.parent_button_view.log.append(new_log_entry)
        print "log...  ", new_log_entry
        self.cancelf()

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
    categories =[]
    app = None
    log=[]

    def build(self):
        print "blabla"
        self.show_first_level()

    def show_first_level(self):
        print "show_first_level", self.button_dict,self.log
        self.categories = []
        for button in self.button_dict:
            print "show first level: ", button

            if 'children' in button:
                bt = QuantButton(text=button['text'],dict=button['children'],type='submenu')
            else:
                bt = QuantButton(text= button['text'],dict=button,type='log')
            bt.bind(on_press=self.buttonpress)
            self.add_widget(bt)
        self.add_add_button(dict=self.button_dict)

    def show_button_dict(self,bdict,text):
        self.clear_widgets()
        self.categories.append(text)
        categoryname_Label = Label()
        categoryname_Label.text = text
        self.add_widget(categoryname_Label)
        for button in bdict:
            print "buttondict - one button: ", button
            if 'children' in button:
                bt = QuantButton(text=button['text'],dict=button['children'],type='submenu')
            else:
                bt = QuantButton(text= button['text'],dict=button,type='log')
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
        print "buttonpress..., ", instance, ";.. value: ", value, instance.dict, instance.text

        if type(instance.dict)==list:
            #-->submenu
            self.show_button_dict(instance.dict,instance.text)
        elif type(instance.dict)==dict:
            #-->entry
            print "buttonview-buttonpress-instance.dict : ", instance.dict
            self.clear_widgets()
            ev = EnterView(dict=instance.dict)
            #ev.dict=instance.dict
            ev.categories =  self.categories
            ev.parent_button_view=self
            print "ev..............", ev
            self.add_widget(ev)

class ListEntry(BoxLayout):

    def __init__(self, **kwargs):
        self.entry=kwargs['entry']
        super(ListEntry, self).__init__(**kwargs)
        print self.entry
        for item in self.entry:
            print item, self.entry[item]
            lab = Label()
            lab.text = self.entry[item]
            self.add_widget(lab)
            self.height = lab.texture_size[1]

class QuantifyApp(App):
    button_dict = []
    log =[]
    filename_buttondict = 'buttons.json'
    filename_logdict = 'log.json'

    def build(self):
        try:
            self.button_dict = self.loadJson(self.filename_buttondict)
        except Exception,e:
            self.button_dict =[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','val1':'71','text':'sleep stop'}]},{'type':'log','text':'health','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
        try:
            self.log = self.loadJson(self.filename_logdict)
        except Exception,e:
            log = [{'datestart':'2014-05-22-13:24:43','text':'sleep_start'}]

        self.mainBL = BoxLayout()
        self.mainBL.orientation = 'vertical'
        actionbar = ActionBar()
        actionview = ActionView()
        actionbar.add_widget(actionview)
        but1 =Button()# ActionButton()
        but1.text = "test"
        but1.height = "30dp"
        but1.bind(on_press=self.list)
        #actionview.add_widget(but1)
        #self.mainBL.add_widget(actionbar)
        self.mainBL.add_widget(but1)
        bv = ButtonView(button_dict=self.button_dict,log=self.log)
        bv.button_dict = self.button_dict
        bv.log = self.log
        bv.app=self
        print "build app...", self.button_dict
        bv.show_first_level()

        self.mainBL.add_widget(bv)
        return self.mainBL

    def list(self,instance):
        self.mainBL.clear_widgets()
        scrollview= ScrollView()
        boxlayout = BoxLayout()
        boxlayout.height =220
        boxlayout.orientation = 'vertical'
        boxlayout.size_hint_y =None
        for entry in self.log:
            entryp = ListEntry(entry=entry)
            boxlayout.add_widget(entryp)
            boxlayout.height += entryp.height
            print "hhh: ", entryp.height, boxlayout.height
        scrollview.add_widget(boxlayout)
        self.mainBL.add_widget(scrollview )
        return True# scrollview

    def on_pause(self):
        self.writeJson(self.filename_buttondict, self.button_dict)
        self.writeJson(self.filename_logdict, self.log)
        return True

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
