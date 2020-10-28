import logging

from modules.pytg.Manager import Manager
from modules.pytg.load import manager

from modules.sqlite3.SqliteSession import SqliteSession

class StripeStoreManager(Manager):
    @staticmethod
    def initialize():
        StripeStoreManager.__instance = StripeStoreManager()

        return

    @staticmethod
    def load():
        return StripeStoreManager.__instance

    def __init__(self):
        self.__logger = logging.getLogger(__name__ + " " + str(id(self)))

        self.__cart_handlers = {}

    def connect_to_database(self):
        self.__session : SqliteSession = manager("sqlite3").create_session("stripe_store")

    def register_cart_handler(self, plan_id, handler):
        self.__cart_handlers[plan_id] = handler

    def get_cart_handler(self, plan_id):
        return self.__cart_handlers[plan_id]

    def register_active_session(self, payment_id, session_id):
        self.__session.lock()

        self.__session.insert("ActiveCheckoutSessions", values = {
            "payment_id": payment_id,
            "session_id": session_id
        })
        self.__session.commit()

        self.__session.unlock()

    def delete_payment_active_session(self, payment_id):
        self.__session.lock()

        self.__session.delete("ActiveCheckoutSessions", key = {
            "payment_id": payment_id
        })
        self.__session.commit()

        self.__session.unlock()

    def get_payment_active_session(self, payment_id):
        self.__session.lock()

        result = self.__session.select("ActiveCheckoutSessions", key = {
            "payment_id": payment_id,
        }).fetchone()
        self.__session.commit()

        self.__session.unlock()

        return result