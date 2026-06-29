
"""
مدير نشاط المستخدمين الخاملين - نظام محسن لمراقبة النشاط والرقص التلقائي
"""
import json
import os
import time
import asyncio
from datetime import datetime
from typing import Dict, Optional, Set

class IdleActivityManager:
    def __init__(self):
        self.auto_dance_file = "data/auto_dance_users.json"
        self.idle_threshold = 1000
        
        # تتبع آخر نشاط للمستخدمين (حركة + كلام)
        self.user_last_activity = {}  # {user_id: {"movement": timestamp, "chat": timestamp}}
        
        # المستخدمين الذين فعلوا الرقص التلقائي
        self.auto_dance_users = {}  # {user_id: {"username": str, "enabled_at": timestamp, "emote": str}}
        
        # المستخدمين الخاملين الذين يرقصون تلقائياً بنظام العاملين
        self.idle_dancers = {}  # {user_id: task}
        
        # رقصات العاملين المخصصة
        self.idle_emotes = [
            "idle-fighter", "idle-dance-tiktok7", "idle_singing", "idle-enthusiastic",
            "idle-floorsleeping2", "idle-floorsleeping", "idle-posh", "idle-sad",
            "idle-angry", "idle-hero", "idle-lookup", "idle_relaxed",
            "idle_layingdown", "idle-sleep", "idle-loop-annoyed", "idle-loop-tapdance",
            "idle-loop-sad", "idle-loop-happy", "idle-loop-aerobics", "idle-dance-swinging",
            "idle-loop-tired", "idle-loop-shy", "idle-loop-sitfloor", "idle-dance-casual",
            "idle-dance-tiktok4", "idle-uwu"
        ]
        
        self.load_auto_dance_data()
        print("😴 مدير نشاط المستخدمين الخاملين المحسن جاهز!")

    def load_auto_dance_data(self):
        """تحميل بيانات المستخدمين الذين فعلوا الرقص التلقائي"""
        try:
            if os.path.exists(self.auto_dance_file):
                with open(self.auto_dance_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.auto_dance_users = data.get("active_auto_dance_users", {})
                print(f"📂 تم تحميل {len(self.auto_dance_users)} مستخدم مع رقص تلقائي نشط")
            else:
                os.makedirs("data", exist_ok=True)
                self.auto_dance_users = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات الرقص التلقائي: {e}")
            self.auto_dance_users = {}

    def save_auto_dance_data(self):
        """حفظ بيانات المستخدمين الذين فعلوا الرقص التلقائي"""
        try:
            data = {
                "active_auto_dance_users": self.auto_dance_users,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.auto_dance_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات الرقص التلقائي: {e}")

    def register_user_movement(self, user_id: str, username: str):
        """تسجيل حركة المستخدم"""
        current_time = time.time()
        
        if user_id not in self.user_last_activity:
            self.user_last_activity[user_id] = {
                "username": username,
                "movement": current_time,
                "chat": 0  # لم يتكلم بعد
            }
        else:
            self.user_last_activity[user_id]["movement"] = current_time
            self.user_last_activity[user_id]["username"] = username
        
        # إيقاف رقص العاملين إذا كان نشطاً
        if user_id in self.idle_dancers:
            self.idle_dancers[user_id].cancel()
            del self.idle_dancers[user_id]
            print(f"🏃 {username} تحرك - تم إيقاف رقص العاملين")

    def register_user_chat(self, user_id: str, username: str):
        """تسجيل كلام المستخدم"""
        current_time = time.time()
        
        if user_id not in self.user_last_activity:
            self.user_last_activity[user_id] = {
                "username": username,
                "movement": 0,  # لم يتحرك بعد
                "chat": current_time
            }
        else:
            self.user_last_activity[user_id]["chat"] = current_time
            self.user_last_activity[user_id]["username"] = username
        
        # إيقاف رقص العاملين إذا كان نشطاً
        if user_id in self.idle_dancers:
            self.idle_dancers[user_id].cancel()
            del self.idle_dancers[user_id]
            print(f"💬 {username} تكلم - تم إيقاف رقص العاملين")

    def add_auto_dance_user(self, user_id: str, username: str, emote: str = "random") -> str:
        """إضافة مستخدم للرقص التلقائي"""
        try:
            self.auto_dance_users[user_id] = {
                "username": username,
                "enabled_at": datetime.now().isoformat(),
                "emote": emote,
                "enabled_timestamp": time.time()
            }
            
            # إيقاف رقص العاملين إذا كان نشطاً
            if user_id in self.idle_dancers:
                self.idle_dancers[user_id].cancel()
                del self.idle_dancers[user_id]
                print(f"🔄 {username} فعل الرقص التلقائي - تم إيقاف رقص العاملين")
            
            self.save_auto_dance_data()
            return f"✅ تم تفعيل الرقص التلقائي لـ {username}"
        except Exception as e:
            return f"❌ خطأ في تفعيل الرقص التلقائي: {str(e)}"

    def remove_auto_dance_user(self, user_id: str) -> str:
        """إزالة مستخدم من الرقص التلقائي"""
        try:
            if user_id in self.auto_dance_users:
                username = self.auto_dance_users[user_id]["username"]
                del self.auto_dance_users[user_id]
                self.save_auto_dance_data()
                print(f"❌ {username} أوقف الرقص التلقائي")
                return f"✅ تم إيقاف الرقص التلقائي لـ {username}"
            else:
                return "❌ المستخدم ليس مفعل للرقص التلقائي"
        except Exception as e:
            return f"❌ خطأ في إيقاف الرقص التلقائي: {str(e)}"

    def is_user_auto_dancing(self, user_id: str) -> bool:
        """التحقق من أن المستخدم لديه رقص تلقائي مفعل"""
        return user_id in self.auto_dance_users

    def is_user_idle(self, user_id: str) -> bool:
        """التحقق من أن المستخدم خامل (لم يتحرك ولم يتكلم لأكثر من 10 دقائق)"""
        if user_id not in self.user_last_activity:
            return False
        
        current_time = time.time()
        activity = self.user_last_activity[user_id]
        
        # آخر نشاط هو الأحدث بين الحركة والكلام
        last_movement = activity.get("movement", 0)
        last_chat = activity.get("chat", 0)
        last_activity = max(last_movement, last_chat)
        
        # إذا لم يكن هناك أي نشاط، يعتبر غير خامل (جديد)
        if last_activity == 0:
            return False
        
        # خامل إذا مر أكثر من 10 دقائق على آخر نشاط
        return (current_time - last_activity) >= self.idle_threshold

    def get_idle_users_for_dancing(self, room_users_data) -> list:
        """الحصول على المستخدمين الخاملين المؤهلين لرقص العاملين"""
        idle_candidates = []
        
        for user, position in room_users_data:
            user_id = user.id
            username = user.username
            
            # تجاهل البوت نفسه
            if user_id == "657a06ae5f8a5ec3ff16ec1b":
                continue
            
            # تجاهل من لديه رقص تلقائي مفعل
            if self.is_user_auto_dancing(user_id):
                continue
            
            # تجاهل من يرقص رقص العاملين حالياً
            if user_id in self.idle_dancers:
                continue
            
            # فحص إذا كان خامل
            if self.is_user_idle(user_id):
                idle_candidates.append({
                    "user_id": user_id,
                    "username": username
                })
        
        return idle_candidates

    async def start_idle_dance_for_user(self, user_id: str, username: str, highrise):
        """بدء رقص العاملين لمستخدم معين"""
        try:
            import random
            
            print(f"😴 بدء رقص العاملين لـ {username}")
            
            while user_id in self.idle_dancers:
                # تأكد أن المستخدم ما زال خامل وليس لديه رقص تلقائي
                if not self.is_user_idle(user_id) or self.is_user_auto_dancing(user_id):
                    break
                
                # اختيار رقصة عشوائية من رقصات العاملين
                emote = random.choice(self.idle_emotes)
                
                try:
                    await highrise.send_emote(emote, user_id)
                    print(f"😴 {username} يرقص رقصة عاملين: {emote}")
                except Exception as emote_error:
                    print(f"فشل في إرسال رقصة العاملين لـ {username}: {emote_error}")
                
                # انتظار 20-40 ثانية قبل الرقصة التالية
                wait_time = random.randint(20, 40)
                await asyncio.sleep(wait_time)
                
        except Exception as e:
            print(f"خطأ في رقص العاملين للمستخدم {username}: {e}")
        finally:
            # تنظيف
            if user_id in self.idle_dancers:
                del self.idle_dancers[user_id]
                print(f"🧹 تم إنهاء رقص العاملين لـ {username}")

    async def monitor_idle_users(self, highrise):
        """مراقبة المستخدمين الخاملين وبدء رقص العاملين"""
        while True:
            try:
                # الحصول على المستخدمين الحاليين في الغرفة
                room_users = await highrise.get_room_users()
                
                if room_users and room_users.content:
                    # الحصول على المستخدمين الخاملين المؤهلين
                    idle_users = self.get_idle_users_for_dancing(room_users.content)
                    
                    for idle_user in idle_users:
                        user_id = idle_user["user_id"]
                        username = idle_user["username"]
                        
                        # بدء رقص العاملين إذا لم يكن نشطاً
                        if user_id not in self.idle_dancers:
                            task = asyncio.create_task(
                                self.start_idle_dance_for_user(user_id, username, highrise)
                            )
                            self.idle_dancers[user_id] = task
                
                # فحص كل 30 ثانية
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"خطأ في مراقبة المستخدمين الخاملين: {e}")
                await asyncio.sleep(30)

    def cleanup_disconnected_users(self, current_user_ids: Set[str]):
        """تنظيف بيانات المستخدمين المنقطعين"""
        # تنظيف النشاط
        disconnected_activity = set(self.user_last_activity.keys()) - current_user_ids
        for user_id in disconnected_activity:
            del self.user_last_activity[user_id]
        
        # تنظيف الرقص التلقائي للمنقطعين
        disconnected_auto_dance = set(self.auto_dance_users.keys()) - current_user_ids
        for user_id in disconnected_auto_dance:
            username = self.auto_dance_users[user_id]["username"]
            del self.auto_dance_users[user_id]
            print(f"🧹 تم إزالة {username} من الرقص التلقائي (منقطع)")
        
        # تنظيف رقص العاملين للمنقطعين
        disconnected_idle = set(self.idle_dancers.keys()) - current_user_ids
        for user_id in disconnected_idle:
            self.idle_dancers[user_id].cancel()
            del self.idle_dancers[user_id]
        
        # حفظ التغييرات
        if disconnected_auto_dance:
            self.save_auto_dance_data()

    def get_activity_stats(self) -> str:
        """الحصول على إحصائيات النشاط"""
        current_time = time.time()
        total_tracked = len(self.user_last_activity)
        auto_dance_count = len(self.auto_dance_users)
        idle_dance_count = len(self.idle_dancers)
        
        # عد المستخدمين الخاملين
        idle_count = 0
        for user_id in self.user_last_activity:
            if self.is_user_idle(user_id):
                idle_count += 1
        
        stats = [
            "📊 إحصائيات نشاط المستخدمين:",
            f"👥 إجمالي المتتبعين: {total_tracked}",
            f"😴 المستخدمين الخاملين: {idle_count}",
            f"🔄 الرقص التلقائي النشط: {auto_dance_count}",
            f"💤 رقص العاملين النشط: {idle_dance_count}",
            f"⏰ حد الخمول: {self.idle_threshold // 60} دقائق"
        ]
        
        return "\n".join(stats)

    def get_auto_dance_users_list(self) -> str:
        """الحصول على قائمة المستخدمين الذين فعلوا الرقص التلقائي"""
        if not self.auto_dance_users:
            return "📭 لا يوجد مستخدمين لديهم رقص تلقائي مفعل"
        
        result = "🔄 المستخدمين مع الرقص التلقائي:\n"
        for user_id, data in self.auto_dance_users.items():
            username = data["username"]
            enabled_date = data["enabled_at"][:16]
            emote = data.get("emote", "عشوائي")
            result += f"• {username} - {emote} ({enabled_date})\n"
        
        return result.strip()
