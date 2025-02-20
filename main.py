import asyncio
import logging
import requests
import random
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder

# Vervang deze waarden met jouw nieuwe token en chat-ID
TOKEN = "7181562151:AAH6ayA93Q5o5KykOOEQja_aALavn8fWnCg"
CHAT_ID = "5748009663"

# GitHub repo info
REPO_OWNER = "Pvpv48"
REPO_NAME = "Pvpv48"
IMAGE_FOLDER = "images"  # Zorg dat dit de juiste map is in je repo
TEXT_FILE = "messages.txt"

# URLs
TEXT_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{TEXT_FILE}"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{IMAGE_FOLDER}"

# Logging instellen
logging.basicConfig(level=logging.INFO)

async def send_photo(bot: Bot):
    while True:
        try:
            # Stap 1: Haal de lijst met bestanden op uit de GitHub map
            response = requests.get(GITHUB_API_URL)
            if response.status_code == 200:
                files = response.json()
                image_files = [file["download_url"] for file in files if file["name"].lower().endswith((".jpg", ".png"))]

                if not image_files:
                    logging.error("Geen afbeeldingen gevonden in de GitHub-repository.")
                    continue

                # Kies een willekeurige afbeelding
                image_url = random.choice(image_files)

                # Download de afbeelding
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open("temp.jpg", "wb") as file:
                        file.write(image_response.content)

                else:
                    logging.error("Kon de afbeelding niet downloaden.")
                    continue
            else:
                logging.error("Kon de lijst met bestanden niet ophalen.")
                continue

            # Stap 2: Haal een willekeurige regel uit het tekstbestand op
            text_response = requests.get(TEXT_URL)
            if text_response.status_code == 200:
                lines = text_response.text.strip().split("\n")
                message = random.choice(lines) if lines else "Geen tekst gevonden."

            else:
                logging.error("Kon het bericht niet ophalen.")
                message = "Geen bericht beschikbaar."

            # Stap 3: Stuur de foto en het bericht naar Telegram
            with open("temp.jpg", "rb") as photo:
                await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=message)
            logging.info("Foto en bericht verzonden!")

        except Exception as e:
            logging.error(f"Fout bij verzenden: {e}")

        # Wacht 3600 seconden (1 uur) voor de volgende update
        await asyncio.sleep(3600)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    bot = app.bot  # Krijg de bot-instantie
    asyncio.create_task(send_photo(bot))  # Start de herhalende taak
    print("Bot is gestart...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
