import telebot
from moviepy.editor import AudioFileClip
import speech_recognition as sr
from config import TOKEN

bot = telebot.TeleBot(token=TOKEN)


# приветственное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 f'Привет, {message.chat.first_name}! Я бот, который умеет конвертировать голосовые сообщения в текст.\nЧтобы начать, просто перешли мне голосовое сообщение.')


# вывод возможностей бота после нажатия на кнопку "старт"
@bot.message_handler(commands=['help'])
def bot_capabilities(message):
    bot.reply_to(message, 'Я могу конвертировать голосовые сообщения в текст.\nПросто перешли мне голосовое сообщение, которое ты слушать не хочешь!')


# функция, которая будет вызываться при получении голосового сообщения
@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    # проверка на наличие пересланного сообщения
    if message.forward_from:
        bot.reply_to(message, 'Подождите немного, я обрабатываю голосовое сообщение :)')

        file_id = message.voice.file_id
        file = bot.get_file(file_id)
        file_path = file.file_path

        # загрузка голосовой записи с серверов Telegram
        downloaded_file = bot.download_file(file_path)
        with open('audio.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        # преобразование голосовой записи в текст
        audio = AudioFileClip('audio.ogg')
        audio.write_audiofile('audio.wav')
        recognizer = sr.Recognizer()
        with sr.AudioFile('audio.wav') as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ru-RU')

        # ответ на голосовое сообщение текстом
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, 'Пересланных голосовых сообщений не найдено')


if __name__ == '__main__':
    bot.polling(none_stop=True)