
"""
أوامر VIP الخاصة - تحتوي على أوامر متقدمة للأعضاء المميزين
"""
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition

class VipCommands:
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, 'vip_following_tasks'):
            self.bot.vip_following_tasks = {}
        print("💎 أوامر VIP جاهزة")

    async def handle_vip_command(self, user, message):
        """معالجة أوامر VIP"""
        try:
            # أمر الملاحقة المتقدم للـ VIP (الجديد)
            if message.startswith("follow @") or message.startswith("اتبع @") or message.startswith("لاحق @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_follow_user(user, target_username)
                else:
                    return "❌ الاستخدام: follow @اسم_المستخدم أو لاحق @اسم_المستخدم"

            elif message.startswith("stopfollow") or message == "توقف_متابعة" or message == "ايقاف_الملاحقة":
                return await self.vip_stop_follow(user)

            elif message == "followers" or message == "المتابعين" or message == "الملاحقين":
                return await self.get_vip_followers_list(user)

            elif message.startswith("lead @") or message.startswith("قود @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_lead_user(user, target_username)
                else:
                    return "❌ الاستخدام: lead @اسم_المستخدم"

            # أمر إيقاف القيادة للـ VIP
            elif message.startswith("stop_lead @") or message.startswith("الغ_قيادة @") or message.startswith("ايقاف_قيادة @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_stop_lead(user, target_username)
                else:
                    return "❌ الاستخدام: stop_lead @اسم_المستخدم أو الغ_قيادة @اسم_المستخدم"

            elif message == "stop_all_leads" or message == "ايقاف_كل_القيادات":
                return await self.vip_stop_all_leads(user)

            # أمر الغمزة الجديد للـ VIP
            elif message == "wink" or message == "غمزة":
                return await self.vip_wink(user)

            # أوامر العقاب الخاصة بـ VIP والمطور
            elif message.startswith("عقاب @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_start_punishment(user, target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'عقاب @'"

            elif message.startswith("الغ_عقاب @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_stop_punishment(user, target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'الغ_عقاب @'"

            elif message == "المعاقبين":
                return await self.vip_get_punished_users_list(user)

            return None

        except Exception as e:
            print(f"❌ خطأ في معالجة أوامر VIP: {e}")
            return "❌ حدث خطأ في تنفيذ الأمر"

    async def vip_follow_user(self, user, target_username):
        """أمر الملاحقة المتقدم للـ VIP"""
        try:
            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            # التحقق من وجود ملاحقة سابقة
            if user.id in self.bot.vip_following_tasks:
                self.bot.vip_following_tasks[user.id]['task'].cancel()
                del self.bot.vip_following_tasks[user.id]

            # بدء الملاحقة
            task = asyncio.create_task(self._follow_loop(user, target_user))
            self.bot.vip_following_tasks[user.id] = {
                'task': task,
                'target_username': target_user.username,
                'target_id': target_user.id
            }

            return f"💎 بدأت متابعة @{target_user.username} بنجاح! استخدم 'stopfollow' للتوقف"

        except Exception as e:
            return f"❌ فشل في بدء الملاحقة: {str(e)}"

    async def _follow_loop(self, follower_user, target_user):
        """حلقة الملاحقة المتقدمة للـ VIP"""
        try:
            print(f"💎 بدء ملاحقة VIP: {follower_user.username} يتبع {target_user.username}")
            
            while True:
                try:
                    # الحصول على موقع المستخدم المستهدف
                    room_users = await self.bot.highrise.get_room_users()
                    target_position = None
                    
                    for room_user, position in room_users.content:
                        if room_user.id == target_user.id:
                            target_position = position
                            break
                    
                    if target_position is None:
                        # المستخدم المستهدف غادر الغرفة
                        await self.bot.highrise.send_whisper(
                            follower_user.id, 
                            f"💎 توقفت المتابعة - @{target_user.username} غادر الغرفة"
                        )
                        break
                    
                    # تحريك البوت بجانب المستخدم المستهدف
                    if type(target_position) != AnchorPosition:
                        # حساب موقع محسن بجانب المستخدم
                        follow_position = Position(
                            target_position.x + 1.0,  # بجانب المستخدم
                            target_position.y,
                            target_position.z
                        )
                        
                        await self.bot.highrise.walk_to(follow_position)
                    
                    # تأخير أقل للاستجابة السريعة
                    await asyncio.sleep(0.3)
                
                except Exception as e:
                    print(f"⚠️ خطأ في حلقة ملاحقة VIP: {e}")
                    await asyncio.sleep(1)
                    continue
                    
        except asyncio.CancelledError:
            print(f"💎 تم إلغاء ملاحقة VIP: {follower_user.username}")
        except Exception as e:
            print(f"❌ خطأ في ملاحقة VIP: {e}")
            await self.bot.highrise.send_whisper(
                follower_user.id, 
                f"❌ حدث خطأ في المتابعة: {str(e)}"
            )

    async def vip_stop_follow(self, user):
        """إيقاف الملاحقة للـ VIP"""
        try:
            if user.id not in self.bot.vip_following_tasks:
                return "❌ أنت لا تتابع أي شخص حالياً"
            
            # إلغاء المهمة
            self.bot.vip_following_tasks[user.id]['task'].cancel()
            target_username = self.bot.vip_following_tasks[user.id]['target_username']
            del self.bot.vip_following_tasks[user.id]
            
            return f"💎 تم إيقاف متابعة @{target_username} بنجاح"
            
        except Exception as e:
            return f"❌ فشل في إيقاف المتابعة: {str(e)}"

    async def get_vip_followers_list(self, user):
        """قائمة المتابعين الحاليين للـ VIP"""
        try:
            if not self.bot.vip_following_tasks:
                return "❌ لا يوجد أعضاء VIP يتابعون أحد حالياً"
            
            followers_list = []
            for follower_id, data in self.bot.vip_following_tasks.items():
                # الحصول على اسم المتابع
                room_users = await self.bot.highrise.get_room_users()
                follower_name = "مجهول"
                
                for room_user, _ in room_users.content:
                    if room_user.id == follower_id:
                        follower_name = room_user.username
                        break
                
                followers_list.append(f"💎 {follower_name} ← {data['target_username']}")
            
            if followers_list:
                return f"📋 قائمة متابعات VIP ({len(followers_list)}):\n" + "\n".join(followers_list)
            else:
                return "❌ لا يوجد متابعات VIP نشطة"
                
        except Exception as e:
            return f"❌ خطأ في جلب قائمة المتابعين: {str(e)}"

    async def vip_lead_user(self, user, target_username):
        """أمر قيادة متقدم للـ VIP - يجعل المستخدم المستهدف يتبع الـ VIP"""
        try:
            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            # إنشاء مهمة قيادة
            task_key = f"lead_{target_user.id}"
            if hasattr(self.bot, 'vip_lead_tasks') and task_key in self.bot.vip_lead_tasks:
                self.bot.vip_lead_tasks[task_key]['task'].cancel()
            
            if not hasattr(self.bot, 'vip_lead_tasks'):
                self.bot.vip_lead_tasks = {}

            task = asyncio.create_task(self._lead_loop(user, target_user))
            self.bot.vip_lead_tasks[task_key] = {
                'task': task,
                'leader_username': user.username,
                'target_username': target_user.username
            }

            return f"💎 الآن @{target_user.username} يتبعك! استخدم 'stop_lead @{target_username}' للتوقف"

        except Exception as e:
            return f"❌ فشل في بدء القيادة: {str(e)}"

    async def _lead_loop(self, leader_user, target_user):
        """حلقة القيادة - جعل المستخدم يتبع الـ VIP"""
        try:
            print(f"💎 بدء قيادة VIP: {target_user.username} يتبع {leader_user.username}")
            
            while True:
                try:
                    # الحصول على موقع القائد (VIP)
                    room_users = await self.bot.highrise.get_room_users()
                    leader_position = None
                    target_exists = False
                    
                    for room_user, position in room_users.content:
                        if room_user.id == leader_user.id:
                            leader_position = position
                        if room_user.id == target_user.id:
                            target_exists = True
                    
                    if not target_exists:
                        # المستخدف المستهدف غادر
                        break
                    
                    if leader_position and type(leader_position) != AnchorPosition:
                        # نقل المستخدم المستهدف بجانب القائد
                        follow_position = Position(
                            leader_position.x - 1.0,  # خلف القائد
                            leader_position.y,
                            leader_position.z
                        )
                        
                        await self.bot.highrise.teleport(target_user.id, follow_position)
                    
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    print(f"⚠️ خطأ في حلقة قيادة VIP: {e}")
                    await asyncio.sleep(1)
                    continue
                    
        except asyncio.CancelledError:
            print(f"💎 تم إلغاء قيادة VIP")
        except Exception as e:
            print(f"❌ خطأ في قيادة VIP: {e}")

    async def vip_stop_lead(self, user, target_username):
        """إيقاف قيادة مستخدم محدد"""
        try:
            if not hasattr(self.bot, 'vip_lead_tasks'):
                return "❌ لا توجد مهام قيادة نشطة"

            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            task_key = f"lead_{target_user.id}"
            
            if task_key not in self.bot.vip_lead_tasks:
                return f"❌ المستخدم @{target_username} غير مقود حالياً"
            
            # إلغاء مهمة القيادة
            self.bot.vip_lead_tasks[task_key]['task'].cancel()
            del self.bot.vip_lead_tasks[task_key]
            
            print(f"💎 تم إيقاف قيادة VIP لـ {target_username}")
            return f"💎 تم إيقاف قيادة @{target_username} بنجاح"
            
        except Exception as e:
            print(f"❌ خطأ في إيقاف قيادة VIP: {e}")
            return f"❌ فشل في إيقاف القيادة: {str(e)}"

    async def vip_stop_all_leads(self, user):
        """إيقاف جميع مهام القيادة"""
        try:
            if not hasattr(self.bot, 'vip_lead_tasks') or not self.bot.vip_lead_tasks:
                return "❌ لا توجد مهام قيادة نشطة"

            stopped_count = 0
            stopped_users = []
            
            # إيقاف جميع مهام القيادة
            for task_key, data in list(self.bot.vip_lead_tasks.items()):
                try:
                    data['task'].cancel()
                    stopped_users.append(data['target_username'])
                    stopped_count += 1
                except Exception as e:
                    print(f"❌ خطأ في إيقاف مهمة القيادة {task_key}: {e}")
            
            # مسح جميع المهام
            self.bot.vip_lead_tasks.clear()
            
            if stopped_count > 0:
                users_list = ", ".join(stopped_users[:3])
                if len(stopped_users) > 3:
                    users_list += f" و {len(stopped_users) - 3} آخرين"
                
                print(f"💎 تم إيقاف {stopped_count} مهمة قيادة VIP")
                return f"💎 تم إيقاف جميع مهام القيادة ({stopped_count}):\n📋 المستخدمين: {users_list}"
            else:
                return "❌ لم يتم إيقاف أي مهام قيادة"
                
        except Exception as e:
            print(f"❌ خطأ في إيقاف جميع مهام القيادة VIP: {e}")
            return f"❌ فشل في إيقاف جميع القيادات: {str(e)}"

    async def vip_wink(self, user):
        """أمر الغمزة الخاص بـ VIP"""
        try:
            # تنفيذ حركة الغمزة
            await self.bot.highrise.send_emote("emote-lust", user.id)
            
            # إرسال رسالة في الشات العام للتأثير
            await self.bot.highrise.chat(f"😉 {user.username} يرسل غمزة مميزة! 💎")
            
            print(f"💎 تم تنفيذ أمر الغمزة VIP بواسطة {user.username}")
            return "😉💎 تم إرسال الغمزة المميزة بنجاح!"
            
        except Exception as e:
            print(f"❌ خطأ في تنفيذ الغمزة VIP: {e}")
            return "❌ فشل في تنفيذ الغمزة، جرب مرة أخرى"

    async def vip_start_punishment(self, user, target_username: str):
        """بدء العقاب VIP - خاص بـ VIP والمطور"""
        try:
            # البحث عن المستخدم في الغرفة
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            original_position = None

            for room_user, position in room_users:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    original_position = position
                    break

            if not target_user:
                return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

            # تهيئة قاموس العقاب إذا لم يكن موجود
            if not hasattr(self.bot, 'vip_punishment_tasks'):
                self.bot.vip_punishment_tasks = {}

            # إيقاف أي عقاب سابق لنفس المستخدم
            if target_user.id in self.bot.vip_punishment_tasks:
                self.bot.vip_punishment_tasks[target_user.id]["task"].cancel()

            # بدء العقاب مع حفظ الموقع الأصلي
            punishment_task = asyncio.create_task(
                self._vip_punish_user_continuously(user, target_user, original_position)
            )
            self.bot.vip_punishment_tasks[target_user.id] = {
                "task": punishment_task,
                "vip_user": user.username,
                "target_username": target_username,
                "target_id": target_user.id,
                "original_position": original_position
            }

            await self.bot.highrise.chat(f"💎⚡ VIP {user.username} بدأ عقاب متقدم لـ @{target_username}!")
            print(f"💎⚡ VIP {user.username} بدأ عقاب {target_username}")
            return f"💎✅ تم بدء العقاب المتقدم لـ {target_username} بنجاح!"

        except Exception as e:
            print(f"❌ خطأ في بدء العقاب VIP: {e}")
            return f"❌ فشل في بدء العقاب: {str(e)}"

    async def _vip_punish_user_continuously(self, vip_user, target_user, original_position=None):
        """تطبيق العقاب المستمر بواسطة VIP"""
        try:
            import random
            from highrise import Position

            print(f"💎⚡ بدء العقاب VIP: {vip_user.username} يعاقب {target_user.username}")

            punishment_count = 0
            max_punishments = 75  # VIP يحصل على عدد أكبر من العقاب

            while (target_user.id in getattr(self.bot, 'vip_punishment_tasks', {}) and 
                   punishment_count < max_punishments):
                try:
                    # إنشاء إحداثيات عشوائية متقدمة
                    x_ranges = [
                        (-25, -15), (15, 25), (-35, -25), (25, 35),
                        (-45, -35), (35, 45), (-20, 20), (-60, 60)
                    ]
                    z_ranges = [
                        (-25, -15), (15, 25), (-35, -25), (25, 35),
                        (-45, -35), (35, 45), (-20, 20), (-60, 60)
                    ]
                    y_values = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

                    # اختيار نطاق عشوائي
                    x_range = random.choice(x_ranges)
                    z_range = random.choice(z_ranges)

                    # إنشاء موقع عشوائي
                    random_position = Position(
                        x=random.uniform(x_range[0], x_range[1]),
                        y=random.choice(y_values),
                        z=random.uniform(z_range[0], z_range[1])
                    )

                    # نقل المستخدم
                    await self.bot.highrise.teleport(target_user.id, random_position)

                    punishment_count += 1
                    print(f"💎⚡ العقاب VIP {punishment_count}: نقل {target_user.username} بواسطة {vip_user.username}")

                    # انتظار أقصر للعقاب المتقدم
                    await asyncio.sleep(random.uniform(0.05, 0.2))

                    # رسائل متقدمة
                    if punishment_count == 25:
                        await self.bot.highrise.chat(f"💎⚡ عقاب VIP في التقدم! {target_user.username} يتم تأديبه...")
                    elif punishment_count == 50:
                        await self.bot.highrise.chat(f"💎🔥 العقاب المتقدم يشتد! {target_user.username} لا يستطيع الهرب!")

                except Exception as teleport_error:
                    print(f"⚠️ خطأ في نقل المستخدم أثناء العقاب VIP: {teleport_error}")
                    await asyncio.sleep(0.3)
                    continue

            # انتهاء العقاب - إرجاع المستخدم لمكانه الأصلي
            try:
                if original_position:
                    await self.bot.highrise.teleport(target_user.id, original_position)
                    await self.bot.highrise.chat(f"💎🏠 تم إرجاع @{target_user.username} إلى مكانه الأصلي بعد العقاب المتقدم!")
                    print(f"💎🏠 تم إرجاع {target_user.username} إلى مكانه الأصلي")
                else:
                    print(f"⚠️ لا يوجد موقع أصلي محفوظ لـ {target_user.username}")
            except Exception as return_error:
                print(f"❌ خطأ في إرجاع المستخدم لمكانه الأصلي: {return_error}")

            # إزالة من قائمة العقاب
            if target_user.id in getattr(self.bot, 'vip_punishment_tasks', {}):
                del self.bot.vip_punishment_tasks[target_user.id]

            await self.bot.highrise.chat(f"💎✅ انتهى العقاب المتقدم لـ @{target_user.username} - تم نقله {punishment_count} مرة بواسطة VIP {vip_user.username}!")
            print(f"💎✅ انتهى العقاب VIP لـ {target_user.username} بعد {punishment_count} عملية نقل")

        except asyncio.CancelledError:
            print(f"💎⏹️ تم إلغاء العقاب VIP لـ {target_user.username}")
            # محاولة إرجاع المستخدم لمكانه الأصلي حتى لو تم إلغاء العقاب
            try:
                if original_position:
                    await self.bot.highrise.teleport(target_user.id, original_position)
                    await self.bot.highrise.chat(f"💎🏠 تم إرجاع @{target_user.username} إلى مكانه الأصلي بعد إلغاء العقاب VIP!")
            except:
                pass
            await self.bot.highrise.chat(f"💎⏹️ تم إلغاء العقاب VIP لـ @{target_user.username}")
        except Exception as e:
            print(f"❌ خطأ في مهمة العقاب VIP: {e}")

    async def vip_stop_punishment(self, user, target_username: str):
        """إيقاف العقاب VIP عن المستخدم"""
        try:
            if not hasattr(self.bot, 'vip_punishment_tasks') or not self.bot.vip_punishment_tasks:
                return "❌ لا توجد عقوبات VIP نشطة حالياً"

            # البحث عن المستخدم في العقوبات النشطة
            target_user_id = None
            punishment_data = None
            for user_id, data in self.bot.vip_punishment_tasks.items():
                if data["target_username"].lower() == target_username.lower():
                    target_user_id = user_id
                    punishment_data = data
                    break

            if not target_user_id:
                return f"❌ المستخدم '{target_username}' ليس تحت العقاب VIP حالياً"

            # إلغاء العقاب
            punishment_data["task"].cancel()

            # محاولة إرجاع المستخدم لمكانه الأصلي
            original_position = punishment_data.get("original_position")
            if original_position:
                try:
                    await self.bot.highrise.teleport(target_user_id, original_position)
                    await self.bot.highrise.chat(f"💎🏠 تم إرجاع @{target_username} إلى مكانه الأصلي!")
                except Exception as e:
                    print(f"❌ خطأ في إرجاع المستخدم لمكانه الأصلي: {e}")

            del self.bot.vip_punishment_tasks[target_user_id]

            await self.bot.highrise.chat(f"💎🛑 تم إلغاء العقاب VIP عن @{target_username} بواسطة {user.username}")
            print(f"💎🛑 VIP {user.username} ألغى العقاب عن {target_username}")
            return f"💎✅ تم إلغاء العقاب VIP عن {target_username} بنجاح"

        except Exception as e:
            print(f"❌ خطأ في إلغاء العقاب VIP: {e}")
            return f"❌ فشل في إلغاء العقاب: {str(e)}"

    async def vip_get_punished_users_list(self, user):
        """عرض قائمة المستخدمين المعاقبين بواسطة VIP"""
        try:
            if not hasattr(self.bot, 'vip_punishment_tasks') or not self.bot.vip_punishment_tasks:
                return "💎⚡ لا يوجد مستخدمين تحت العقاب VIP حالياً"

            punished_users = []
            for user_id, punishment_data in self.bot.vip_punishment_tasks.items():
                vip_user = punishment_data["vip_user"]
                target_user = punishment_data["target_username"]
                punished_users.append(f"💎 {target_user} (بواسطة {vip_user})")

            users_text = "\n".join(punished_users)
            count = len(self.bot.vip_punishment_tasks)

            return f"💎⚡ المستخدمين تحت العقاب VIP حالياً ({count}):\n{users_text}\n💡 استخدم 'الغ_عقاب @اسم_المستخدم' لإلغاء العقاب"

        except Exception as e:
            print(f"❌ خطأ في عرض قائمة المعاقبين VIP: {e}")
            return f"❌ خطأ في عرض قائمة المعاقبين: {str(e)}"
