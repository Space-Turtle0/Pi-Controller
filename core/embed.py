import discord
import random


def randomrgb():
    values = []
    while len(values) < 3:
        values.append(random.randint(0, 255))
    color = discord.Color.from_rgb(values[0], values[1], values[2])
    return color