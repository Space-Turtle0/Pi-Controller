import discord
import random


def randomrgb() -> discord.Color:
    """Get a random Discord Color Object"""
    values = []
    while len(values) < 3:
        values.append(random.randint(0, 255))
    color = discord.Color.from_rgb(values[0], values[1], values[2])
    return color


def hex_to_rgb(code) -> discord.Color:  # used from https://gist.github.com/matthewkremer/3295567#gistcomment-3098081
    """Converts hex code to a Discord Color Object"""
    code = code.lstrip('#')
    codelen = len(code)
    r, g, b = tuple(int(code[i:i + codelen // 3], 16) for i in range(0, codelen, codelen // 3))
    color = discord.Color.from_rgb(r, g, b)
    return color


def rgb_to_hex(rgb: tuple) -> str:
    """Converts rgb tuple to hex code."""
    r, g, b = rgb
    code = "#{0:02x}{1:02x}{2:02x}".format(r, g, b)
    return code
