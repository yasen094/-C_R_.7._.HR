
"""
نظام فحص المشرفين من إعدادات الغرفة التلقائي
"""
import asyncio
from highrise import BaseBot
from highrise.webapi import WebAPI
from datetime import datetime
import json
import os

class RoomModeratorDetector:
    def __init__(self, bot):
        self.bot = bot
        self.webapi = WebAPI()
        self.room_id = None
        self.last_check = None
        print("🔍 نظام فحص المشرفين من إعدادات الغرفة جاهز")

    async def get_room_moderators(self):
        """الحصول على قائمة المشرفين من إعدادات الغرفة"""
        try:
            if not self.room_id:
                # محاولة الحصول على room_id من البوت
                room_info = await self.bot.highrise.get_room_users()
                if hasattr(self.bot.highrise, 'room_id'):
                    self.room_id = self.bot.highrise.room_id
                else:
                    print("❌ لا يمكن الحصول على معرف الغرفة")
                    return []

            # استخدام WebAPI للحصول على معلومات الغرفة
            room_data = await self.webapi.get_room(self.room_id)
            
            if not room_data:
                print("❌ لا يمكن الحصول على بيانات الغرفة")
                return []

            moderators = []
            
            # فحص المشرفين من إعدادات الغرفة
            if hasattr(room_data, 'moderators'):
                for mod in room_data.moderators:
                    moderators.append({
                        'id': mod.id,
                        'username': mod.username,
                        'role': 'moderator'
                    })
            
            # فحص مالك الغرفة
            if hasattr(room_data, 'owner'):
                moderators.append({
                    'id': room_data.owner.id,
                    'username': room_data.owner.username,
                    'role': 'owner'
                })

            print(f"🔍 تم العثور على {len(moderators)} مشرف في إعدادات الغرفة")
            return moderators

        except Exception as e:
            print(f"❌ خطأ في فحص مشرفي الغرفة: {e}")
            return []

    async def sync_moderators_with_room_settings(self):
        """عرض إحصائيات الغرفة ومعلومات المشرفين مع فحص متقدم"""
        try:
            # الحصول على المستخدمين الحاليين في الغرفة
            room_users = await self.bot.highrise.get_room_users()
            current_users_count = len(room_users.content)
            
            # تحديث صلاحيات المستخدمين باستخدام النظام المتقدم
            await self.bot.user_manager.sync_with_room_users(room_users.content, self.bot)
            
            # الحصول على إحصائيات محدثة من user_manager
            current_moderators = self.bot.user_manager.get_moderators_list()
            room_moderators = self.bot.user_manager.room_moderators
            total_users_ever = self.bot.user_manager.get_total_users_count()
            
            # فحص المشرفين الموجودين حالياً في الغرفة
            online_moderators = []
            online_highrise_mods = []
            
            for user, _ in room_users.content:
                user_type = self.bot.user_manager.get_user_type_advanced(user)
                emoji = self.bot.user_manager.get_user_emoji(user.username)
                
                # المشرفين من القائمة اليدوية
                if user.username in current_moderators:
                    online_moderators.append(f"{emoji} {user.username}")
                
                # المشرفين من إعدادات Highrise
                if user.id in room_moderators:
                    online_highrise_mods.append(f"{emoji} {user.username}")
            
            # تحديث وقت آخر فحص
            self.last_check = datetime.now().isoformat()
            
            # بناء التقرير المحسن
            result_msg = f"📊 إحصائيات الغرفة المحدثة:\n"
            result_msg += f"👥 المتصلين الآن: {current_users_count}\n"
            result_msg += f"📈 إجمالي الزوار: {total_users_ever}\n"
            result_msg += f"👮‍♂️ المشرفين اليدويين: {len(current_moderators)}\n"
            result_msg += f"🏠 مشرفي Highrise: {len(room_moderators)}\n"
            
            if online_moderators:
                result_msg += f"🟢 المشرفين اليدويين المتصلين ({len(online_moderators)}):\n"
                result_msg += "\n".join([f"  • {mod}" for mod in online_moderators])
            
            if online_highrise_mods:
                result_msg += f"\n🏠 مشرفي Highrise المتصلين ({len(online_highrise_mods)}):\n"
                result_msg += "\n".join([f"  • {mod}" for mod in online_highrise_mods])
            
            if not online_moderators and not online_highrise_mods:
                result_msg += f"🔴 لا يوجد مشرفين متصلين حالياً"
                
            result_msg += f"\n🕐 آخر فحص: {datetime.now().strftime('%H:%M:%S')}"
            
            return result_msg

        except Exception as e:
            error_msg = f"❌ خطأ في الحصول على إحصائيات الغرفة: {str(e)}"
            print(error_msg)
            return error_msg

    async def auto_check_moderators(self):
        """فحص دوري تلقائي للمشرفين (كل 30 دقيقة)"""
        while True:
            try:
                await asyncio.sleep(1800)  # 30 دقيقة
                result = await self.sync_moderators_with_room_settings()
                if "تم إضافة" in result:
                    await self.bot.highrise.chat("🔄 تم اكتشاف مشرفين جدد وإضافتهم تلقائياً!")
                    print(f"🔄 فحص تلقائي: {result}")
            except Exception as e:
                print(f"❌ خطأ في الفحص التلقائي: {e}")
                await asyncio.sleep(300)  # إعادة المحاولة بعد 5 دقائق

    def get_status(self):
        """الحصول على حالة نظام الفحص"""
        status = f"🔍 نظام فحص المشرفين:\n"
        status += f"📍 معرف الغرفة: {self.room_id or 'غير محدد'}\n"
        status += f"🕐 آخر فحص: {self.last_check[:19] if self.last_check else 'لم يتم فحص بعد'}\n"
        status += f"👮‍♂️ المشرفين المدونين: {len(self.bot.user_manager.get_moderators_list())}"
        return status
