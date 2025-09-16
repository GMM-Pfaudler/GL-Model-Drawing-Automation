from repositories.ofn_db import OFNDB

class OFNService:
    def __init__(self):
        self.ofnDB = OFNDB()

    def get_ofn_by_sfon(self, sfon):
        ofn_details = self.ofnDB.get_by_sfon(sfon=sfon)
        return ofn_details
    
    def get_masters(self, master_names):
        masters = self.ofnDB.get_masters(data=master_names)
        return masters