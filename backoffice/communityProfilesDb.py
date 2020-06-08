
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
        self.communityProfiles = self.airMarshall.welcomeComSettings

    def register_community_for_service(self, community_id,community_name, owner_id, owner_name):
        community_profile = {
            "communityId":int(community_id),
            "communityName":str(community_name),
            "communityOwnerName":str(owner_name),
            "communityOwnerId":int(owner_id),
            "appliedChannel":int(0),
            "appliedMessage":int(0),
            "welcomeService":int(0),
        }
        
        try:
            self.communityProfiles.insert(community_profile)
            return True
        except errors.PyMongoError:
            return False

        
    def check_community_existance(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id})
        
        if result:
            return True
        else:
            return False
        
    def check_if_turned_on(self, community_id:int):
        result = self.communityProfiles.find_one({"communityId":community_id},
                                                 {"_id":0,
                                                  "welcomeService":1})
        return result['weclomeService']
    
