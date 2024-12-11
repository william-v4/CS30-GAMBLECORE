import enum
import time
from tkinter import *
from tkinter.font import Font
import customtkinter as gui
import random
import pygame
from PIL import Image
import os

# working directory (for importing assets)
workingdir = os.path.dirname(__file__)
print("working directory: " + workingdir)
# load fonts
gui.FontManager.load_font(os.path.join("Montserrat-SemiBold.ttf"))
gui.FontManager.load_font(os.path.join("Roboto-Regular.ttf"))
# set label styles
title = ("Montserrat", 20)
text = ("Roboto-Regular", 16)
# gambleman image
gambleman = Image.open(
    os.path.join( workingdir, "gambleman.png")
)
# submit button icon
submiticon = gui.CTkImage(Image.open( os.path.join( workingdir, "return.png") ), size=(20, 20))
# exit button icon
exiticon = gui.CTkImage(Image.open( os.path.join( workingdir, "exit.png") ), size=(20, 20))
# initialize UI window
window = gui.CTk()
# set window title and icon
window.title("GAMBLECORE")
window.wm_iconphoto(False, PhotoImage(file=os.path.join( workingdir, "slots.png")))


"""
create a label
Args:
    text (str): text to display
    style (tuple): text style
    row (int): row to place label
    column (int): column to place label
    action: function to call when label is clicked
"""
def label(text : str, style : tuple, row : int, column : int, columnspan=None):
    if columnspan:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10)
    else:
        gui.CTkLabel(window, text=text, font=style).grid(row=row, column=column)

# balance
balance = 1000
def balancelabel():
    label("$" + str(round(balance)), text, 0, 1)

# error checking for positive integer
spins = 0
slots = 0
guess= 0
vartype = enum.Enum('vartype', 'spins slots guess')
def posint(variable : vartype):
    # global variables
    global spins, slots, guess
    match variable:
        # for each type of variable, set all relevant UI elements, its corresponding global variable, and the confirm text (ternary for grammar)
        case vartype.spins:
            inputfield = spinfield
            inputlabel = spinfieldlabel
            inputbutton = spinbutton
        case vartype.slots:
            inputfield = slotfield
            inputlabel = slotfieldlabel
            inputbutton = slotbutton
        case vartype.guess:
            inputfield = guessfield
            inputlabel = guessfieldlabel
            inputbutton = guessbutton
    try:
        # try to convert input to int
        input = int(inputfield.get())
        # check if input is negative
        if input <0:
            # if yes, trigger except
            raise ValueError
        # if the above passes, input is valid. update variable and confirmation text accordingly
        match variable:
            case vartype.spins:
                spins = input
                confirmtext = f"{spins} spin{'s' if spins != 1 else ''}"
            case vartype.slots:
                slots = input
                confirmtext = f"{slots} number{'s' if slots != 1 else ''} on the slot machine"
            case vartype.guess:
                guess = input
                confirmtext = f"You bet on {guess}"
        # remove input field and button
        inputfield.grid_forget()
        inputbutton.grid_forget()
        # update spins label to show number of spins (ternary operator for grammar)
        inputlabel.configure(text=confirmtext)
        # if guess is not in range, trigger except
        if variable == vartype.guess and guess > slots:
            raise IndexError
    except ValueError:
        inputlabel.configure(text="Please enter a positive integer")
        # let other functions know that input was invalid
        return True
    # triggered if guess is not in range
    except IndexError:
        # let user know
        inputlabel.configure(text="That's not on the slot machine")
    # if all is well, return False
    return False

# error checking on bet amount
bet = 0
def betsubmit():
    global bet
    try:
        # try to convert input to int
        bet = float(betfield.get())
        # check if input is negative
        if bet <0:
            # if yes, let user know and trigger except
            betfieldlabel.configure(text="That's theft")
            raise ValueError
        # if the above passes, let the user know
        betfieldlabel.configure(text=f"You bet ${bet}")
        # remove input field and button
        betfield.grid_forget()
        betbutton.grid_forget()
        # and let other functions know
        return False
    # if error raised
    except ValueError:
        # let other functions know
        return True

# for clearing the window
def clear():
    # for every widget in the window
    for widget in window.winfo_children():
        # eject them
        widget.destroy()

