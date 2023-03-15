#!/usr/bin/python3

import reservationapi
import configparser
import sys
import time
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError, UnexpectedError, RetriesExhaustedError)

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))


band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

# Your code goes here

def start_App(type1: reservationapi, type2: reservationapi):

    print("Welcome to The Wedding Planner!\n")
    print("We will do our best to find you the best reservations for your hotel and band")
    time.sleep(1)
    print("First we will look for the common slots where the band and hotel are available.")
    time.sleep(2)

    # Check the availability of common slots and getting the best slot back.
    optimal_slot = earliest_Common_Slot(type1,type2)

    # If there are no common slots
    if optimal_slot==-1:
        book_When_noCommon(type1, type2)

    # When there is a common slot.
    else:
        # Realease any curently booked slots
        release_Booked_Slots(type1, type2)

        # Book earliest common slot.
        book_Best(optimal_slot, type1, type2)

        # Recheck once for better bookings
        reCheck(optimal_slot, type1, type2)




def book_When_noCommon(type1: reservationapi, type2: reservationapi):

    # Find the best slot for each invidually since there is no common slot.
    bbest = get_Next_Slot_Available(type1)
    print("\nWe will arrange a reservation for the band in slot " + str(bbest) + " Which is the earliest available slot.")
    time.sleep(1)
    hbest = get_Next_Slot_Available(type2)
    print("\nWe will arrange a reservation for the hotel in slot " + str(hbest) + " Which is the earliest available slot.")

    # Realease any curently booked slots
    release_Booked_Slots(type1, type2)

    # Reserve the 2 slots for each.
    slot_Reserve(type1, bbest)
    print("~Band\n")
    slot_Reserve(type2, hbest)
    print("~Hotel\n")

    reCheck_When_noCommon(bbest ,hbest, type1, type2)

def reCheck_When_noCommon(bbest: int, hbest: int ,type1: reservationapi, type2: reservationapi) :
    print("Re-Checking if there exist an earlier available slot......")

    # Find if there exist a common slot now or maybee just better slots.
    new =  earliest_Common_Slot(type1,type2)

    # If no common slots where found again...
    if new ==-1 : 
        # Find the best slot for each invidually since there is no common slot.
        new_bbest = get_Next_Slot_Available(type1)
        new_hbest = get_Next_Slot_Available(type2)

        # re-Check if the band has a better slot.
        if new_bbest < bbest :
            release_slot(type1, new_bbest)
            print("~Band\n")
            slot_Reserve(type1, new_bbest)
            print("~Band\n")
            print("\nYour reservation for the Band has been completed, and slot " + str(new_bbest) + " were booked for you, thank you.")
        else:
            print("\nYour reservation for the Band has been completed, and slot " + str(bbest) + " were booked for you, thank you.")
                

        # re-Check if the Hotel has a better slot.
        if new_bbest < bbest :
            release_slot(type2, new_hbest)
            print("~Hotel\n")
            slot_Reserve(type2, new_hbest)
            print("~Hotel\n") 
            print("\nYour reservation for the Hotel has been completed, and slot " + str(new_hbest) + " were booked for you, thank you.")

        else:
            print("\nYour reservation for the Hotel has been completed, and slot " + str(hbest) + " were booked for you, thank you.")




    else: 
        print("It's your lucky day! it seems we found a common slot after the re-check.")
        # Realease any curently booked slots
        release_Booked_Slots(type1, type2)

        # Book earliest common slot.
        book_Best(new, type1, type2)
        print("Your reservation has been completed, and slot " + str(new) + " were booked for you, thank you.")



def reCheck(old: int , type1: reservationapi, type2: reservationapi):
    print("Re-Checking if there exist an earlier available slot......")

    # Find the current best slot.
    new = earliest_Common_Slot(type1,type2)

    # If the current is earlier than the old one we found then we're going to re-book.
    if new < old:
        release_Booked_Slots(type1, type2)
        book_Best(new, type1, type2)
        print("Your reservation has been completed, and slot " + str(new) + " were booked for you, thank you.")

def book_Best(best: int , type1: reservationapi, type2: reservationapi):
    print("\nPlease wait while we book slot " + str(best) + " for you.....")
    slot_Reserve(type1, best)
    print("~Band\n")
    slot_Reserve(type2, best)
    print("~Hotel\n")


def release_Booked_Slots(type1: reservationapi, type2: reservationapi):
    print("\nChecking if there are any previously reserved slots and releasing them....")
    band_equiped = slots_Equiped(type1)
    print("~Band\n")
    hotel_equiped = slots_Equiped(type2)
    print("~Hotel\n")
    if band_equiped != []:
        for i in band_equiped:
            slot_release(type1, i['id'])
            print("~Band\n")

    if hotel_equiped != []:
        for j in hotel_equiped:
            slot_release(type2, j['id'])
            print("~Hotel\n")

    print("\nAll slots are free now")        




