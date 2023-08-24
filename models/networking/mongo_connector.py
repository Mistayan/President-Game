import logging
from os import getenv
from pprint import pprint
from urllib.parse import quote_plus

import pymongo
from coloredlogs.converter import html_encode
from pymongo.errors import OperationFailure
from pymongo.mongo_client import MongoClient

from models.networking.db import Database


class MongoConnector(Database):
    __client: MongoClient = None

    def __init__(self, game_name: str, online: bool = True):
        # encode the username and password to bytes and then URL-encode them
        name = html_encode(getenv("DB_USER"))
        password = html_encode(getenv("DB_PASS"))
        db_name = getenv("DB_NAME")
        db_port = int(getenv("DB_PORT", 27017))

        self.__logger = logging.getLogger(__class__.__name__)

        # Create the connection string
        uri = "mongodb://%s:%s@%s" % (
            quote_plus(name), quote_plus(password), "localhost")
        # Create a new client and connect to the server
        with pymongo.timeout(3):
            self.__client = MongoClient(uri, db_port)

        # Send a ping to confirm a successful connection
        try:
            with pymongo.timeout(3):
                self.__client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            super().__init__(game_name)
            self.__logger.critical("Failed to connect to mongo")
            return

        # use a database named "games"
        self.__db = self.__client.get_database(db_name)

        # use the defined collection in the database according to the game that started
        self.__my_collection = self.__db[game_name]

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
                pprint(doc)
                game_type = doc['game']
                rounds_count = doc['plays'].__len__()
                winners = doc['winners']
                print("Game type: %s" % game_type)
                print("Rounds: %s" % rounds_count)
                print("Winners: %s" % winners)
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
    def save(self, target: dict, data: dict):
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


