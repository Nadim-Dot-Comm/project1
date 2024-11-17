#TPRG-2131-01 
#Project 1 - Vending Machine
#Nadim Gutto -- 100665657
#November 15, 2024
#Due Date: November 17, 2024
#This program was half provided by the teacher which I completly finished on my own
#with the help of online resources, class materials, and the links below.
'''
For bonus mark #5, uncomment lines 103, 142, 146, 172, 182 for the amount to show on the interface.
                (click on line # then press alt 4 to uncomment)

For bonus mark #6 see line 200 to see how it shows on the interface.

The lines are commented out becasue it won't work when running pytest.
Make sure the lines listed above are commented out before running pytest.
'''

# PySimpleGUI recipes used:
#
# Persistent GUI example
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#recipe-pattern-2a-persistent-window-multiple-reads-using-an-event-loop
#
# Asynchronous Window With Periodic Update
# https://pysimplegui.readthedocs.io/en/latest/cookbook/#asynchronous-window-with-periodic-update

'''This program simulates a vending machine that accepts coins then waits for a selection.
If the sum of the value of the coins is sufficient for the selection, the machine activates
the servo to deliver the product. Also the use of GUI to simulate a vending machine.'''

import PySimpleGUI as sg #Imports PySimpleGUI library for creating Graphical User Interfaces. 
from time import sleep #Imports the sleep function from the time module.

# Detect if running on Raspberry Pi and set up hardware
hardware_present = False #Hardware (button,servo) is not present).
try:
    from gpiozero import Button, Servo #Imports the Button and Servo classes from the gpiozero library.
    servo = Servo(17)  # Initialize servo on GPIO 17
    key1 = Button(5)   # Button on GPIO 5 acts as "RETURN"
    hardware_present = True #Hardware (button,servo) is present).
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")

#Enable logging during testing
TESTING = True
def log(s):
    """Log output if in testing mode."""
    if TESTING:
        print(s)

"""State machine for a vending machine."""
class VendingMachine:
    PRODUCTS = {
        "SURPRISE": ("SURPRISE", 300),    #300 cents
        "CHIPS": ("CHIPS", 200),          #200 cents
        "CHOCOLATE": ("CHOCOLATE", 125),  #125 cents
        "POP": ("POP", 250),              #250 cents
        "WATER": ("WATER", 175)           #175 cents
        }
    
    COINS = {
        "5\u00A2": ("5", 5),         #5 cents
        "10\u00A2": ("10", 10),     #10 cents
        "25\u00A2": ("25", 25),     #25 cents
        "100\u00A2": ("1.00", 100),       #100 cents
        "200\u00A2": ("2.00", 200)        #200 cents
        }

    def __init__(self):
        self.state = None
        self.states = {}
        self.event = ""
        self.amount = 0
        self.change_due = 0
        self.coin_values = sorted([coin[1] for coin in self.COINS.values()], reverse=True)
#         log("Available coin values: " + str(self.coin_values))
    
    '''Adds a stste to the collection of states'''
    def add_state(self, state):
        self.states[state.name] = state
    
    """Transition to the given state."""
    def go_to_state(self, state_name):
        new_state = self.states.get(state_name) #Retrieves a state from self.states using the state’s name (state_name) and stores it in new_state
        if not new_state:  #Checks if new_state is None(not found)
            log(f"State '{state_name}' not found!") #Logs an error message that the state with the given name (state_name) wasn't found in the collection.
            return
        
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.on_exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.on_entry(self)
    
    """Update the machine based on the current state."""
    def update(self):
        if self.state:
            self.state.update(self)
    
    """Add the value of the selected coin to the current balance.."""
    def add_coin(self, coin):
        self.amount += self.COINS[coin][1]          #Add the coin's value to the current amount
        log(f"CURRENT AMOUNT: {self.amount}\u00A2") #Logs the updated balance
#         window["amount_display"].update(f"Current Amount: {self.amount}\u00A2")

    """Physical 'RETURN' button callback."""
    def button_action(self):
        self.event = 'RETURN'
        self.update()

# Abstract state class
class State:
    """Superclass for all states in the vending machine."""
    _NAME = ""
    @property
    def name(self):
        return self._NAME
    def on_entry(self, machine):
        pass
    def on_exit(self, machine):
        pass
    def update(self, machine):
        pass

# Implement state classes for the vending machine
'''Represents the "waiting" state in a state machine and handles transitions when a specific event occurs'''
class WaitingState(State):
    _NAME = "waiting"
    def update(self, machine): #Handle actions based on the current event,then goes to state 'add_coins' if coin inserted
        if machine.event in machine.COINS:
            machine.add_coin(machine.event)  ##Add the inserted coin to the current amount
            machine.go_to_state('add_coins') #Transition to state 'add_coins'


