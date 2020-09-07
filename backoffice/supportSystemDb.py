"""
Script to handle support background
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors
from colorama import Fore


class SupportSystemManager:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['VirtualAirMarshal']
        self.supportSystem = self.airMarshall.supportProfiles

    def register_community_for_support_service(self, community_id, community_name, owner_id, owner_name):
        community_profile = {
            "communityId": int(community_id),
            "communityName": str(community_name),
            "communityOwnerName": str(owner_name),
            "communityOwnerId": int(owner_id),
            "appliedChannelId": int(0),
            "appliedChannelName": None,
            "supportService": int(0),
        }
        from pprint import pprint
        pprint(community_profile)
        try:
            self.supportSystem.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False

    def remove_from_support_system(self, community_id: int):
        try:
            result = self.supportSystem.delete_one({"communityId": community_id})
            print(Fore.LIGHTWHITE_EX + f'Support system community deleted = {result.deleted_count}')
        except errors.PyMongoError as e:
            print(Fore.LIGHTRED_EX + f'Support system could not remove {community_id}: {e}')

    def get_channel(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": int(community_id)},
                                             {"_id": 0,
                                              "appliedChannelId": 1})
        if result:
            return result["appliedChannelId"]
        else:
            return 0

    def check_support_system_status(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": int(community_id)},
                                             {"_id": 0,
                                              "supportService": 1})
        try:
            if result["supportService"] == 0:
                return False
            else:
                return True
        except TypeError:
            return False

    def get_communtiy_settings(self, community_id):

        result = self.supportSystem.find_one({"communityId": int(community_id)},
                                             {"_id": 0})
        if result:
            return result
        else:
            return {}

    def modify_channel(self, community_id: int, channel_id: int, channel_name: str):
        try:
            self.supportSystem.update_one({"communityId": int(community_id)},
                                          {"$set": {"appliedChannelId": int(channel_id),
                                                    "appliedChannelName": channel_name}})
            return True
        except errors.PyMongoError:
            return False

    def turn_on_off(self, community_id: int, direction: int):
        print(direction)
        print(community_id)
        result = self.supportSystem.update_one({"communityId": int(community_id)},
                                               {"$set": {"supportService": direction}})
        print(result.modified_count)
        print(result.modified_count)
        if result:
            return True
        else:
            return False

    def check_if_not_registered(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": community_id})
        if result:
            return False
        else:
            return True

    def check_community_reg_status(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": community_id})

        if result:
            return True
        else:
            return False

    def get_details_of_channel(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": community_id},
                                             {"_id": 0,
                                              "appliedChannelName": 1,
                                              "appliedChannelId": 1,
                                              })
        if result:
            return result
        else:
            return {}

    def check_if_support_activated(self, community_id: int):
        result = self.supportSystem.find_one({"communityId": community_id},
                                             {"_id": 0,
                                              "supportService": 1})
        try:
            return int(result['supportService'])
        except TypeError:
            return 2