if __name__ == '__main__':
    # load .env
    from dotenv import load_dotenv

    load_dotenv()
    mng = MongoConnector()
    mng.drop()
    mng.save([{"game": "PresidentGame",
               "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [
                   {"player": "AI - George Ku", "rank": 1, "round": 8, "last_play": "J,Spade", "grade": "President"},
                   {"player": "AI - Violet Whalen", "rank": 2, "round": 11, "last_play": "4,Spade", "grade": "Neutre"},
                   {"player": "AI - Nona Martinez", "rank": 3, "round": 11, "last_play": "7,Spade", "grade": "Troufion"}
               ],
               "plays": [
                   ["A,Spade", "A,Clover"], ["3,Clover", "3,Spade", "3,Heart", "K,Spade", "K,Square", "K,Heart"],
                   ["9,Square", "9,Clover", "2,Square", "2,Spade"], ["10,Spade", "10,Clover"],
                   ["5,Heart", "5,Spade", "Q,Square", "Q,Heart"], ["5,Clover", "6,Clover", "K,Clover"],
                   ["6,Spade", "Q,Clover"], ["8,Square", "8,Clover", "J,Heart", "J,Clover", "J,Spade"],
                   ["8,Heart", "10,Heart"], ["6,Heart"], ["4,Spade", "7,Spade"]
               ]
               },
              {"game": "PresidentGame", "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [
                   {"player": "AI - George Ku", "rank": 1, "round": 10, "last_play": "2,Square", "grade": "President"},
                   {"player": "AI - Violet Whalen", "rank": 2, "round": 11, "last_play": "K,Clover", "grade": "Neutre"},
                   {"player": "AI - Nona Martinez", "rank": 3, "round": 11, "last_play": "Q,Clover",
                    "grade": "Troufion"}],
               "plays": [["3,Square", "3,Heart", "7,Clover", "7,Heart", "10,Spade", "10,Square"],
                         ["Q,Heart", "Q,Spade", "Q,Square"], ["8,Clover", "8,Heart", "9,Clover", "9,Heart"],
                         ["4,Square", "4,Spade", "6,Spade", "6,Square", "K,Heart", "K,Square"],
                         ["5,Clover", "8,Square", "8,Spade", "10,Clover"],
                         ["4,Clover", "J,Heart", "J,Square", "J,Spade"], ["5,Spade", "A,Heart", "A,Spade"],
                         ["5,Square", "5,Heart"], ["6,Clover", "2,Spade"], ["9,Spade", "2,Square"],
                         ["Q,Clover", "K,Clover"]]},
              {"game": "PresidentGame", "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [
                   {"player": "AI - George Ku", "rank": 1, "round": 8, "last_play": "6,Clover", "grade": "President"},
                   {"player": "AI - Violet Whalen", "rank": 2, "round": 9, "last_play": "A,Spade", "grade": "Neutre"},
                   {"player": "AI - Nona Martinez", "rank": 3, "round": 9, "last_play": "7,Square",
                    "grade": "Troufion"}], "plays": [["3,Heart", "3,Square", "3,Clover"],
                                                     ["8,Clover", "8,Heart", "8,Spade", "8,Square", "Q,Clover",
                                                      "Q,Heart", "2,Spade", "2,Clover"],
                                                     ["9,Spade", "9,Clover", "9,Square"],
                                                     ["10,Clover", "10,Square", "K,Spade", "K,Heart", "K,Clover",
                                                      "K,Square"], ["7,Heart", "7,Spade", "2,Square", "2,Heart"],
                                                     ["4,Spade", "4,Heart", "4,Square"],
                                                     ["5,Square", "5,Clover", "7,Square", "J,Clover", "J,Spade"],
                                                     ["6,Clover", "Q,Square"], ["A,Spade"]]},
              {"game": "PresidentGame", "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [
                   {"player": "AI - George Ku", "rank": 1, "round": 9, "last_play": "2,Heart", "grade": "President"},
                   {"player": "AI - Violet Whalen", "rank": 2, "round": 11, "last_play": "2,Clover", "grade": "Neutre"},
                   {"player": "AI - Nona Martinez", "rank": 3, "round": 11, "last_play": "A,Spade",
                    "grade": "Troufion"}],
               "plays": [["4,Square", "4,Clover", "7,Clover", "7,Square", "8,Spade", "8,Square", "8,Heart", "8,Clover"],
                         ["10,Heart", "10,Spade", "10,Clover"],
                         ["3,Heart", "3,Square", "9,Heart", "9,Clover", "J,Clover", "J,Heart"],
                         ["K,Square", "K,Spade", "K,Clover"], ["5,Clover", "5,Square"],
                         ["6,Square", "9,Spade", "J,Spade", "Q,Square", "Q,Clover"], ["10,Square", "2,Square"],
                         ["5,Spade", "2,Spade"], ["6,Heart", "2,Heart"], ["7,Heart", "A,Square", "A,Spade"],
                         ["2,Clover"]]},
              {"game": "PresidentGame", "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [{"player": "AI - Violet Whalen", "rank": 1, "round": 10, "last_play": "Q,Spade",
                            "grade": "President"},
                           {"player": "AI - George Ku", "rank": 2, "round": 11, "last_play": "K,Heart",
                            "grade": "Neutre"},
                           {"player": "AI - Nona Martinez", "rank": 3, "round": 11, "last_play": "3,Heart",
                            "grade": "Troufion"}],
               "plays": [["9,Spade", "9,Clover", "A,Spade", "A,Heart", "A,Clover", "A,Square"], ["2,Square", "2,Heart"],
                         ["10,Heart", "10,Spade", "K,Clover", "K,Spade"], ["7,Spade", "7,Clover", "7,Heart"],
                         ["5,Square", "5,Spade"], ["4,Spade", "4,Square", "4,Heart"],
                         ["3,Heart", "6,Square", "6,Clover", "6,Spade"], ["8,Square", "8,Spade", "8,Heart"],
                         ["7,Square", "9,Heart", "J,Square", "J,Spade", "J,Heart"],
                         ["9,Square", "Q,Spade", "Q,Clover", "Q,Square"], ["3,Heart", "K,Heart"]]},
              {"game": "PresidentGame", "players": ["AI - Nona Martinez", "AI - George Ku", "AI - Violet Whalen"],
               "winners": [{"player": "AI - Violet Whalen", "rank": 1, "round": 6, "last_play": "Q,Square",
                            "grade": "President"},
                           {"player": "AI - George Ku", "rank": 2, "round": 10, "last_play": "A,Spade",
                            "grade": "Neutre"},
                           {"player": "AI - Nona Martinez", "rank": 3, "round": 10, "last_play": "10,Square",
                            "grade": "Troufion"}],
               "plays": [["3,Clover", "3,Spade", "6,Clover", "6,Heart", "8,Heart", "8,Square", "2,Spade", "2,Heart"],
                         ["6,Square", "6,Spade", "7,Clover", "7,Square", "A,Square", "A,Heart"],
                         ["K,Spade", "K,Square", "K,Heart"],
                         ["5,Spade", "5,Heart", "7,Heart", "7,Spade", "2,Square", "2,Clover"],
                         ["4,Heart", "J,Clover", "J,Spade", "J,Square"], ["Q,Square", "Q,Spade", "Q,Heart"],
                         ["8,Spade", "8,Clover"], ["9,Spade", "9,Square"], ["10,Clover", "10,Square"], ["A,Spade"]]}]
             )
    mng.find()
    mng.find_one("players", "AI - Nona Martinez")
    mng.save({"players": "AI - Nona Martinez"}, {"players": "AI - Nona Martinez"})
    mng.delete([{"players": "AI - Nona Martinez"}, {"players": "AI - George Ku"}])
    mng.find()
