"""
File:messenger.py
Main class for the messenger program
Contains definitions of the listener and connector classes that are both needed
to establish a messenger connection.
"""

from socket import socket,AF_INET,SOCK_STREAM
from queue import Queue
from threading import Thread
from tkinter import *
from time import sleep
from messengerinterface import Interface

class Messenger(socket):
    def __init__(self):
        socket.__init__(self,AF_INET,SOCK_STREAM)
        self.asklistenerconnector()
        self.stopthread=False
        self.messages=Queue()
        self.instream=Thread(target=self.listen)
        self.instream.start()
        self.root=Tk()
        gui=Interface(self.root,self.messages,self.transmit,self.endapp)
        gui.pack()
        self.root.protocol('WM_DELETE_WINDOW',lambda: self.transmit('stop'))
        self.root.mainloop()

    def asklistenerconnector(self):
        root=Tk()
        main=Frame(root)
        main.pack()
        header=Label(main,text='Will this terminal be the listener or the connector?')
        header.pack(side=TOP)
        buttonbar=Frame(main)
        listener=Button(buttonbar,text='LISTENER',command=lambda:self.setuplistener(root))
        connector=Button(buttonbar,text='CONNECTOR',command=lambda:self.setupconnector(root))
        listener.pack(side=LEFT)
        connector.pack(side=RIGHT)
        buttonbar.pack(side=BOTTOM)
        root.mainloop()

    def setuplistener(self,window):
        window.destroy()
        self.bind(('',4096))
        socket.listen(self,5)
        (self.sock,self.address)=self.accept()

    def setupconnector(self,window):
        window.destroy()
        try:
            self.connect(('192.168.1.103',4096))
        except:
            import sys
            print (sys.exc_info())
            sys.exit(0)
        self.sock=self

    def listen(self):
        while not (self.stopthread):
            fullmessage=''
            while True:
                readin=self.sock.recv(1024)
                readin=readin.decode()
                fullmessage+=readin
                if readin[-1:]=='|':break
            self.messages.put(fullmessage[:-1])
            sleep(0.5)

    def transmit(self,message):
        sentlength=0
        lastmessage=False
        if message=='stop':lastmessage=True
        message+='|'
        message=message.encode()
        while True:
            sent=self.sock.send(message)
            sentlength+=sent
            if sentlength==len(message):break
        if lastmessage:
            self.endapp()
            
    def endapp(self):
        self.stopthread=True        
        self.sock.close()
        self.root.destroy()
        sys.exit(0)

if __name__=='__main__':
    Messenger()
