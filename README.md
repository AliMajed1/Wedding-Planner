# Wedding-Planner

This is a Python script that helps you find the best slots for booking a hotel and a band for your wedding. The script uses two APIs provided by a hotel and a band reservation service, respectively.

The script is designed to work in scenarios where there may or may not be common slots available for booking both the hotel and the band. If common slots are available, the script will book them, otherwise it will find the earliest slots available for each and book them individually.

To use the script, you need to have access to the two APIs and provide their endpoints and authentication keys in a configuration file called api.ini. The script will read this file to instantiate two objects of the ReservationApi class (provided by the APIs).

Once the APIs are set up, you can run the start_App function, passing the two ReservationApi objects as arguments. This function will print some messages to guide you through the booking process and call some helper functions to find and book the slots.

The script also handles some common errors that may occur during the booking process, such as bad requests, invalid tokens, slot unavailability, and retries exhaustion. If an error occurs, the script will raise an exception of a specific type defined in the exceptions.py file.

This script is intended as a simple example of how to use two APIs in combination and how to handle common errors in Python. You are free to use and modify it as you like.


This software was developed during my 2st year as an Artificial Intelligence student at the University of Manchester, it was submitted as an assessed coursework for the COMP28112 course unit.
