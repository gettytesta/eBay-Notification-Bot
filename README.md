# eBay-Notification-Bot

This python program can send an email to the user when a new listing for a certain item is posted on eBay. 

The application uses eBay's Finding API to query for current listings and compares them against a database of previous listings in MongoDB to check for any new listings. The code then uses SMTP to send an email notifying the user of any new listings.
