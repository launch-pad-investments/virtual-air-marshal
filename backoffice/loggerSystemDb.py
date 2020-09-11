"""
Script to handle logger background
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors
from colorama import Fore


class LoggerSystem:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['VirtualAirMarshal']
        self.loggin = self.airMarshall.loggerSystem

    def register_community_for_logger_service(self, community_id, community_name, owner_id, owner_name):
        community_profile = {
            "communityId": int(community_id),
            "communityName": str(community_name),
            "communityOwnerName": str(owner_name),
            "communityOwnerId": int(owner_id),
            "appliedChannelId": int(0),
            "appliedChannelName": None,
            "loggerService": int(0),
        }

        try:
            self.loggin.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False

    def remove_from_logger_system(self, community_id: int):
        try:
            result = self.loggin.delete_one({"communityId": community_id})
        except errors.PyMongoError as e:
            print(Fore.LIGHTRED_EX + f'Logger system could not remove {community_id}: {e}')

    def get_channel(self, community_id: int):
        result = self.loggin.find_one({"communityId": int(community_id)},
                                      {"_id": 0,
                                       "appliedChannelId": 1})
        if result:
            return result["appliedChannelId"]
        else:
            return 0

    def check_logger_system_status(self, community_id: int):
        result = self.loggin.find_one({"communityId": int(community_id)},
                                      {"_id": 0,
                                       "loggerService": 1})
        try:
            if result["loggerService"] == 0:
                return False
            else:
                return True
        except TypeError:
            return False

    def get_communtiy_settings(self, community_id):

        result = self.loggin.find_one({"communityId": int(community_id)},
                                      {"_id": 0})
        if result:
            return result
        else:
            return {}

    def modify_channel(self, community_id: int, channel_id: int, channel_name: str):
        try:
            self.loggin.update_one({"communityId": int(community_id)},
                                   {"$set": {"appliedChannelId": int(channel_id),
                                             "appliedChannelName": channel_name}})
            return True
        except errors.PyMongoError:
            return False

    def turn_on_off(self, community_id: int, direction: int):
        result = self.loggin.update_one({"communityId": int(community_id)},
                                        {"$set": {"loggerService": direction}})
        print(result.modified_count)
        print(result.modified_count)
        if result:
            return True
        else:
            return False

    def check_if_not_registered(self, community_id: int):
        result = self.loggin.find_one({"communityId": community_id})
        if result:
            return False
        else:
            return True

    def check_community_reg_status(self, community_id: int):
        result = self.loggin.find_one({"communityId": community_id})

        if result:
            return True
        else:
            return False

    def check_if_not_registered(self,community_id):
        result = self.loggin.find_one({"communityId": community_id})

        if result:
            return False
        else:
            return True

    def get_details_of_channel(self, community_id: int):
        result = self.loggin.find_one({"communityId": community_id},
                                      {"_id": 0,
                                       "appliedChannelName": 1,
                                       "appliedChannelId": 1,
                                       })
        if result:
            return result
        else:
            return {}

    def check_if_logger_activated(self, community_id: int):
        result = self.loggin.find_one({"communityId": community_id},
                                      {"_id": 0,
                                       "loggerService": 1})
        try:
            return int(result['loggerService'])
        except TypeError:
            return 2
