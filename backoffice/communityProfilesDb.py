
"""
Script to handle statistics of the bot
"""

import os
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors

class CommunityManager:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['AirMarshall']
        self.communityProfiles = self.airMarshall.communityProfiles

    def register_community_for_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "appliedChannelId":int(0),
            "appliedChannelName":None,
            "appliedMessageId":int(0),
            "welcomeService":int(0),
            "jailService":int(0)
        }
        
        try:
            self.communityProfiles.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False
        
    def check_welcome_channel_status(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":int(community_id)},
                                                 {"_id":0,
                                                  "appliedChannelId":1})
        if result["appliedChannelId"] == 0:
            return False
        else:
            return True
        
    def check_reaction_message_status(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":int(community_id)},
                                                 {"_id":0,
                                                  "appliedMessageId":1})
        if result["appliedChannelId"] == 0:
            return False
        else:
            return True      

    def modify_channel(self, community_id:int, channel_id:int, channel_name:str):
        result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                                    {"$set":{"appliedChannelId":int(channel_id),
                                                             "appliedChannelName":channel_name}})

    def modify_message(self,community_id:int, channel_id:int, channel_name:str, ):
        result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                                    {"$set":{"appliedMessageId":channel_id}})
    
    def turn_on_off(self, community_id, direction:int, service_type:int):
        if service_type == 1:
            result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                                        {"$set":{"jailService":direction}})
        elif service_type == 2:
            result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                            {"$set":{"welcomeService":direction}})   
        
        
    def check_if_not_registered(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id})
        
        if result:
            return False
        else:
            return True
        
    def check_community_reg_status(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id})
        
        if result:
            return True
        else:
            return False
    
    def get_details_of_channel(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id},
                                                 {"_id":0,
                                                  "appliedChannelName":1,
                                                  "appliedChannelId":1,
                                                  "appliedMessageId":1,
                                                  })
        return result
    
    def check_if_security_activated(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id},
                                                 {"_id":0,
                                                  "welcomeService":1})
        try:
            return result['weclomeService']
        except TypeError:
            return 2