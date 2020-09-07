import pymongo
from pymongo import MongoClient
from pymongo import errors
import os
import sys
from colorama import Fore

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class BotStructureCheck:
    def __init__(self):
        self.connection = MongoClient("mongodb://localhost:27017")
        self.vam = self.connection["VirtualAirMarshal"]
        self.required_collections = ["jailedMembers",  # Collection storing all jailled members
                                     "jailProfiles",  # Collection storing all communities applied for jair service
                                     "spamProfiles",  # Collection storing all communities applied for spam preventions
                                     "supportProfiles"  # Collection storing all communities applied for support system
                                     ]
        
    def check_collections(self):
        """ Check bots backend on load"""
        bot_collections = self.vam.list_collection_names()
        print(Fore.GREEN + "Checking Virtual Air Marshal backend integrity")
        for collection in self.required_collections:
            if collection not in bot_collections:
                self.vam.create_collection(collection)
                print(Fore.YELLOW + f"{collection.upper()} has been created!")
            else:
                print(Fore.GREEN + f'{collection.upper()} already exists')
        print("Done! Ready to go ")
