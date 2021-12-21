# -*- coding: utf-8 -*-
# !/usr/bin/python3

# python3 -m pip install pyTelegramBotAPI python-dotenv picamera --no-cache-dir

import os
import json
import telebot
import requests
import subprocess
from picamera import PiCamera


def get911(key):
    f = open('/home/pi/.911')
    data = json.load(f)
    f.close()
    return data[key]


TRANSMISSION_USER = get911('TRANSMISSION_USER')
TRANSMISSION_PASS = get911('TRANSMISSION_PASS')
TRANSMISSION_PORT = get911('TRANSMISSION_PORT')
TELEGRAM_TOKEN = get911('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)
camera = PiCamera()


# Get Hardware / Software Information
def getInfo():
    r = requests.get('http://0.0.0.0:8888/json')
    r = json.loads(r.text)

    infos = ""
    if r["Uptime"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Uptime" + "\n"
        infos += "Boot Time: " + str(r["Uptime"]["Boot_Time"]) + "\n"
        infos += "Uptime: " + str(r["Uptime"]["Uptime"]) + "\n"

    if r["Temperature"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Temperature: " + \
            str(r["Temperature"]["Temperature"]) + " ºC" + "\n"

    if r["AmbientHumidityTemperature"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Ambient" + "\n"
        infos += "Date: " + str(r["AmbientHumidityTemperature"]["Date"]) + "\n"
        infos += "Humidity: " + \
            str(r["AmbientHumidityTemperature"]["Humidity"]) + " %" + "\n"
        infos += "Temperature: " + \
            str(r["AmbientHumidityTemperature"]["Temperature"]) + " ºC" + "\n"

    if r["CPU"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "CPU" + "\n"
        infos += "Percentage: " + str(r["CPU"]["Percentage"]) + " %" + "\n"
        infos += "PIDs: " + str(r["CPU"]["PIDs"]) + "\n"

    if r["Memory"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Memory" + "\n"
        infos += "Percentage: " + str(r["Memory"]["Percentage"]) + " %" + "\n"

    if r["Disks"]["SDCard"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "SDCard" + "\n"
        infos += "Percentage: " + \
            str(r["Disks"]["SDCard"]["Percentage"]) + " %" + "\n"

    if r["Disks"]["918"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "918" + "\n"
        infos += "Percentage: " + \
            str(r["Disks"]["918"]["Percentage"]) + " %" + "\n"

    if r["Network"]["Info"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Hostname: " + str(r["Network"]["Info"]["Hostname"]) + "\n"

    if r["Network"]["Wired"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Wired" + "\n"
        infos += "Received: " + str(r["Network"]["Wired"]["Received"]) + "\n"
        infos += "Sent: " + str(r["Network"]["Wired"]["Sent"]) + "\n"

    if r["Network"]["Wifi"]["hasInfo"] == "Yes":
        infos += "\n" + "-----------------------------------------" + "\n"
        infos += "Wifi" + "\n"
        infos += "Received: " + str(r["Network"]["Wifi"]["Received"]) + "\n"
        infos += "Sent: " + str(r["Network"]["Wifi"]["Sent"]) + "\n"

    return infos


def getPic():
    imgFilePath = "/home/pi/TelegramBot/pic.jpg"
    camera.rotation = 180
    camera.capture(imgFilePath)
    return imgFilePath


@bot.message_handler(commands=['help'])
def send_help(message):
    response = "Available Cmds" + "\n\n"
    response += "/stats - Get HW Info" + "\n"
    response += "/pic - Get a Pic" + "\n"
    response += "/tlist - Torrent List" + "\n"
    response += "/tstart - Torrent Start All" + "\n"
    response += "/tstop - Torrent Stop All" + "\n"
    bot.reply_to(message, response)


@bot.message_handler(commands=['stats'])
def send_stats(message):
    response = getInfo()
    bot.reply_to(message, response)


@bot.message_handler(commands=['pic'])
def send_pic(message):
    imgFilePath = getPic()
    photo = open(imgFilePath, 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()


@bot.message_handler(commands=['tlist'])
def send_torrent_list(message):

    response = subprocess.getoutput("transmission-remote 127.0.0.1:" + TRANSMISSION_PORT +
                                    " --auth=" + TRANSMISSION_USER + ":" + TRANSMISSION_PASS + " --list")

    if len(response.split("\n")) >= 3:
        cmd, torrents = [], []
        for entry in response.split("\n")[:-1]:
            for section in entry.replace("  ", "|").split("|"):
                if section:
                    cmd.append(section.replace(" ", " ").lstrip().rstrip())
        for i in range(0, len(cmd), 9):
            torrents.append(cmd[i:i + 9])

        response = ""
        for i in range(1, len(torrents), 1):
            for j in range(0, len(torrents[0]), 1):
                response += torrents[0][j] + " - " + torrents[i][j] + "\n"
            response += "\n"
    else:
        response = "No Torrents"

    bot.reply_to(message, response)


@bot.message_handler(commands=['tstart'])
def send_torrent_start(message):
    response = subprocess.getoutput("transmission-remote 127.0.0.1:" + TRANSMISSION_PORT +
                                    " --auth=" + TRANSMISSION_USER + ":" + TRANSMISSION_PASS + " --torrent all --start")
    bot.reply_to(message, response)


@bot.message_handler(commands=['tstop'])
def send_torrent_stop(message):
    response = subprocess.getoutput("transmission-remote 127.0.0.1:" + TRANSMISSION_PORT +
                                    " --auth=" + TRANSMISSION_USER + ":" + TRANSMISSION_PASS + " --torrent all --stop")
    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    response = message.text
    bot.reply_to(message, response)


if __name__ == "__main__":
    bot.infinity_polling()
