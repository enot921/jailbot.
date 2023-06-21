import subprocess


def start_bot():
    subprocess.call(["python", "jailbot.py"])

def run_bot():
    while True:
        try:
            start_bot()
        except Exception as e:
            print('Error running the bot:', str(e))
            continue


# Вызов функции для запуска бота
run_bot()