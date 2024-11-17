#TPRG-2131-01
#Project 1 testing code
#Nadim Gutto -- 100665657
#November 15, 2024
#Due Date: November 17, 2024
#This program was provided by the teacher which I completly finished on my own
#with the help of online resources and class materials.

'''If pytest is not working go to vending_machine.py file for an explination'''


"""This program test the functionality of the file vending_machine.py"""

from vending_machine import VendingMachine, WaitingState, AddCoinsState, DeliverProductState, CountChangeState

def test_VendingMachine():
    # new machine object
    vending = VendingMachine()
    
    vending.add_state(WaitingState())        #Machine waits for user input
    vending.add_state(AddCoinsState())       #User inserts coins
    vending.add_state(DeliverProductState()) #Product is dispensed
    vending.add_state(CountChangeState())    #Change is returned to the user

    #Transtion to initial state
    vending.go_to_state('waiting')           #when machine is idle
    assert vending.state is not None, "State transition failed: 'waiting' state not set"
    assert vending.state.name == 'waiting'   #Current state
    
    # test that the first coin causes a transition to 'add_coins' state
    vending.event = '200\u00A2'              #Inserting 200 cents
    vending.update()                         #Processes the event of inserting coin
    assert vending.state.name == 'add_coins' #Transitioning to 'add_coins'
    assert vending.amount == 200             #Current amount after inserting 200 cents
    
    #Simulates selecting a product that cost 200 cents
    vending.event = 'CHOCOLATE'               #Selecting product
    vending.update()                          #Processes the event of selecting the product
    assert vending.state.name == 'add_coins'  #Remain in 'add_coins' state after product selection
    assert vending.amount == 75               #Remaining balance after dispensing
    
    #Test returning change
    vending.event = 'RETURN'                 #User presses the 'RETURN' button to get change
    vending.update()                         #Processes the event of returning the change
    assert vending.state.name == 'waiting'   #Returns change, goes back to 'waiting' state
    assert vending.change_due == 0           #Change = 0, after returning the change
    