def earliest_Common_Slot(type1: reservationapi, type2: reservationapi):

    print("\nChecking the availablity of common slots....")

    # Get the lists of available slots for both the hotel and band.
    res1 = type1.get_slots_available()
    res2 = type2.get_slots_available()

    # A list to contain common slots.
    list_Of_Commons = []

    # Find Common slots and append them to the list.
    for i in res1 :
        for j in res2:
            if j['id']== i['id'] :
                list_Of_Commons.append(j['id'])

    # If there are no common slots
    if list_Of_Commons == []:
        print("\nIt appears that there are no common slots to be be reserved.\n We will make sure to reserve you the nearest slots possible... ")

        # Indicating no common slots found.
        return -1

    # If there is any common slot.
    else:
        print("Common slots found are: \n ")
        print(list_Of_Commons)
        time.sleep(1)
        print("\nWe will arrange a reservation for you in slot " + str(list_Of_Commons[0]) + " Which is the earliest available slot.")
    return int(list_Of_Commons[0])           







def get_Next_Slot_Available(type: reservationapi):
        
    try:

        print("\nLoading.....")
        res = type.get_slots_available()
        next_slot = res[0]['id']
        return next_slot

    except BadRequestError as e:
        print("Bad Request Error: Code 400")
        sys.exit() 
    except InvalidTokenError as e:
        print("Invalid Token Error: Code 401")
        sys.exit()   
    except NotProcessedError as e:
        print("Not Processed Error:  Code 404")
        sys.exit()
    except UnexpectedError as e:
        print("Unexpected Error....Shutting down the client.")
        sys.exit() 


def slots_Available(type: reservationapi): # type is basically either a hotel or a band.

    try:
        print("The slots currently available are: ")
        print("\nLoading.....")
        res = type.get_slots_available()
        print(res)

    except BadRequestError as e:
        print("Bad Request Error: Code 400")
        sys.exit() 
    except InvalidTokenError as e:
        print("Invalid Token Error: Code 401")
        sys.exit()   
    except NotProcessedError as e:
        print("Not Processed Error:  Code 404")
        sys.exit()
    except UnexpectedError as e:
        print("Unexpected Error....Shutting down the client.")
        sys.exit() 


def slots_Equiped(type: reservationapi):

    try:
        res = type.get_slots_held()
        print("\nCurrently Equiped slots: " + str(res)) 
        return res
    except BadRequestError as e:
        print("Bad Request Error: Code 400")
        sys.exit() 
    except InvalidTokenError as e:
        print("Invalid Token Error: Code 401")
        sys.exit()   
    except NotProcessedError as e:
        print("Not Processed Error:  Code 404")
        sys.exit()
    except UnexpectedError as e:
        print("Unexpected Error....Shutting down the client.")
        sys.exit()  





def slot_Reserve(type: reservationapi, slot_num: int):

    try:
        res = type.reserve_slot(slot_num)
        print("\nSlot number " + str(slot_num) + " has been reserved successfully.")

    except BadRequestError as e:
        print("Bad Request Error: Code 400")
        sys.exit() 
    except InvalidTokenError as e:
        print("Invalid Token Error: Code 401")
        sys.exit()   
    except NotProcessedError as e:
        print("Not Processed Error:  Code 404")
        sys.exit()

    except SlotUnavailableError as e:
        print("Slot Unavailable Error : Code 409")
        print("Slot " + str(slot_num) + " is either already reserved or currently unavailable.")

    except BadSlotError as e:
        print("Bad Slot Error:  Code: 403")
        print("Slot " + str(slot_num) + " does not exist!")
        sys.exit()   
    except ReservationLimitError as e:
        print("Reservation Limit Error : Code: 451")
        print("The hotel and band restrict a user to hold at most two reservations at any one time.")
        sys.exit()                      
    except UnexpectedError as e:
        print("Unexpected Error....Shutting down the client.")
        sys.exit() 




def slot_release(type: reservationapi, slot_num: int):

    try:
        res = type.release_slot(slot_num)
        print("\nSlot number " + str(slot_num) + " has been released successfully.")
    except BadRequestError as e:
        print("Bad Request Error: Code 400")
        sys.exit() 
    except InvalidTokenError as e:
        print("Invalid Token Error: Code 401")
        sys.exit()   
    except NotProcessedError as e:
        print("Not Processed Error:  Code 404")
        sys.exit()

    except SlotUnavailableError as e:
        print("Slot Unavailable Error : Code 409")
        print("Slot " + str(slot_num) + " is either already reserved or currently unavailable.")

    except BadSlotError as e:
        print("Bad Slot Error:  Code: 403")
        print("Slot " + str(slot_num) + " does not exist!")
        sys.exit()   
    except ReservationLimitError as e:
        print("Reservation Limit Error : Code: 451")
        print("The hotel and band restrict a user to hold at most two reservations at any one time.")
        sys.exit()                      
    except UnexpectedError as e:
        print("Unexpected Error....Shutting down the client.")
        sys.exit() 









start_App(band, hotel)




