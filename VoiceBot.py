import os
import tempfile
import logging
from pydub import AudioSegment
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import speech_recognition as sr
import io

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Привет! Отправь голосовое сообщение, чтобы я его распознал :)')


def voice(update: Update, context: CallbackContext) -> None:
    """Recognition of Russian speech in a voice message on telegram"""
    try:
        # Get voice message file
        voice_msg = update.message.voice
        logger.info(f"New voice message from chat_id {update.effective_chat.id}")

        # Create temporary directory to store files
        tempdir = tempfile.TemporaryDirectory()

        # Download file from Telegram and save to BytesIO object
        voice_file = context.bot.get_file(voice_msg.file_id)
        voice_data = io.BytesIO()
        voice_file.download(out=voice_data)

        # Save file to disk for debugging purposes
        with open(os.path.join(tempdir.name, 'test.ogg'), 'wb') as f:
            f.write(voice_data.getbuffer())

        # Use pydub to convert audio
        ogg_audio = AudioSegment.from_file(os.path.join(tempdir.name, 'test.ogg'), format="ogg")
        ogg_audio.export(os.path.join(tempdir.name, 'test.wav'), format="wav")

        # Create SpeechRecognition object
        r = sr.Recognizer()

        # Test if file can be recognized by speech_recognition with Google Speech Recognition
        with sr.AudioFile(os.path.join(tempdir.name, 'test.wav')) as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source, duration=5)
            r.recognize_google(audio_data, language="ru-RU")

        # Recognition with Google Speech Recognition
        with sr.AudioFile(os.path.join(tempdir.name, 'test.wav')) as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source, duration=5)
            recognized_text = r.recognize_google(audio_data, language="ru-RU")

        # Send recognition result
        text = f"<strong>Распознанный текст:</strong> \n{recognized_text}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error occurred during audio transcription: {e}")
        update.message.reply_text("Извините, произошла ошибка. Попробуйте еще раз.")

    finally:
        tempdir.cleanup()


def main() -> None:
    """Start the bot."""
    # Read bot token from env variable or file
    BOT_TOKEN = os.getenv("BOT_TOKEN") or open('bot_token.txt').read().strip()

    updater = Updater(BOT_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice))

    # Start the Bot
    logger.info("Starting bot polling...")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
