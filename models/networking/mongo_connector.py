from os import getenv
from urllib.parse import quote_plus

import pymongo
from pymongo.errors import OperationFailure
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoConnector:
    __client: MongoClient = None

    def __init__(self):
        name = quote_plus(getenv("DB_USER"))
        password = quote_plus(getenv("DB_PASS"))
        cluster = getenv("DB_CLUSTER")
        db_name = getenv("DB_NAME")

        uri = 'mongodb+srv://' + name + ':' + password + '@' + cluster + '/?retryWrites=true&w=majority'

        # Create a new client and connect to the server
        self.__client = MongoClient(uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.__client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        # use a database named "myDatabase"
        self.__db = self.__client.myDatabase

        # use the defined collection in the database
        self.__my_collection = self.__db[db_name]

    # drop the collection in case it already exists
    def drop(self):
        try:
            self.__my_collection.drop()

            # return a friendly error if an authentication error is thrown
        except OperationFailure:
            print(
                "An authentication error was received. Are your username and password correct in your connection string?")
            raise Exception(
                "An authentication error was received. Are your username and password correct in your connection string?")

    # INSERT DOCUMENTS
    #
    # You can insert individual documents using collection.insert_one().
    # In this example, we're going to create four documents and then
    # insert them all with insert_many().
    def save(self, data):
        try:
            result = self.__my_collection.insert_many(data)

        # return a friendly error if the operation fails
        except pymongo.errors.OperationFailure:
            print(
                "An authentication error was received. Are you sure your database user is authorized to perform write operations?")
        else:
            inserted_count = len(result.inserted_ids)
            print("I inserted %x documents." % (inserted_count))

            print("\n")

    # FIND DOCUMENTS
    #
    # Now that we have data in Atlas, we can read it. To retrieve all of
    # the data in a collection, we call find() with an empty filter.
    def find(self):
        result = self.__my_collection.find()

        if result:
            for doc in result:
                my_recipe = doc['name']
                my_game_count = len(doc['ingredients'])
                my_win_times = doc['winners']
                print(
                    "%s has %x ingredients and takes %x minutes to make." % (my_recipe, my_game_count, my_win_times))

        else:
            print("No documents found.")

        print("\n")

    # We can also find a single document. Let's find a document
    # that has the string "potato" in the ingredients list.
    def find_one(self, table, data):
        my_doc = self.__my_collection.find_one({table: data})

        if my_doc is not None:
            print("a player that has %s as a name." % data)
            print(my_doc)
        else:
            print("I didn't find any player that contain %s as a name." % data)
        print("\n")

    # UPDATE A DOCUMENT
    #
    # You can update a single document or multiple documents in a single call.
    #
    # Here we update the prep_time value on the document we just found.
    #
    # Note the 'new=True' option: if omitted, find_one_and_update returns the
    # original document instead of the updated one.
    def update(self, target: dict, data: dict):
        my_doc = self.__my_collection.find_one_and_update(target, {"$set": data}, new=True)
        if my_doc is not None:
            print("Here's the updated player:")
            print(my_doc)
        else:
            print("I didn't find any player that contain %s as a name." % data)
        print("\n")

    # DELETE DOCUMENTS
    #
    # As with other CRUD methods, you can delete a single document
    # or all documents that match a specified filter. To delete all
    # of the documents in a collection, pass an empty filter to
    # the delete_many() method. In this example, we'll delete two of
    # the recipes.
    #
    # The query filter passed to delete_many uses $or to look for documents
    # in which the "name" field is either "elotes" or "fried rice".
    def delete(self, targets: list[dict[str, str]]):
        my_result = self.__my_collection.delete_many({"$or": targets})
        print("I deleted %x records." % (my_result.deleted_count))
        print("\n")
