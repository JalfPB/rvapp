from pymongo import MongoClient  
uri = "mongodb://localhost:27017/rvapp"
client = MongoClient(uri)
db = client.rvapp
farmacias = db.farmacias

cursor = farmacias.find()
for u in cursor:
    print(u)