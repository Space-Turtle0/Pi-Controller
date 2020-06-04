import aiofiles
import os
import sys
import json


def getbotdir() -> str:
    """Returns the root directory of the bot as a string."""
    path = os.path.realpath(os.path.dirname(sys.argv[0]))
    return path


async def makefile(filename: str, data: any):
    """Make a file with the given data written. Non-Blocking, requires await."""
    root = getbotdir()
    path = os.path.join(root, filename)
    async with aiofiles.open(path, mode="w+") as file:
        await file.write(data)


async def loadjson(filename: str):
    """Load json file, return the data. Non-Blocking, requires await."""
    async with aiofiles.open(filename, "r") as file:
        content = await file.read()
    data = json.loads(content)
    return data


async def dumpjson(data: dict, filename: str):
    """Save data dictionary to the given file. Non-Blocking, requires await."""
    async with aiofiles.open(filename, "w+") as file:
        content = json.dumps(data, indent=4, sort_keys=True)
        await file.write(content)
