#!/usr/bin/python3

import reservationapi
import configparser
import sys
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

def release_Booked_Slots(type1: reservationapi):
    print("\nCancelling any previously reserved slots....")
    band_equiped = slots_Equiped(type1)



    if band_equiped != [None]:
        for i in band_equiped:
            slot_release(type1, i['id'])



    print("\nAll slots are free now")


def get_Next_Slot_Available(available):
        next_slot = available[0]['id']
        return next_slot



def slots_Available(type: reservationapi): # type is basically either a hotel or a band.

    try:
        print("The slots currently available are: ")
        print("\nLoading.....")
        res = type.get_slots_available()
        print(res)
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
        raise ReservationLimitError                      
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


# Print out the slots available and return the same printed list.
slots_avail = slots_Available(band)

# Find the next available slot to be reserved from that list, and try reserving it...in case there are already two slots reserved then release them first.
slot = get_Next_Slot_Available(slots_avail)


try:
    # Reserve the slot, but in case there are already two slots reserved then release them first.
    slot_Reserve(band, slot)
except ReservationLimitError as e:  
    print("Whoops, it seems you already have previous reservations, let me cancel them for you then procced...")
    # Cancel previous bookings.
    release_Booked_Slots(band)
    # Now we can reserve a slot.
    slot_Reserve(band, slot)
    





# Show the currently equiped slots.
slots_Equiped(band)

# Now release tha slot we equiped.
slot_release(band, slot)
