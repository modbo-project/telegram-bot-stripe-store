import logging

from modules.pytg.load import manager

logger = logging.getLogger(__name__)

def abort_callback_handler(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    user_id = query.message.from_user.id

    logger.info("Handling callback data from {}: {}".format(chat_id, query.data))

    payment_id = update.callback_query.data.split(",")[2]

    manager("payments").cancel_payment(payment_id)

    __update_message(context.bot, query.message)

def __update_message(bot, message):
    phrases = manager("text").load_phrases("stripe_store")

    bot.edit_message_text(
        chat_id = message.chat_id,
        message_id = message.message_id,
        text = phrases["payment_aborted"],
        reply_markup = None
    )