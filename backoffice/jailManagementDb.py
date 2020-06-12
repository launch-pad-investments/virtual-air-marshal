import pymongo
from pymongo import MongoClient
from pymongo import errors
import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class JailManagement():
    def __init__(self):
        self.connection = MongoClient("mongodb://localhost:27017")
        self.jail = self.connection['JailManagement']
        self.counter = self.jail.counter
        self.jailed = self.jail.jailed

    def get_served_users(self, timestamp):
        all_users = list(self.jailed.find({"end": {"$lt": timestamp}}))
        return all_users
    
    def get_jailed_user(self, discord_id):
        user = self.jailed.find_one({"userId":discord_id},
                                    {"_id":0})
        return user
    
    
    def check_if_in_counter(self, discord_id:int):
        result = self.counter.find_one({"userId":discord_id})
        
        if result:
            return True
        else:
            return False
    
    def apply_user(self, discord_id:int):
        try:
            self.counter.insert_one({"userId":discord_id,
                                            "count":1})
            return True
        except errors.PyMongoError:
            return False
        
    def throw_to_jail(self, user_id:int,community_id:int, expiration:int, role_ids:list):
        try:
            self.jailed.insert_one({"userId":discord_id,
                                            "end":int(expiration),
                                            "roleIds":role_ids,
                                            "community":community_id})
            return True
        except errors.PyMongoError:
            return False
    
    def remove_from_counter(self, discord_id:int):
        try:
            self.counter.delete_one({"userId":discord_id})
            return True
        except errors.PyMongoError:
            return False
    
    def remove_from_jailed(self, discord_id:int):
        try:
            self.jailed.delete_one({"userId":discord_id})
            return True
        except errors.PyMongoError:
            return False
    
    
    def check_if_jailed(self, discord_id:int):
        result = self.jailed.find_one({"userId":discord_id})
        if result:
            return True
        else:
            return False
        
    def increase_count(self, discord_id:int):
        self.counter.update_one({"userId":discord_id},
                                         {"$inc":{"count":1}})
        
        result = self.counter.find_one({"userId":discord_id},
                                       {"_id":0,
                                        "count":1})

        return result['count']