# actual gambling function
def spin():
    global balance
    # resubmit variables
    for variable in vartype:
        # run all submit functions and make sure none of them return true (invalid)
        if posint(variable):
            # if any of them are invalid, stop the function and trap user on previous screen
            return
        if betsubmit(): 
            return
    # clear window
    clear()
    # play let's go gambling sound
    pygame.mixer.init()
    pygame.mixer.Sound(os.path.join( workingdir, "letsgogambling.ogg")).play()
    # replace gambleman with spinning slot machine
    image = gui.CTkLabel(window, text="", image=gui.CTkImage(Image.open( os.path.join( workingdir, "spin.gif") ), size=(300, 200)))
    image.grid(row=1, column=0, columnspan=2, pady=20)
    # update header
    header = label("Spinning...", title, 0, 0, 2)
    change = 0 # change in balance
    interest = 0 # if in debt
    wins = 0 # number of spins won
    losses = 0 # number of spins lost
    # update window
    window.update()
    # wait 3 sec
    time.sleep(2)
    # do the actual spinning: for each spin
    for round in range(spins):
        # if guess matches random number guessween 1 and number of slots, they win
        if guess == (num := random.randint(1, slots)):
            # play win sound
            pygame.mixer.Sound(os.path.join( workingdir, "icantstopwinning.ogg")).play()
            # add bet weighted by number of slots
            change += bet * slots
            # tally wins
            wins += 1
            # let user know (round//10 is for column placement. floor division by 10)
            gui.CTkLabel(window, text=f"spin {round + 1}: {num} you won ${bet*slots}", font=text).grid(row=2 + (round%10), column=round//10, padx=10)
        # if not, they lost
        else:
            # play lose sound
            pygame.mixer.Sound(os.path.join( workingdir, "awwdangit.ogg")).play()
            # subtract bet 
            change -= bet
            # tally losses
            losses += 1
            # let user know (round//10 is for column placement. floor division by 10)
            gui.CTkLabel(window, text=f"spin {round + 1}: {num} you lost ${bet}", font=text).grid(row=2 + (round%10), column=round//10, padx=10)
        # if in debt, add 10% interest
        if instantaneousbalance := (balance+change) < 0:
            interest = instantaneousbalance * 0.1
        # update window
        window.update()
        # wait 1.25 sec
        time.sleep(1.25)
    # when all spins done, update balance
    balance += change
    if balance < 0:
        balance += interest
    # show summary (most cursed one-liner to date)
    label(text=f"You {'lost ' + str( x := losses) if change < 0 else 'won ' + str( x := wins)} spin{'s' if x != 1 else ''}. " + f"You've {'won' if change > 0 else 'lost'} ${abs(change)}", style=text, row=2 + spins, column=0, columnspan=2)
    label(text=f"Your balance is now ${balance}", style=text, row=3 + spins, column=0, columnspan=2)
    # show options
    gui.CTkButton(window, text="KEEP GAMBLING", font=text, command=main).grid(row=4 + spins, column=0, columnspan=2, padx=20, pady=10)
    gui.CTkButton(window, text="", image=exiticon, command=exit).grid(row=5 + spins, column=0, columnspan=2, padx=20, pady=10)
    # if in debt, loan shark
    if balance < 0:
        label("you are now in debt. you will now pay 10% interest on every spin", text, 6 + spins, 0, 2)

"""
    main method
"""
def main():
    global window, image, spinbutton, spinfield, spinfieldlabel, slotfield, slotbutton, slotfieldlabel, guessfield, guessbutton, guessfieldlabel, betfield, betbutton, betfieldlabel, startbutton
    # dark mode
    gui.set_appearance_mode("dark")
    # clear window
    clear()
    # create header label
    label("Let's go gambling!", title, 0, 0, 2)
    # load and display gambleman (200x200)
    image = gui.CTkLabel(window, text="", image=gui.CTkImage(gambleman, size=(200, 200)))
    image.grid(row=1, column=0, columnspan=2, pady=20)
    # display balance
    balancelabel()
    # ask user how many times to spin
    spinfieldlabel = gui.CTkLabel(window, text="How many times to spin?", font=text)
    spinfieldlabel.grid(row=2, column=0, padx=20, pady=10)
    # create input field and place it
    spinfield = gui.CTkEntry(window, font=text)
    spinfield.grid(row=3, column=0, padx=20, pady=10)
    # bind enter (and numpad enter) key to submit
    spinfield.bind("<Return>", lambda event: posint(vartype.spins))
    spinfield.bind("<KP_Enter>", lambda event: posint(vartype.spins))
    # create button to submit
    spinbutton = gui.CTkButton(window, text="", image=submiticon, command= lambda: posint(vartype.spins))
    spinbutton.grid(row=3, column=1, padx=20, pady=10)

    # ask user how many numbers on slot machine
    slotfieldlabel = gui.CTkLabel(window, text="How many numbers on the slot machine?", font=text)
    slotfieldlabel.grid(row=4, column=0, padx=20, pady=10)
    # create input field and place it
    slotfield = gui.CTkEntry(window, font=text)
    slotfield.grid(row=5, column=0, padx=20, pady=10)
    # bind enter (and numpad enter) key to submit
    slotfield.bind("<Return>", lambda event: posint(vartype.slots))
    slotfield.bind("<KP_Enter>", lambda event: posint(vartype.slots))
    # create button to submit
    slotbutton = gui.CTkButton(window, text="", image=submiticon, command= lambda: posint(vartype.slots))
    slotbutton.grid(row=5, column=1, padx=20, pady=10)

    # ask user what to guess on
    guessfieldlabel = gui.CTkLabel(window, text="What number to guess on?", font=text)
    guessfieldlabel.grid(row=6, column=0, padx=20, pady=10)
    # create input field and place it
    guessfield = gui.CTkEntry(window, font=text)
    guessfield.grid(row=7, column=0, padx=20, pady=10)
    # bind enter (and numpad enter) key to submit
    guessfield.bind("<Return>", lambda event: posint(vartype.guess))
    guessfield.bind("<KP_Enter>", lambda event: posint(vartype.guess))
    # create button to submit
    guessbutton = gui.CTkButton(window, text="", image=submiticon, command= lambda: posint(vartype.guess))
    guessbutton.grid(row=7, column=1, padx=20, pady=10)

    # ask user how much to bet
    betfieldlabel = gui.CTkLabel(window, text="How much to bet?", font=text)
    betfieldlabel.grid(row=8, column=0, padx=20, pady=10)
    # create input field and place it
    betfield = gui.CTkEntry(window, font=text)
    betfield.grid(row=9, column=0, padx=20, pady=10)
    # bind enter (and numpad enter) key to submit
    betfield.bind("<Return>", lambda event: betsubmit())
    betfield.bind("<KP_Enter>", lambda event: betsubmit())
    # create button to submit
    betbutton = gui.CTkButton(window, text="", image=submiticon, command=betsubmit)
    betbutton.grid(row=9, column=1, padx=20, pady=10)

    # create button to start gambling
    startbutton = gui.CTkButton(window, text="GO", font=title, command=spin)
    startbutton.grid(row=10, column=0, columnspan=2, pady=20)

    # start window
    window.mainloop()


"""
    MAIN THREAD
"""
main()