from highrise import BaseBot, User, Position, AnchorPosition
import asyncio
from asyncio import Task
from owner import OWNER_USER



class FollowCommands:

    def __init__(self, bot: BaseBot):
        self.bot = bot

    async def handle_command(self, user: User, message: str) -> None:
        if message.lower().startswith(("follow", "الحق", "!follow")):
            await self.follow(user, message)
            
        elif message.lower().startswith(("stopfollow", "لا تلحق", "!stopfollow")):
            await self.stopfollow(user, message)

    async def follow(self, user: User, message: str) -> None:
        privilege_response = await self.bot.highrise.get_room_privilege(user.id)
        if not (privilege_response.moderator or user.username.lower() in OWNER_USER):
            await self.bot.highrise.send_whisper(user.id, "Vous n'avez pas la permission pour utiliser cette commande.")
            return

        # Check if the user provided a specific username to follow
        target_username = None
        if len(message.split()) > 1:  # If there's more than just the command, we assume there's a username
            target_username = message.split()[1].replace("@", "").lower()  # Extract the username and remove '@'

        async def following_loop(target_user: User) -> None:
            while True:
                # Gets the target user's position
                room_users = (await self.bot.highrise.get_room_users()).content
                user_position = None
                for room_user, position in room_users:
                    if room_user.id == target_user.id:
                        user_position = position
                        break

                if user_position is None:
                    await self.bot.highrise.chat(f"User {target_user.username} is no longer in the room.")
                    break  # Stop following if the user leaves the room

                if type(user_position) != AnchorPosition:
                    await self.bot.highrise.walk_to(Position(user_position.x + 1, user_position.y, user_position.z))
                await asyncio.sleep(0.5)

        # Search for the target user in the room if a username was provided
        target_user = user
        if target_username:
            room_users = (await self.bot.highrise.get_room_users()).content
            for room_user, position in room_users:
                if room_user.username.lower() == target_username:
                    target_user = room_user
                    break

            if target_user.username.lower() != target_username:
                await self.bot.highrise.send_whisper(user.id, f"User @{target_username} not found in the room.")
                return

        # Ensure that there isn't an existing follow loop running
        taskgroup = self.bot.highrise.tg
        task_list = list(taskgroup._tasks)
        for task in task_list:
            if task.get_name() == "following_loop":
                await self.bot.highrise.send_whisper(user.id, "Already following someone.")
                return
        
        # Create a new follow task
        taskgroup.create_task(coro=following_loop(target_user))
        task_list = list(taskgroup._tasks)
        for task in task_list:
            if task.get_coro().__name__ == "following_loop":
                task.set_name("following_loop")
        await self.bot.highrise.chat(f"Take the lead @{target_user.username}")

    async def stopfollow(self, user: User, message: str) -> None:
        privilege_response = await self.bot.highrise.get_room_privilege(user.id)
        if not (privilege_response.moderator or user.username.lower() in OWNER_USER):
            await self.bot.highrise.send_whisper(user.id, "Vous n'avez pas la permission pour utiliser cette commande.")
            return

        taskgroup = self.bot.highrise.tg
        task_list = list(taskgroup._tasks)
        for task in task_list:
            if task.get_name() == "following_loop":
                task.cancel()
                await self.bot.highrise.chat(f"Alright imma stay here then @{user.username}")
                return
        await self.bot.highrise.send_whisper(user.id, "Not following anyone")

