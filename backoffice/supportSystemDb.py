
"""
Script to handle statistics of the bot
"""

import os
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors

class SupportSystemManager:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['AirMarshall']
        self.supportSystem = self.airMarshall.supportProfiles

    def register_community_for_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "appliedChannelId":int(0),
            "appliedChannelName":None,
            "supportService":int(0),
        }
        
        try:
            self.supportSystem.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False
        
    def check_support_system_status(self, community_id:int):
        result = self.supportSystem.find_one({"communityId":int(community_id)},
                                                 {"_id":0,
                                                  "supportService":1})
        if result["appliedChannelId"] == 0:
            return False
        else:
            return True
        
    def get_communtiy_settings(self, community_id):
        
        result = self.supportSystem.find_one({"communityId":int(community_id)},
                                                 {"_id":0})
        if result:
            return result
        else:
            return {}
          

    def modify_channel(self, community_id:int, channel_id:int, channel_name:str):
        try:
            self.supportSystem.update_one({"communityId":int(community_id)},
                                                        {"$set":{"appliedChannelId":int(channel_id),
                                                                "appliedChannelName":channel_name}})
            return True
        except errors.PyMongoError:
            return False
    
    def turn_on_off(self, community_id, direction:int):
        result = self.supportSystem.update_one({"communityId":int(community_id)},
                                        {"$set":{"supportService":direction}})   
        if result:
            return True
        else:
            return False
        
        
    def check_if_not_registered(self, community_id:int):
        result = self.supportSystem.find_one({"communityId":community_id})
        if result:
            return False
        else:
            return True
        
    def check_community_reg_status(self, community_id:int):
        result = self.supportSystem.find_one({"communityId":community_id})
        
        if result:
            return True
        else:
            return False
    
    def get_details_of_channel(self, community_id:int):
        result = self.supportSystem.find_one({"communityId":community_id},
                                                 {"_id":0,
                                                  "appliedChannelName":1,
                                                  "appliedChannelId":1,
                                                  })
        if result:
            return result
        else:
            return {}
    
    def check_if_security_activated(self, community_id:int):
        result = self.supportSystem.find_one({"communityId":community_id},
                                                 {"_id":0,
                                                  "welcomeService":1})
        try:
            return int(result['welcomeService'])
        except TypeError:
            return 2
