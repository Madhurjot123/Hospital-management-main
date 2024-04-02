import pymongo

class MongoDBHelper:

    def __init__(self, collection=''):
        uri = "mongodb+srv://madhurjot123:qZsof0U7ui8yKqdx@cluster0.wu0f27q.mongodb.net/?retryWrites=true&w=majority"
        client = pymongo.MongoClient(uri)
        self.db = client['mydatabase']
        self.collection = self.db[collection]
        print("MongoDB Connected")

    def insert(self, document):
        result = self.collection.insert_one(document)
        print("Document Inserted:", result)
        # result.inserted_id -> Document Id
        return result

    def delete(self, query):
        result = self.collection.delete_one(query)
        print("Document Deleted:", result)

    def fetch(self, query=""):
        documents = self.collection.find(query) # find_one()
        return list(documents)

    def update(self, document, query):
        update_query = {'$set': document}
        result = self.collection.update_one(query, update_query)
        print("Updated Document:", result.modified_count)

    def fetch_one(self, query):
        document = self.collection.find_one(query)
        return document

    def fetch_all(self):
        documents = self.collection.find()
        return list(documents)

    def find_one(self, query):
        document = self.collection.find_one(query)
        return document

    def update_one(self, query, update_data):
        result = self.collection.update_one(query, update_data)
        print("Updated Document:", result.modified_count)

    def update_appointment_status(self, appointment_id, status):
        query = {'appointment_id': appointment_id}
        update_data = {'$set': {'status': status}}
        self.update_one(query, update_data)

    def update_appointment_cancel_by_patient(self, appointment_id):
        self.update_appointment_status(appointment_id, 'cancel by patient')

    def update_prescription(self, appointment_id, prescription_data):
        query = {'appointment_id': appointment_id}
        update_data = {'$set': {'prescription': prescription_data}}
        self.update_one(query, update_data)
