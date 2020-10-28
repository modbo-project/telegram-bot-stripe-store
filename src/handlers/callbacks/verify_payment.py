import telegram, logging, random, stripe

from modules.pytg.load import manager

logger = logging.getLogger(__name__)

def verify_payment_callback_handler(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    user_id = query.message.from_user.id

    logger.info("Handling verify payment callback data from {}: {}".format(chat_id, query.data))

    payment_id = int(update.callback_query.data.split(",")[2])

    # logger.warning("Mock payment verification")
    # manager("payments").register_verified_payment(payment_id)

    current_session_state = __update_stripe_session_state(payment_id)

    if not __has_user_completed_payment(payment_id):
        __send_unverified_payment_warning(context.bot, query) 
        return

    __update_message(context.bot, query.message)
    __deliver(context, chat_id, payment_id, current_session_state)

    # __clear_session_entry(payment_id)

def __clear_session_entry(payment_id):
    manager("stripe_store").delete_payment_active_session(payment_id)

def __update_stripe_session_state(payment_id):
    logger.info("Updating stripe session for payment id #{}".format(payment_id))

    session_data = manager("stripe_store").get_payment_active_session(payment_id)

    result = stripe.checkout.Session.retrieve(session_data["session_id"])

    if result["payment_status"] == "paid":
        manager("payments").register_verified_payment(payment_id)

    return result

def __send_unverified_payment_warning(bot, query):
    phrases = manager("text").load_phrases("stripe_store")

    bot.answer_callback_query(
        callback_query_id = query.id,
        show_alert = True,
        text = phrases["payment_unverified"]
    )

def __update_message(bot, message):
    phrases = manager("text").load_phrases("stripe_store")

    bot.edit_message_text(
        chat_id = message.chat_id,
        message_id = message.message_id,
        text = phrases["payment_verified"]
    )

def __has_user_completed_payment(payment_id):
    return manager("payments").verify_payment(payment_id)

def __deliver(context, chat_id, payment_id, stripe_session_state):
    payment_data = manager("payments").get_payment_data(payment_id)

    cart_handler = manager("stripe_store").get_cart_handler(payment_data["category"])
    cart_handler.deliver(context, chat_id, meta = {
        "subscription_meta": stripe_session_state["subscription"]
    })