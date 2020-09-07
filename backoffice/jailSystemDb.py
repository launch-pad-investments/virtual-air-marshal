
"""
Script to handle statistics of the bot
"""

import os
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors
from colorama import Fore

class JailSystemManager:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['VirtualAirMarshal']
        self.jailSystem = self.airMarshall.jailProfiles

    def register_community_for_jail_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "jailService":int(0),
            "jailRoleId":None,
            "jailRoleName":None
        }
        
        try:
            self.jailSystem.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False
        
    def remove_from_jail_system(self, community_id:int):
        try:
            result = self.jailSystem.delete_one({"communityId":community_id})
            print(Fore.LIGHTWHITE_EX + f'Jail system community deleted = {result.deleted_count}')
        except errors.PyMongoError as e:
            print(Fore.LIGHTRED_EX + f'Jail system could not remove {community_id}: {e}')

    def turn_on_off(self, community_id, direction:int):
        try:
            self.jailSystem.update_one({"communityId":int(community_id)},
                                                {"$set":{"jailService":direction}})   
            return True
        except errors.PyMongoError:
            return False

    def get_jail_status(self, community_id:int):
        result = self.jailSystem.find_one({"communityId":community_id},
                                          {"_id":0,
                                           "jailService":1})
        try:
            return int(result['jailService'])
        except TypeError:
            return 2
            
    def jail_activated(self, community_id:int):
        result = self.jailSystem.find_one({"communityId":community_id},
                                          {"_id":0,
                                           "jailService":1})
        try:
            if int(result['jailService'])==1:
                return True
            else:
                return False
        except TypeError:
            return False
        
    def check_if_jail_not_registered(self, community_id:int):
        result = self.jailSystem.find_one({"communityId":community_id})
        if result:
            return False
        else:
            return True
        
    def check_if_jail_registered(self, community_id:int):
        result = self.jailSystem.find_one({"communityId":community_id})
        
        if result:
            return True
        else:
            return False
    