'''Represents the "add_coins" state in a state machine for a vending machine'''
class AddCoinsState(State):
    _NAME = "add_coins"
    def update(self, machine): #Handles current event and updates the machine's state accordingly.
        if machine.event == "RETURN":  #Returns the total change if the "RETURN" button is pressed
            machine.change_due = machine.amount
            machine.amount = 0                  #Resets the amount to zero after returning the change
            machine.go_to_state('count_change') #Transition to state 'count_change'
#             window["amount_display"].update(f"Returning Change: {machine.change_due} \u00A2")
        
        elif machine.event in machine.COINS:
            machine.add_coin(machine.event) #Add the inserted coin to the current amount
#             window["amount_display"].update(f"Current Amount: {machine.amount} \u00A2")
        
        elif machine.event in machine.PRODUCTS:
            product_price = machine.PRODUCTS[machine.event][1] #Gets the price of the selected product
            if machine.amount >= product_price:                #Checks if the balance is enough for the product
                machine.go_to_state('deliver_product')         #Transition to state 'deliver_product'
            else:
                log("Insufficient funds")


'''Executes the actions to dispense a product and update the machine state.'''
class DeliverProductState(State):
    _NAME = "deliver_product"
    def on_entry(self, machine): #Handles the action when entering 'deliver_product' state
        product_price = machine.PRODUCTS[machine.event][1]
        machine.amount -= product_price #Deducts the price of the product from the current balance.
        log(f"DISPENSING: {machine.PRODUCTS[machine.event][0]}") #Logs the product being dispensed.

        '''Dispensing action is simulated via servo'''
        if hardware_present:
            servo.min()  
            sleep(1)
            servo.max() 
            sleep(1)
            servo.min()
        log(f"REMAINING BALANCE: {machine.amount} \u00A2") #Logs remaining balance
#         window["amount_display"].update(f"Remaining Balance: {machine.amount} \u00A2")
        
        machine.go_to_state('add_coins') #Transition to state 'add_coins'
        

'''Responsible for calculating and returning the change due, and resets the machine's state.'''
class CountChangeState(State):
    _NAME = "count_change"
    def on_entry(self, machine): #Handles the action when entering 'count_change' state
        log(f"RETURNING TOTAL CHANGE: {machine.change_due} \u00A2") #Logs total change due
#         window["amount_display"].update(f"Returning Change: {machine.change_due} \u00A2")
        machine.amount = 0             #Resets total amount
        machine.change_due = 0         #Reset total change
        machine.go_to_state('waiting') #Transition to state 'waiting'


# Main GUI program
if __name__ == "__main__":
    sg.theme('DefaultNoMoreNagging')

    '''Set up GUI layout for coin section'''
    coin_col = [[sg.Text("INSERT COINS", font=("Helvetica", 24))]]
    for item in VendingMachine.COINS:
        coin_col.append([sg.Button(item, font=("Helvetica", 18))])

    '''Set up GUI layout for product section'''
    select_col = [[sg.Text("SELECT ITEM", font=("Helvetica", 24))]]
    for item, (name, price) in VendingMachine.PRODUCTS.items():
        price_text = f"{name} --- {price} \u00A2"
        select_col.append([sg.Button(price_text, font=("Helvetica", 18), key=item)])

    '''Set up GUI layout'''
    layout = [[sg.Column(coin_col), sg.VSeparator(), sg.Column(select_col)],
              [sg.Text("Current Amount: 0 \u00A2", key="amount_display", font=("Helvetica", 12))],
              [sg.Button("RETURN", font=("Helvetica", 12))]]
    window = sg.Window('Vending Machine', layout)

    #Initialize vending machine with states
    vending = VendingMachine()
    vending.add_state(WaitingState())         #Add the "Waiting" state
    vending.add_state(AddCoinsState())        #Add the "Add Coins" state
    vending.add_state(DeliverProductState())  #Add the "Deliver Product" state
    vending.add_state(CountChangeState())     #Add the "Count Change" state
    vending.go_to_state('waiting')            #Set the initial state to 'waiting'

    #Register physical RETURN button callback
    if hardware_present:
        key1.when_pressed = vending.button_action #Hardware button preforms the same as vending button

    #Event loop for GUI
    while True:
        event, values = window.read(timeout=10) #Read the event from the window with a timeout of 10ms
        
        if event != '__TIMEOUT__': #If the event is not a timeout, log the event
            log(event)
        
        if event in (sg.WIN_CLOSED, 'Exit'): #if the user clicks 'Exit', break the loop and close the window 
            break
        
        vending.event = event   #Set the current event for the vending machine
        vending.update()        #Update the vending machine's state based on the event

    window.close()              #Close the window when the event loop ends
    print("Normal exit")        #Print "Normal exit" when the prgram ended normally
