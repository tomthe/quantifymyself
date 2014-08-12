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


class EnterView(BoxLayout):
    val1 = NumericProperty()
    val1text = StringProperty("no String")
    val2 = NumericProperty()
    val2text = StringProperty("no string")

    def build(self,dict):
        print "dicht:",dict
        if 'val1' in dict:
            self.val1 = int(dict['val1'])
            print self.val1
        #ev.val2text = "halbwert"

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
        self.parent_button_view.show_first_level()


class ButtonView(BoxLayout):
    button_dict =[]#[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
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
            ev = EnterView(dict=instance.dict)
            self.add_widget(ev)

class QuantifyApp(App):
    button_dict =[{'type':'submenu','text':'sleep','children':[{'type':'log','text':'sleep start'},{'type':'log','val1':'71','text':'sleep stop'}]},{'type':'log','text':'health','children':[{'type':'log','text':'sleep start'},{'type':'log','text':'sleep stop'}]} ]
    log = [{'datestart':'2014-05-22-13:24:43','text':'sleep_start'}]

    def build(self):
        bv = ButtonView(button_dict=self.button_dict,log=self.log)
        bv.button_dict = self.button_dict
        print "build app...", self.button_dict
        bv.show_first_level()
        return bv

if __name__ == '__main__':
    QuantifyApp().run()