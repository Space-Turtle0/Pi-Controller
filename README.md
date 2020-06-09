# Pi-Controller
Personal server controller hosted on a Raspberry Pi.
**In-Development**

Feel free to modify or use to host your own servers if you like.

## Current Features:
- Automatic Updates (Finished)
  - Bot will receive automatic updates through Github Releases. Toggleable.
- JSON driven server control (In-Progress)
  - Hopefully allows for easy flexibility with supported servers down the line.
- Admin System (In-Progress)
  - Only those granted permission can send sensitive requests to the bot.
- System Monitor (Finished)
  - Will report updated values every minute regarding the CPU usage, RAM usage, Disk space, and the boot time.
- Console Channel (In-Progress)
  - Set a channel in your discord server as the console, for ease of sending commands to the launched server.
  - Will only listen to bot admins.

## Planned Features/To-Do:
- General:
    - ~~Switch from `requests` to `aiohttp`.~~ (Done)
    - ~~Make getting server directories into a function.~~ (Done)
    - Error handling/more forgiving commands.
        - Shutdown server before closing bot with shutdown.
        - If no server is running, stop certain commands from attempting execution.
    - File request system (In-Progress)
        - Request server directories to be sent to you in DMs
        - Can be sent back to replace data that is there
- Contributors System:
    - Allow contributors to easily look up their own contributions
    - Link Discord Users to Github Profiles
    - Add a bio option for contributors to use.
- Admin System:
    - Extend to allow server specific admins/moderators, able to control aspects relating to their server.
- Console Channel:
    - Extend to allow multiple console channels running at once.
    - Send messages whenever a JSON command is run or a server is started/stopped.
- JSON Server Control:
    - Rewrite JSON command parsing to accept arguments from Discord.
        - Split each JSON Command Argument into its' own function. Provide cleaner code.
    - Experiment with dynamically adding bot commands referencing the JSON Command.
        - Requires ability to programmatically add commands. Is this even possible?
            - it is possible, Metaclasses.
    - Timer JSON Command Argument
        - Wait a specified amount of time before continuing.
    - File->Download JSON Command Argument
        - Choose to download from the given link or from a message attachment.
    - File->Delete JSON Command Argument
        - Delete the given file if it exists.
    - File->Upload JSON Command Argument
        - Upload the given file to Discord if it exists.
        - Send file to either ctx, DM's, or a specific channel.
    - File->Append JSON Command Argument
        - Append data to the end of a file.
    - Directory->Create JSON Command Argument
        - Create the specified directory.
    - Directory->Delete JSON Command Argument
        - Delete the specified directory if it exists.
    - Directory->Upload JSON Command Argument
        - Upload the compressed directory to Discord if it exists.
        - Send file to either ctx, DM's or a specific channel.
    - JSON->Modify JSON Command Argument
        - Change a specific value of a server's JSON file.
        - This provides flexibility to let files modify themselves.
    

## JSON Documentation
- Coming soon.