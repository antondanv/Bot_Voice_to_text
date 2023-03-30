import os
import tempfile
import logging
import telegram
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import speech_recognition as sr
import io

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: telegram.ext.CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Отправь голосовое сообщение, чтобы я его распознал :)')


def voice(update: Update, context: telegram.ext.CallbackContext) -> None:
    """Recognition of Russian speech in a voice message on telegram"""

    try:
        # Get voice message file
        voice_msg = update.message.voice
        logger.info(f"New voice message from chat_id {update.effective_chat.id}")

        # Create temporary directory to store files
        with tempfile.TemporaryDirectory() as tempdir:

            # Download file from Telegram and save as OGG file
            voice_file = context.bot.get_file(voice_msg.file_id)
            voice_data = io.BytesIO()
            voice_file.download(out=voice_data)
            with open(os.path.join(tempdir, 'test.ogg'), 'wb') as f:
                f.write(voice_data.getbuffer())

            # Load OGG file into AudioFile object
            voice_data.seek(0)
            audio = sr.AudioFile(voice_data)

            # Test if file can be recognized by speech_recognition with Google Speech Recognition
            with audio as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = r.record(source, duration=5)
                r.recognize_google(audio_data, language="ru-RU")

            # Recognition with Google Speech Recognition
            with audio as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = r.record(source, duration=5)
                recognized_text = r.recognize_google(audio_data, language="ru-RU")

        # Send recognition result
        text = f"<strong>Распознанный текст:</strong> \n{recognized_text}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error occurred during audio transcription: {e}")
        update.message.reply_text("Извините, произошла ошибка. Попробуйте еще раз.")


def main() -> None:
    """Start the bot."""
    # Read bot token from env variable or file
    BOT_TOKEN = os.environ.get("BOT_TOKEN") or open('bot_token.txt').read().strip()

    updater = Updater(BOT_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice))

    # Start the Bot
    logger.info("Starting bot polling...")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Create SpeechRecognition object
    r = sr.Recognizer()

    # Start the bot
    main()
