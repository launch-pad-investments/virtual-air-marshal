import pymongo
from pymongo import MongoClient
from pymongo import errors
import os
import sys
from colorama import Fore

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class JailManagement():
    def __init__(self):
        self.connection = MongoClient("mongodb://localhost:27017")
        self.jail = self.connection['AirMarshall']
        self.jailed = self.jail.jailedMembers

    def get_served_users(self, timestamp):
        all_users = list(self.jailed.find({"end": {"$lt": timestamp}}))
        return all_users

    def get_jailed_user(self, discord_id):
        user = self.jailed.find_one({"userId": discord_id},
                                    {"_id": 0})
        if user:
            return user
        else:
            return {}

    def throw_to_jail(self, user_id: int, community_id: int, expiration: int, role_ids: list):
        try:
            self.jailed.insert_one({"userId": user_id,
                                    "end": int(expiration),
                                    "roleIds": role_ids,
                                    "community": community_id})
            return True
        except errors.PyMongoError:
            return False

    def remove_from_jailed(self, discord_id: int):
        try:
            self.jailed.delete_one({"userId": discord_id})
            return True
        except errors.PyMongoError:
            return False

    def clear_community_jail(self, community_id: int):
        try:
            result = self.jailed.delete_many({"community": community_id})
            print(Fore.LIGHTWHITE_EX + f'Jail clear of users = {result.deleted_count}')
        except errors.PyMongoError as e:
            print(Fore.LIGHTRED_EX + f'Jail could not be cleared of {community_id}: {e}')

    def clear_community_member_jail(self, community_id: int, member_id: int):
        try:
            result = self.jailed.delete_one({"community": community_id, "userId": member_id})
            print(Fore.LIGHTWHITE_EX + f'Jail clear of users = {result.deleted_count}')
        except errors.PyMongoError as e:
            print(
                Fore.LIGHTRED_EX + f'Member {member_id} could not be removed from Jail on community {community_id}: {e}')

    def check_if_jailed(self, user_id: int, community_id):
        result = self.jailed.find_one({"userId": user_id, "community": community_id})
        if result:
            return True
        else:
            return False

    def check_if_in_jail(self, user_id: int):
        """
        For on_message
        """
        result = self.jailed.find_one({"userId": user_id})
        if result:
            return True
        else:
            return False
        
