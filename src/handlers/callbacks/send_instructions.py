import telegram, logging, time, stripe

from modules.pytg.load import manager

logger = logging.getLogger(__name__)

def send_instructions_callback_handler(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = update.callback_query.message.from_user.id

    logger.info("Handling send instructions callback data from {}: {}".format(chat_id, query.data))

    plan = update.callback_query.data.split(",")[2]

    __send_wait_notification(context.bot, chat_id, message_id)

    payment_id = __register_pending_payment(user_id, plan)

    checkout_object = __generate_checkout_object(plan)
    session_id = checkout_object["id"]

    payment_link = manager("stripe").retrieve_checkout_link(session_id)

    manager("stripe_store").register_active_session(payment_id, session_id)

    __send_message(context.bot, chat_id, message_id, plan, payment_id, payment_link)

def __send_wait_notification(bot, chat_id, message_id):
    bot.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text =  manager("text").load_phrases("stripe_store")["payment_loading"],
        parse_mode = telegram.ParseMode.MARKDOWN,
        reply_markup = None
    )

def __send_message(bot, chat_id, message_id, plan, payment_id, payment_link):
    bot.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text = __load_instructions_text(plan),
        reply_markup = __create_reply_markup(payment_id, payment_link),
        parse_mode = telegram.ParseMode.MARKDOWN
    )

def __register_pending_payment(user_identifier, plan):
    payment_id = manager("payments").register_pending_payment(user_identifier, plan)

    return payment_id

def __load_instructions_text(plan):
    return manager("text").load_phrases(plan)["instructions"]

def __create_reply_markup(payment_id, payment_link):
    return manager("menu").create_reply_markup("stripe_store", "subscription", meta = {
        "__PAYMENT_LINK__": payment_link,
        "__PAYMENT_ID__": payment_id 
    })

def __generate_checkout_object(plan):
    plan_settings = manager("config").load_settings(plan, "stripe_item")

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': plan_settings["price_id"],
            'quantity': 1,
        }],
        mode=plan_settings["mode"],
        success_url='https://t.me/FreeMoneySignalsBot',
        cancel_url='https://t.me/FreeMoneySignalsBot',
    )

    return session