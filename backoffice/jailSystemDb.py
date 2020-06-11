
"""
Script to handle statistics of the bot
"""

import os
import sys
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
from pymongo import MongoClient, errors

class JailSystemManager:
    def __init__(self):
        self.connection = MongoClient('mongodb://localhost:27017/')
        self.airMarshall = self.connection['AirMarshall']
        self.jailSystem = self.airMarshall.jailProfiles

    def register_community_for_jail_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "jailService":int(0),
            "jailRoleId":None,
        }
        
        try:
            self.jailSystem.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False
        
    def turn_on_off(self, community_id, direction:int):
        result = self.jailSystem.update_one({"communityId":int(community_id)},
                                            {"$set":{"welcomeService":direction}})   

        

