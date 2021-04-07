from datetime import date
from .utils import connect_mongodb, Dashboard
from .minicrawlbot import MiniCrawlbot
import os
import time

def track_links_periodically():
    
    try:
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        isTracked = coll.find_one({})["isTracked"]

        # Track all links every Monday
        if date.today().weekday() == 0 and isTracked == False:
            print("Tracking flagged links")
            dash = Dashboard()
            flagged_links = dash.read_db("flagged-links", "darkweb-flagged")
            links_tracker = MiniCrawlbot()
            todays_status = links_tracker.get_todays_status(flagged_links)

            for flagged_link, new_status in zip(flagged_links, todays_status):

                status = coll.find_one({"Link":flagged_link})["Status"]
                if len(status)>=53:
                    status.pop(0)
                status.append(new_status)

                coll.update_one({"Link":flagged_link}, {"$set":{"Status":status, "isTracked":True}})            

            return "The flagged links were tracked! Link status updated!"

        # Update database on Tuesday so as to not perform tracking on other days
        if date.today().weekday() == 1 and isTracked == True:
            print("Resetting tracking for this week")
            coll.update_many({},{"$set":{"isTracked":False}})
            return "Tracking for this week is completed. Next tracking will occur on Monday."
    
    except Exception:
        pass