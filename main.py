from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
from groq import Groq   

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Init Groq client
client = Groq(api_key=GROQ_API_KEY)

# Model
MODEL_NAME = "llama3-8b-8192"

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)


class Reference:
    """
    A class to store the previous assistant response.
    """
    def __init__(self) -> None:
        self.response = ""   


reference = Reference()


def clear_paste():
    """
    Clear the previous conversation and context.
    """
    reference.response = ""


@dispatcher.message_handler(commands=['clear'])
async def clear(message: types.Message):
    clear_paste()
    await message.reply("I've cleared the past conversation and context.")


@dispatcher.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply("Hi 👋\nI am Tele Bot!\nCreated by Anoop Krishna.\nHow can I assist you?")


@dispatcher.message_handler(commands=['help'])
async def helper(message: types.Message):
    help_command = """
Hi There, I'm Groq Telegram bot created by Anoop Krishna!  
Please follow these commands:
- /start → Start the conversation
- /clear → Clear the past conversation and context
- /help → Show this help menu
    """
    await message.reply(help_command)


@dispatcher.message_handler()
async def groq_handler(message: types.Message):
    """
    Process user's input and generate a response using the Groq API.
    """
    print(f">>> USER: {message.text}")

    # Call Groq API
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": reference.response},  # last assistant reply
            {"role": "user", "content": message.text}              # new user query
        ]
    )

    # Extract reply
    reply_text = response.choices[0].message.content

    # Save context
    reference.response = reply_text

    print(f">>> Groq: {reply_text}")

    await bot.send_message(chat_id=message.chat.id, text=reply_text)


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
