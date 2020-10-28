import telegram, logging

from modules.pytg.load import manager

from telegram.ext import CallbackQueryHandler

from .handlers.callbacks.send_instructions import send_instructions_callback_handler
from .handlers.callbacks.verify_payment import verify_payment_callback_handler
from .handlers.callbacks.abort import abort_callback_handler

from .StripeStoreManager import StripeStoreManager

def load_callback_handlers(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(send_instructions_callback_handler, pattern="stripe_store,send_instructions"))
    dispatcher.add_handler(CallbackQueryHandler(verify_payment_callback_handler, pattern="stripe_store,verify_payment"))
    dispatcher.add_handler(CallbackQueryHandler(abort_callback_handler, pattern="stripe_store,abort"))

def initialize():
    StripeStoreManager.initialize()

def connect():
    load_callback_handlers(manager("bot").updater.dispatcher)

    load_manager().connect_to_database()

def load_manager():
    return StripeStoreManager.load()

def depends_on():
    return ["bot"]