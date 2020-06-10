
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
        
        #TODO rewrite to two separate files
        self.communityProfiles = self.airMarshall.communityProfiles

    def register_community_for_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "appliedChannelId":int(0),
            "appliedChannelName":None,
            "appliedMessageId":None,
            "welcomeService":int(0),
            "jailService":int(0),
            "jailRoleId":None,
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
        
    def get_communtiy_settings(self, community_id):
        
        result = self.communityProfiles.find_one({"communityId":int(community_id)},
                                                 {"_id":0})
        if result:
            return result
        else:
            return {}
        
    def check_reaction_message_status(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":int(community_id)},
                                                 {"_id":0,
                                                  "appliedMessageId":1})
        if result["appliedMessageId"] == 0:
            return False
        else:
            return True      

    def modify_channel(self, community_id:int, channel_id:int, channel_name:str):
        try:
            self.communityProfiles.update_one({"communityId":int(community_id)},
                                                        {"$set":{"appliedChannelId":int(channel_id),
                                                                "appliedChannelName":channel_name}})
            return True
        except errors.PyMongoError:
            return False

    def modify_message(self,community_id:int, message_id:int):
        try:
            self.communityProfiles.update_one({"communityId":int(community_id)},
                                                        {"$set":{"appliedMessageId":message_id}})
            return True
        except errors.PyMongoError:
            return False
    
    def turn_on_off(self, community_id, direction:int, service_type:int):
        # Direction == 1 --> ON
        # Direction == 0 --> OFF
        if service_type == 1:
            result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                                        {"$set":{"jailService":direction}})
            
        elif service_type == 2:
            result = self.communityProfiles.update_one({"communityId":int(community_id)},
                                            {"$set":{"welcomeService":direction}})   
        if result:
            return True
        else:
            return False
        
        
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
            return int(result['welcomeService'])
        except TypeError:
            return 2
        
    # def get_active_jails(self):
    #     """
    #     Returns the list of communities who have applied for jail service
    #     """
    #     result = list(self.communityProfiles.find({"jailService":{"$gt":0}},
    #                                               {"_id":0,
    #                                                "communityId":1}))
        
    #     return result