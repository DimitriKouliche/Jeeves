# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""This is the main way to communicate to Jeeves: using a tkinter UI"""

from tkinter import *
from bot import speech
from bot import brain

window = Tk()

messages = Text(window, wrap=WORD)
window.title('Chat with Jeeves!')
messages.pack()
messages.insert(INSERT, '%s\n' % "You are now talking with Jeeves. Say hi!")
messages.tag_configure("red", foreground="red")
messages.tag_configure("blue", foreground="blue")
messages.config(state=DISABLED)
motor = brain.Motor()

input_user = StringVar()
input_field = Entry(window, text=input_user)
input_field.focus_set()


def main():
    """Called when we launch the project"""
    draw_gui()


def draw_gui():
    """Sets up the UI"""
    input_field.pack(side=BOTTOM, fill=X)
    frame = Frame(window)
    input_field.bind("<Return>", enter_pressed)
    frame.pack()
    window.mainloop()


def insert_message(message, color):
    """Inserts a message in the main window
    Args:
        message (str): A message to insert in our window
        color (str): The color we want the message to display in."""
    messages.config(state=NORMAL)
    messages.insert(END, message, color)
    messages.config(state=DISABLED)
    input_user.set('')
    Tk.update(window)
    messages.see(END)


def enter_pressed(event):
    """Fires whenever enter is pressed, retrieves user inputs and responds to it
    Args:
        event (str): The event that was sent"""
    input_get = input_field.get()
    insert_message('%s\n' % input_get, "blue")
    insert_message('%s\n\n' % speech.respond(motor, input_get.lower()), "red")
    return "break"

if __name__ == '__main__':
    main()
