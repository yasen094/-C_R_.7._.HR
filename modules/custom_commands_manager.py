"""
مدير الأوامر المخصصة - معزول عن النظام الأساسي
"""
import json
import os
from datetime import datetime

class CustomCommandsManager:
    def __init__(self):
        self.commands_file = "custom_commands_config.py"
        self.commands_data = {}
        self.load_commands()
        print("🎛️ مدير الأوامر المخصصة جاهز")

    def load_commands(self):
        """تحميل الأوامر المخصصة من ملف Python"""
        try:
            if os.path.exists(self.commands_file):
                # قراءة الملف كنص
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # استخراج البيانات من المحتوى
                if 'CUSTOM_COMMANDS_DATA' in content:
                    import ast
                    start = content.find('CUSTOM_COMMANDS_DATA = ')
                    if start != -1:
                        # استخراج البيانات
                        data_start = content.find('{', start)
                        brace_count = 0
                        data_end = data_start

                        for i, char in enumerate(content[data_start:], data_start):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    data_end = i + 1
                                    break

                        data_str = content[data_start:data_end]
                        self.commands_data = ast.literal_eval(data_str)
                    else:
                        self._create_default_data()
                else:
                    self._create_default_data()
            else:
                self._create_default_data()
                self.save_commands()
        except Exception as e:
            print(f"❌ خطأ في تحميل الأوامر المخصصة: {e}")
            self._create_default_data()

    def _create_default_data(self):
        """إنشاء البيانات الافتراضية"""
        self.commands_data = {
            "navigation_commands": [],
            "dance_commands": [],
            "message_commands": [],
            "teleport_commands": [],
            "settings": {
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

    def save_commands(self):
        """حفظ الأوامر المخصصة كملف Python"""
        try:
            # تحويل البيانات إلى نص Python صحيح
            import pprint
            data_str = pprint.pformat(self.commands_data, indent=4, width=80)

            content = f'''"""
ملف الأوامر المخصصة - يتم إنشاؤه تلقائياً بواسطة مصنع الأوامر
تم آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

CUSTOM_COMMANDS_DATA = {data_str}

def get_navigation_commands():
    """الحصول على أوامر التنقل"""
    return CUSTOM_COMMANDS_DATA.get("navigation_commands", [])

def get_all_custom_commands():
    """الحصول على جميع الأوامر المخصصة"""
    return CUSTOM_COMMANDS_DATA

def is_custom_command(command_text):
    """فحص إذا كان النص أمر مخصص"""
    nav_commands = get_navigation_commands()
    for cmd in nav_commands:
        if cmd.get("enabled", True) and cmd.get("command", "").lower() == command_text.lower():
            return True, cmd
    return False, None
'''

            with open(self.commands_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ تم حفظ {len(self.commands_data.get('navigation_commands', []))} أمر مخصص")
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الأوامر المخصصة: {e}")
            return False

    def add_navigation_command(self, command_word, coordinates, response_message, permissions="everyone"):
        """إضافة أمر تنقل مخصص"""
        try:
            new_command = {
                "id": len(self.commands_data["navigation_commands"]) + 1,
                "command": command_word.strip(),
                "coordinates": {
                    "x": float(coordinates.get("x", 0)),
                    "y": float(coordinates.get("y", 0)),
                    "z": float(coordinates.get("z", 0))
                },
                "message": response_message.strip(),
                "permissions": permissions,
                "created_at": datetime.now().isoformat(),
                "enabled": True
            }

            # التحقق من عدم تكرار الأمر
            for cmd in self.commands_data["navigation_commands"]:
                if cmd["command"].lower() == command_word.lower():
                    return False, "الأمر موجود مسبقاً"

            self.commands_data["navigation_commands"].append(new_command)

            if self.save_commands():
                return True, f"تم إضافة أمر التنقل '{command_word}' بنجاح"
            else:
                return False, "فشل في حفظ الأمر"

        except Exception as e:
            return False, f"خطأ في إضافة الأمر: {str(e)}"

    def add_dance_command(self, command_word, emote_name, response_message, permissions="everyone"):
        """إضافة أمر رقصة مخصص"""
        try:
            new_command = {
                "id": len(self.commands_data["dance_commands"]) + 1,
                "command": command_word.strip(),
                "emote": emote_name.strip(),
                "message": response_message.strip(),
                "permissions": permissions,
                "created_at": datetime.now().isoformat(),
                "enabled": True
            }

            # التحقق من عدم تكرار الأمر
            for cmd in self.commands_data["dance_commands"]:
                if cmd["command"].lower() == command_word.lower():
                    return False, "الأمر موجود مسبقاً"

            # التحقق من عدم تكرار الأمر في أوامر التنقل أيضاً
            for cmd in self.commands_data["navigation_commands"]:
                if cmd["command"].lower() == command_word.lower():
                    return False, "الأمر موجود مسبقاً في أوامر التنقل"

            self.commands_data["dance_commands"].append(new_command)

            if self.save_commands():
                return True, f"تم إضافة أمر الرقصة '{command_word}' بنجاح"
            else:
                return False, "فشل في حفظ الأمر"

        except Exception as e:
            return False, f"خطأ في إضافة أمر الرقصة: {str(e)}"

    def get_navigation_commands(self):
        """الحصول على جميع أوامر التنقل"""
        return self.commands_data.get("navigation_commands", [])

    def delete_navigation_command(self, command_id):
        """حذف أمر تنقل"""
        try:
            commands = self.commands_data["navigation_commands"]
            self.commands_data["navigation_commands"] = [
                cmd for cmd in commands if cmd.get("id") != command_id
            ]

            if self.save_commands():
                return True, "تم حذف الأمر بنجاح"
            else:
                return False, "فشل في حفظ التغييرات"

        except Exception as e:
            return False, f"خطأ في حذف الأمر: {str(e)}"

    def delete_dance_command(self, command_id):
        """حذف أمر رقصة"""
        try:
            commands = self.commands_data["dance_commands"]
            self.commands_data["dance_commands"] = [
                cmd for cmd in commands if cmd.get("id") != command_id
            ]

            if self.save_commands():
                return True, "تم حذف أمر الرقصة بنجاح"
            else:
                return False, "فشل في حفظ التغييرات"

        except Exception as e:
            return False, f"خطأ في حذف أمر الرقصة: {str(e)}"

    def delete_command(self, command_id, command_type="navigation"):
        """حذف أمر حسب النوع"""
        if command_type == "dance":
            return self.delete_dance_command(command_id)
        else:
            return self.delete_navigation_command(command_id)

    def toggle_command(self, command_id, command_type="navigation"):
        """تفعيل/إيقاف أمر"""
        try:
            commands_list = self.commands_data.get(f"{command_type}_commands", [])

            for cmd in commands_list:
                if cmd.get("id") == command_id:
                    cmd["enabled"] = not cmd.get("enabled", True)
                    break

            if self.save_commands():
                return True, "تم تغيير حالة الأمر"
            else:
                return False, "فشل في حفظ التغييرات"

        except Exception as e:
            return False, f"خطأ في تغيير حالة الأمر: {str(e)}"

    async def handle_custom_command(self, user, message, bot):
        """معالجة الأوامر المخصصة"""
        try:
            if not self.commands_data.get("settings", {}).get("enabled", True):
                return None

            # فحص أوامر التنقل
            for cmd in self.commands_data.get("navigation_commands", []):
                if not cmd.get("enabled", True):
                    continue

                if message.lower() == cmd.get("command", "").lower():
                    # تنفيذ أمر التنقل
                    from highrise import Position
                    coords = cmd.get("coordinates", {})
                    position = Position(
                        x=coords.get("x", 0),
                        y=coords.get("y", 0),
                        z=coords.get("z", 0)
                    )

                    await bot.highrise.teleport(user.id, position)
                    return cmd.get("message", f"تم النقل إلى {cmd.get('command')}")

            # فحص أوامر الرقص المخصصة
            dance_commands = self.commands_data.get("dance_commands", [])
            for cmd in dance_commands:
                if cmd.get("enabled", True) and cmd.get("command", "").lower() == message.lower():
                    emote_name = cmd.get("emote", "")
                    print(f"🎭 تنفيذ أمر رقص مخصص: {message} -> {emote_name}")

                    try:
                        if cmd.get("is_auto_dance", False) or cmd.get("auto_repeat", False):
                            # رقصة تلقائية مستمرة
                            print(f"🔄 بدء رقصة تلقائية: {emote_name}")

                            # إيقاف الرقصة الحالية إن وجدت
                            if user.id in bot.auto_emotes:
                                bot.auto_emotes[user.id]["task"].cancel()

                            # بدء الرقصة التلقائية
                            import asyncio
                            task = asyncio.create_task(bot.repeat_emote_for_user(user.id, emote_name))
                            bot.auto_emotes[user.id] = {"emote": emote_name, "task": task}

                            return f"🔄 بدأت الرقصة التلقائية: {cmd.get('command')} - {emote_name}\n✅ {cmd.get('message', 'ستتكرر تلقائياً')}"
                        else:
                            # رقصة عادية
                            await bot.highrise.send_emote(emote_name, user.id)
                            print(f"✅ تم إرسال رقصة: {emote_name}")
                            return f"💃 {cmd.get('command')} - {cmd.get('message', emote_name)}"

                    except Exception as emote_error:
                        print(f"❌ فشل في إرسال الرقصة {emote_name}: {emote_error}")
                        return f"❌ فشل في تنفيذ الرقصة {cmd.get('command')}: {str(emote_error)}"

            return None

        except Exception as e:
            print(f"❌ خطأ في معالجة الأوامر المخصصة: {e}")
            return None

    def get_stats(self):
        """إحصائيات الأوامر المخصصة"""
        nav_count = len(self.commands_data.get("navigation_commands", []))
        dance_count = len(self.commands_data.get("dance_commands", []))
        message_count = len(self.commands_data.get("message_commands", []))
        teleport_count = len(self.commands_data.get("teleport_commands", []))

        return {
            "navigation": nav_count,
            "dance": dance_count,
            "message": message_count,
            "teleport": teleport_count,
            "total": nav_count + dance_count + message_count + teleport_count
        }

    def execute_custom_command(self, command: str, user, requesting_user=None) -> str:
        """تنفيذ أمر مخصص"""
        try:
            # البحث عن الأمر في قاعدة البيانات
            for cmd in self.commands_data.get("navigation_commands", []):
                if cmd["command"].lower() == command.lower():
                    # التحقق من الصلاحيات
                    if not self._check_command_permissions(cmd, user):
                        return f"❌ ليس لديك صلاحية لاستخدام الأمر '{command}'"

                    # تنفيذ الأمر
                    return self._execute_navigation_command(cmd, user)

            return f"❌ الأمر '{command}' غير موجود"

        except Exception as e:
            return f"❌ خطأ في تنفيذ الأمر: {str(e)}"

    def _execute_navigation_command(self, cmd, user):
        """تنفيذ أمر التنقل"""
        try:
            # إرجاع رسالة النجاح مباشرة
            return cmd["message"]

        except Exception as e:
            return f"❌ فشل في النقل: {str(e)}"

    def _check_command_permissions(self, cmd, user) -> bool:
        """فحص صلاحيات المستخدم لتنفيذ الأمر"""
        permissions = cmd.get("permissions", "everyone")

        if permissions == "everyone":
            return True
        elif permissions == "owner":
            # سيتم تطبيق فحص الصلاحيات لاحقاً
            return True
        elif permissions == "moderator":
            # سيتم تطبيق فحص الصلاحيات لاحقاً
            return True
        elif permissions == "vip":
            # سيتم تطبيق فحص الصلاحيات لاحقاً
            return True

        return False

    def get_commands_list(self) -> str:
        """الحصول على قائمة الأوامر المخصصة"""
        try:
            navigation_commands = self.commands_data.get("navigation_commands", [])

            if not navigation_commands:
                return "❌ لا توجد أوامر مخصصة"

            commands_list = "📋 الأوامر المخصصة المتاحة:\n"
            commands_list += "═" * 30 + "\n"

            for i, cmd in enumerate(navigation_commands, 1):
                commands_list += f"{i}. 🎯 {cmd['command']}\n"
                commands_list += f"   📍 الموقع: ({cmd['coordinates']['x']}, {cmd['coordinates']['y']}, {cmd['coordinates']['z']})\n"
                commands_list += f"   🔒 الصلاحية: {cmd['permissions']}\n"
                commands_list += f"   💬 الرسالة: {cmd['message']}\n\n"

            return commands_list

        except Exception as e:
            return f"❌ خطأ في جلب قائمة الأوامر: {str(e)}"

    def make_command_auto_repeat(self, command_word: str, emote_name: str) -> tuple:
        """جعل أمر الرقصة تلقائياً ومتكرراً"""
        try:
            # البحث عن الأمر في قائمة أوامر الرقصات
            dance_commands = self.commands_data.get("dance_commands", [])

            for cmd in dance_commands:
                if cmd.get("command", "").lower() == command_word.lower():
                    # تحديث الأمر ليصبح تلقائياً
                    cmd["auto_repeat"] = True
                    cmd["is_auto_dance"] = True
                    cmd["updated_at"] = datetime.now().isoformat()

                    if self.save_commands():
                        return True, f"✅ تم تحديث الرقصة '{command_word}' لتصبح تلقائية ومتكررة"
                    else:
                        return False, "فشل في حفظ التحديث"

            return False, f"لم يتم العثور على الأمر '{command_word}'"

        except Exception as e:
            return False, f"خطأ في تحديث الأمر: {str(e)}"

# إنشاء المتغير العام
custom_commands_manager = CustomCommandsManager()