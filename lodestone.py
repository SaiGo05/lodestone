import urllib
import re
import logging
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

ffxivLodeUrl = "http://na.finalfantasyxiv.com/lodestone/character/16386483/"

soup = BeautifulSoup(urlopen(ffxivLodeUrl), "html5lib")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

charaOwnedMounts = []
ffxivMissingMounts = []

# Array and code for a bunch of Character info
charaInfo = []
for charaSubInfo in soup.find_all("p", class_="character-block__name"):
    charaInfo.append(charaSubInfo.text)
# Array and code for level related info
charaLvAll = []
charaLvRaw = soup.find_all(class_="character__level__list")
for charaLvTmp1 in charaLvRaw:
    charaLvTmp2 = charaLvTmp1.find_all("li")
    for charaLvTmp3 in charaLvTmp2:
        charaLvAll.append(charaLvTmp3.text)
logging.info("Job levels parsed")
# Importing mount data
ffxivMountInfo = []
with open("mounts.txt") as rawMountData:
    for eachMount in rawMountData:
        ffxivMountInfo.append(eachMount.rstrip('\n'))
logging.info("Mount data imported")

# --->Character Name
def charaName():
    return soup.find("p", "frame__chara__name").text


# --->Character Birthday
def charaBday():
    return soup.find("p", "character-block__birth").text


# --->Character Title
def charaTitle():
    return soup.find("p", "frame__chara__title").text


# --->Character Server
def charaServer():
    return soup.find("p", "frame__chara__world").text


# --->Character Race and Tribe
def charaRace():
    charaRaceTemp = charaInfo[0]
    if charaRaceTemp[:1] is "A":
        if len(charaRaceTemp) is 13:
            return "Au Ra, Raen"
        else:
            return "Au Ra, Xaela"
    elif charaRaceTemp[:1] is "E":
        if len(charaRaceTemp) is 18:
            return "Elezen, Wildwood"
        else:
            return "Elezen, Duskwight"
    elif charaRaceTemp[:1] is "H":
        if len(charaRaceTemp) is 18:
            return "Hyur, Highlander"
        else:
            return "Hyur, Midlander"
    elif charaRaceTemp[:1] is "L":
        if len(charaRaceTemp) is 22:
            return "Lalafell, Plainsfolk"
        else:
            return "Lalafell, Dunesfolk"
    elif charaRaceTemp[:1] is "M":
        if len(charaRaceTemp) is 29:
            return "Miqo'te, Keeper of the Moon"
        else:
            return "Miqo'te, Seeker of the Sun"
    elif charaRaceTemp[:1] is "R":
        if len(charaRaceTemp) is 22:
            return "Roegadyn, Hellsguard"
        else:
            return "Roegadyn, Sea Wolf"
    else:
        return "Error"


# --->Character Gender
def charaGender():
    charaRaceTemp = charaInfo[0]
    return charaRaceTemp[-1]


# --->Character Free Company
def charaFC():
    charaFCTemp = soup.find(class_="character__freecompany__name")
    if len(charaFCTemp.find("h4").text) > 0:
        return charaFCTemp.find("h4").text
    else:
        return "None"


# --->Character Guardian
def charaGuardian():
    return charaInfo[1]


# --->Character City-State
def charaCity():
    return charaInfo[2]


# --->Character Grand Company
def charaGC():
    charaGCTemp = charaInfo[3]
    if charaGCTemp[:1] is "M":
        return "Maelstrom, " + charaGCTemp[12:]
    elif charaGCTemp[:1] is "O":
        return "Order of the Twin Adder, " + charaGCTemp[26:]
    elif charaGCTemp[:1] is "I":
        return "Immortal Flames, " + charaGCTemp[18:]
    else:
        return "None"


# --->Character Mounts
# Code is uhh... functional.
def charaMounts():

    divCharaMounts = (soup.find("div", "character__mounts"))
    divCharaOwnedMounts = (divCharaMounts.find_all("div", "character__item_icon js__tooltip"))
    for eachMount in divCharaOwnedMounts:
        tempMountVar = eachMount["data-tooltip"]
        charaOwnedMounts.append(tempMountVar)
        charaOwnedMounts.sort()
    logging.info("Character mount data parsed")
    return charaOwnedMounts


# ---Character Minions
# Same as above, changed params cause of the similar nature of the two
def charaMinions():
    charaOwnedMinions = []
    divCharaMinion = (soup.find("div", "character__minion"))
    divCharaOwnedMinions = (divCharaMinion.find_all("div", "character__item_icon js__tooltip"))
    for eachMinion in divCharaOwnedMinions:
        tempMinionVar = eachMinion["data-tooltip"]
        charaOwnedMinions.append(tempMinionVar)
        charaOwnedMinions.sort()
    logging.info("Character minion data parsed")
    return charaOwnedMinions


# --->Character Job levels
# -->Tank Job levels
# PLD, WAR, DRK
def charaTankLv():
    return charaLvAll[0:3]


# -->Healer Job levels
# WHM, SCH, AST
def charaHealLv():
    return charaLvAll[3:6]


# --->DPS Job levels
# MNK, DRG, NIN, SAM, BRD, MCH, BLM, SMN, RDM
def charaDPSLv():
    return charaLvAll[6:15]


# --->Crafter Job Levels
# CRP, BSM, ARM, GSM, LTW, WVR, ALC, CUL
def charaCraftLv():
    return charaLvAll[15:23]


# --->Gathering Job Levels
# MIN, BTN, FSH
def charaGatherLv():
    return charaLvAll[23:26]


# --->Missing mounts
# Finally managed to get it working after putting it off for so long
def charaMissingMounts():
    charaMounts()
    for number in ffxivMountInfo:
        formatedMounts = re.split('%', number)
        if formatedMounts[0] in charaOwnedMounts:
            formatedMounts.pop()
            formatedMounts.pop()
        ffxivMissingMounts.append(formatedMounts)
    logging.info("Obtained missing mount data")
    return list(filter(None, ffxivMissingMounts))


def mountImage():
    start_time = time.time()
    charaMountData = charaMissingMounts()
    imgHeight = len(charaMountData) * 28 + 110
    imgMissingMounts = Image.new('RGB', (1280, imgHeight), (255, 255, 255, 0))
    fntTitle = ImageFont.truetype('title.ttf', 40)
    fntName = ImageFont.truetype('reg.ttf', 22)
    fntExecTime = ImageFont.truetype('time.ttf', 15)
    footfnt = ImageFont.truetype('footer.ttf',26)
    d = ImageDraw.Draw(imgMissingMounts)
    d.text((230,0), charaName() + "'s Missing Mounts", font=fntTitle, fill=(80, 99, 128 , 255))
    i = 1
    for eachMount in charaMountData:
        n = 30 + i*28
        d.text((5,n),"> " + eachMount[0] + "   -   " + eachMount[-1], font=fntName, fill=(000))
        i += 1
    exeTime = str(time.time() - start_time)
    exeTime = exeTime[:8]
    d.text((5,34),"exec: " + exeTime + "s", font=fntExecTime, fill=(000))
    imgMissingMounts.save("mounts.jpg")
    return ()

mountImage()

