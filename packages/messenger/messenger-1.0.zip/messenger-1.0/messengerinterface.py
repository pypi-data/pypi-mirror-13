"""
File:messengerinterface.py
User interface for messenger program
"""

from tkinter import *

class Interface(Frame):
    def __init__(self,master,messagequeue,transmit,endapp):
        Frame.__init__(self,master)
        self.messagequeue=messagequeue
        self.transmit=transmit
        self.endapp=endapp
        self.setup()

    def setup(self):
        inbackground=Frame(self)
        inbackground.pack(side=TOP,expand=YES,fill=BOTH)
        inmessagesSCR=Scrollbar(inbackground)
        inmessagesSCR.pack(side=RIGHT,expand=YES,fill=Y)
        self.inmessages=Text(inbackground,wrap=WORD,takefocus=0)
        self.inmessages.config(yscrollcommand=inmessagesSCR.set)
        inmessagesSCR.config(command=self.inmessages.yview)
        self.checkqueue()
        self.inmessages.pack(expand=YES,fill=BOTH)
        outbackground=Frame(self)
        outbackground.pack(side=BOTTOM,expand=YES,fill=X)
        self.outmessages=Text(outbackground,wrap=WORD)
        self.outmessages.bind('<Return>',self.sendmessage)
        self.outmessages.pack(fill=X,expand=YES)
                
    def checkqueue(self):
        try:
            message=self.messagequeue.get(block=FALSE)
        except:
            pass
        else:
            if message:
                if message=='stop':
                    self.endapp()
                message='\nThem: '+message
                self.inmessages.insert(END,message)
                self.inmessages.see(END)
        self.inmessages.after(500,self.checkqueue)

    def sendmessage(self,event):
        message=self.outmessages.get(0.0,END)
        if message[0]=='\n':
            message=message[1:]
        message=message[:-1]
        self.outmessages.delete(0.0,END)
        self.outmessages.delete(0.0,0.2)
        self.transmit(message)
        message='\nYou:'+message
        self.inmessages.insert(END,message)
        self.inmessages.see(END)
