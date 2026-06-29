"""
نظام إدارة المستخدمين المحدث مع التعرف المتقدم على الصلاحيات
"""
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from highrise import User, Position

class UserManager:
    def __init__(self):
        # البيانات الحية للمستخدمين الحاليين في الغرفة
        self.users = {}  # المستخدمين النشطين فقط في الغرفة
        self.data_file = "data/users_data.json"

        # ملف منفصل لحفظ جميع من دخل الغرفة (تاريخي)
        self.people_file = "data/people.json"
        self.people_data = {}  # جميع من دخل الغرفة على الإطلاق

        self.moderators_file = "data/moderators.json"
        # إعدادات ثابتة للمشرفين
        self.bot_id = '657a06ae5f8a5ec3ff16ec1b'  # معرف البوت الجديد
        self.owner_username = 'HR_LY'  # اسم مالك البوت
        self.owner_id = '65402b9fffc87c0146e3dcb3'  # معرف مالك البوت
        self.room_king = "HR_LY"  # صاحب الغرفة

        # قائمة المشرفين من الملف
        self.moderators_list = []

        # النظام المتقدم للتعرف على المشرفين
        self.room_moderators = []  # قائمة مشرفي الغرفة من إعدادات Highrise
        self.room_owner = None     # مالك الغرفة من إعدادات Highrise
        self.known_room_owners = ["lopns_", "selAbu_Nasser_711_", "Abu_Nasser_711_"]  # قائمة مالكي الغرف المعروفين

        # النظام المتقدم - ملك وملكة الغرفة
        self.room_king = None      # ملك الغرفة
        self.room_queen = None     # ملكة الغرفة

        # نظام VIP
        self.vip_file = "data/vip_users.json"
        self.vip_users = {}  # قائمة مستخدمي VIP

        self.load_all_data()
        print("👥 مدير المستخدمين المحدث مع نظام التعرف المتقدم جاهز")

    def load_all_data(self):
        """تحميل جميع البيانات من الملفات"""
        self.load_users_data()
        self.load_people_data()
        self.load_moderators_data()
        self.load_vip_data()

    def load_users_data(self):
        """تحميل بيانات المستخدمين النشطين"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data if isinstance(data, dict) else {}
                print(f"📂 تم تحميل بيانات {len(self.users)} مستخدم نشط")
            else:
                os.makedirs("data", exist_ok=True)
                self.users = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات المستخدمين: {e}")
            self.users = {}

    def load_people_data(self):
        """تحميل بيانات جميع الأشخاص الذين دخلوا الغرفة"""
        try:
            if os.path.exists(self.people_file):
                with open(self.people_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.people_data = data if isinstance(data, dict) else {}
                print(f"👥 تم تحميل بيانات {len(self.people_data)} شخص في السجل التاريخي")
            else:
                os.makedirs("data", exist_ok=True)
                self.people_data = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات الأشخاص: {e}")
            self.people_data = {}

    def load_moderators_data(self):
        """تحميل قائمة المشرفين من الملف"""
        try:
            if os.path.exists(self.moderators_file):
                with open(self.moderators_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.moderators_list = data.get("moderators", [])
                    # تحميل البيانات المتقدمة
                    self.room_moderators = data.get("room_moderators", [])
                    self.room_owner = data.get("room_owner", None)
                    self.room_king = data.get("room_king", None)
                    self.room_queen = data.get("room_queen", None)
                    print(f"📋 تم تحميل {len(self.moderators_list)} مشرف من القائمة اليدوية")
                    print(f"👮‍♂️ تم تحميل {len(self.room_moderators)} مشرف من إعدادات الغرفة")
            else:
                # إنشاء ملف المشرفين الافتراضي
                self.moderators_list = [
                    "VECTOR000",
                    "Abu_Nasser_711_",
                    "kim_impose",
                    "NVuM_1",
                    "ASDFGH2025",
                    "Mayagghhj"
                ]
                self.save_moderators_data()
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات المشرفين: {e}")
            self.moderators_list = []

    def save_users_data(self):
        """حفظ بيانات المستخدمين النشطين"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات المستخدمين: {e}")

    def save_people_data(self):
        """حفظ بيانات جميع الأشخاص"""
        try:
            with open(self.people_file, 'w', encoding='utf-8') as f:
                json.dump(self.people_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات الأشخاص: {e}")

    def save_moderators_data(self):
        """حفظ قائمة المشرفين مع البيانات المتقدمة"""
        try:
            data = {
                "moderators": self.moderators_list,
                "room_moderators": self.room_moderators,
                "room_owner": self.room_owner,
                "room_king": self.room_king,
                "room_queen": self.room_queen,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.moderators_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 تم حفظ قائمة المشرفين: {len(self.moderators_list)} يدوي + {len(self.room_moderators)} من Highrise")
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات المشرفين: {e}")

    def load_vip_data(self):
        """تحميل قائمة VIP من الملف"""
        try:
            if os.path.exists(self.vip_file):
                with open(self.vip_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vip_users = data if isinstance(data, dict) else {}
                print(f"👑 تم تحميل {len(self.vip_users)} مستخدم VIP")
            else:
                os.makedirs("data", exist_ok=True)
                self.vip_users = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات VIP: {e}")
            self.vip_users = {}

    def save_vip_data(self):
        """حفظ قائمة VIP"""
        try:
            with open(self.vip_file, 'w', encoding='utf-8') as f:
                json.dump(self.vip_users, f, ensure_ascii=False, indent=2)
            print(f"💾 تم حفظ قائمة VIP: {len(self.vip_users)} مستخدم")
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات VIP: {e}")

    async def add_user_to_room(self, user: User, bot=None):
        """إضافة مستخدم عند دخول الغرفة مع فحص متقدم للصلاحيات"""
        user_id = user.id
        username = user.username
        current_time = datetime.now().isoformat()

        print(f"🔍 إضافة مستخدم للغرفة: {username} (ID: {user_id})")

        # فحص الصلاحيات المتقدم من إعدادات الغرفة إذا توفر البوت
        user_type = "visitor"  # افتراضي
        if bot:
            try:
                detected_type = await self.check_room_privileges_advanced(bot, user)
                user_type = detected_type
                print(f"🎯 تم التعرف على {username} كـ: {user_type}")
            except Exception as e:
                print(f"⚠️ فشل فحص الصلاحيات المتقدم لـ {username}: {e}")
                user_type = self.get_user_type_advanced(user)
        else:
            user_type = self.get_user_type_advanced(user)

        # تحديث البيانات الحية للمستخدمين النشطين
        if user_id in self.users:
            # مستخدم عائد للغرفة
            self.users[user_id].update({
                "username": username,
                "last_seen": current_time,
                "is_active": True,
                "user_type": user_type
            })
        else:
            # مستخدم جديد في الغرفة
            self.users[user_id] = {
                "username": username,
                "joined_at": current_time,
                "last_seen": current_time,
                "user_type": user_type,
                "is_active": True
            }

        # تحديث السجل التاريخي في people.json
        if user_id in self.people_data:
            # زيادة عدد الزيارات وتحديث آخر زيارة
            self.people_data[user_id].update({
                "username": username,
                "last_visit": current_time,
                "visit_count": self.people_data[user_id].get("visit_count", 0) + 1
            })
        else:
            # شخص جديد كلياً
            self.people_data[user_id] = {
                "username": username,
                "first_visit": current_time,
                "last_visit": current_time,
                "visit_count": 1,
                "user_type": self.get_user_type_advanced(user)
            }

        # حفظ البيانات
        self.save_users_data()
        self.save_people_data()

        # فحص الصلاحيات
        user_type = self.get_user_type_advanced(user)
        is_moderator = self.is_moderator_advanced(user)

        print(f"   📊 النتيجة: {username} - النوع: {user_type} - مشرف: {is_moderator}")

        return {
            "username": username,
            "user_id": user_id,
            "user_type": user_type,
            "is_moderator": is_moderator
        }

    def remove_user_from_room(self, user: User):
        """إزالة مستخدم عند الخروج من الغرفة"""
        user_id = user.id
        username = user.username
        current_time = datetime.now().isoformat()

        print(f"🚪 إزالة مستخدم من الغرفة: {username} (ID: {user_id})")

        # إزالة من البيانات الحية
        if user_id in self.users:
            del self.users[user_id]
            self.save_users_data()
            print(f"   ✅ تم حذف {username} من البيانات الحية")

        # تحديث آخر زيارة في السجل التاريخي
        if user_id in self.people_data:
            self.people_data[user_id]["last_visit"] = current_time
            self.save_people_data()

    async def check_room_privileges_advanced(self, bot, user: User):
        """
        فحص صلاحيات المستخدم من إعدادات الغرفة - النسخة المحسنة مع الاكتشاف التلقائي
        """
        try:
            # فحص المطور الأساسي أولاً
            if user.username == self.owner_username:
                print(f"🔱 تم التعرف على {user.username} كمطور البوت")
                return "bot_developer"

            # فحص قائمة مالكي الغرف المعروفين
            if user.username in self.known_room_owners:
                self.room_owner = user.id
                self.set_user_type_advanced(user.id, "room_owner")
                print(f"👑 تم التعرف على {user.username} كمالك الغرفة (قائمة معروفة)")
                return "room_owner"

            # الحصول على صلاحيات المستخدم من إعدادات الغرفة
            privileges_response = await bot.highrise.get_room_privilege(user.id)
            print(f"🔍 فحص صلاحيات {user.username} من إعدادات الغرفة: {privileges_response}")
            
            # التحقق من نوع الاستجابة
            if hasattr(privileges_response, '__class__') and privileges_response.__class__.__name__ == 'Error':
                print(f"⚠️ خطأ في الحصول على صلاحيات {user.username}: {privileges_response}")
                # استخدام النظام الاحتياطي
                return self.get_fallback_user_type(user)
            
            # إذا كانت الاستجابة من نوع RoomPermissions
            room_privileges = privileges_response

            # معالجة البيانات حسب نوع الإرجاع
            is_moderator = False
            is_designer = False
            is_owner = False

            if hasattr(room_privileges, 'moderator') and hasattr(room_privileges, 'designer'):
                # نوع RoomPermissions
                is_moderator = room_privileges.moderator
                is_designer = room_privileges.designer
                print(f"📊 تحليل صلاحيات {user.username}: مشرف={is_moderator}, مصمم={is_designer}")

            elif hasattr(room_privileges, 'privilege'):
                # نوع نص
                privilege = room_privileges.privilege
                if privilege == "owner":
                    is_owner = True
                elif privilege == "moderator":
                    is_moderator = True
                print(f"📊 صلاحية {user.username}: {privilege}")

            # متغير لتتبع إذا تم اكتشاف مشرف جديد
            new_moderator_detected = False

            # تحديد نوع المستخدم بناءً على البيانات
            if is_owner:
                self.room_owner = user.id
                self.set_user_type_advanced(user.id, "room_owner")
                print(f"👑 تم التعرف على {user.username} كمالك الغرفة (من Highrise)")
                
                # إضافة مالك الغرفة للقائمة اليدوية إذا لم يكن موجود
                if user.username not in self.moderators_list:
                    self.moderators_list.append(user.username)
                    self.save_moderators_data()
                    new_moderator_detected = True
                    print(f"✨ تم إضافة مالك الغرفة {user.username} تلقائياً للقائمة اليدوية")
                    
                    # إرسال رسالة تأكيد في الروم
                    try:
                        await bot.highrise.chat(f"👑 تم اكتشاف مالك الغرفة {user.username} وإضافته تلقائياً للمشرفين!")
                    except:
                        pass
                
                return "room_owner"

            elif is_moderator and is_designer:
                # مشرف ومصمم
                if user.id not in self.room_moderators:
                    self.room_moderators.append(user.id)
                    self.save_moderators_data()
                self.set_user_type_advanced(user.id, "moderator_designer")
                print(f"👮‍♂️🎨 تم التعرف على {user.username} كمشرف ومصمم")
                
                # إضافة للقائمة اليدوية إذا لم يكن موجود
                if user.username not in self.moderators_list:
                    self.moderators_list.append(user.username)
                    self.save_moderators_data()
                    new_moderator_detected = True
                    print(f"✨ تم إضافة المشرف المصمم {user.username} تلقائياً للقائمة اليدوية")
                    
                    # إرسال رسالة تأكيد في الروم
                    try:
                        await bot.highrise.chat(f"👮‍♂️🎨 تم اكتشاف مشرف ومصمم جديد {user.username} وإضافته تلقائياً!")
                    except:
                        pass
                
                return "moderator_designer"

            elif is_moderator:
                # مشرف فقط
                if user.id not in self.room_moderators:
                    self.room_moderators.append(user.id)
                    self.save_moderators_data()
                self.set_user_type_advanced(user.id, "moderator")
                print(f"👮‍♂️ تم التعرف على {user.username} كمشرف")
                
                # إضافة للقائمة اليدوية إذا لم يكن موجود - هنا الجزء المهم!
                if user.username not in self.moderators_list:
                    self.moderators_list.append(user.username)
                    self.save_moderators_data()
                    new_moderator_detected = True
                    print(f"✨ تم إضافة المشرف {user.username} تلقائياً للقائمة اليدوية")
                    
                    # إرسال رسالة تأكيد في الروم
                    try:
                        await bot.highrise.chat(f"👮‍♂️ تم اكتشاف مشرف جديد {user.username} وإضافته تلقائياً للقائمة!")
                    except:
                        pass
                
                return "moderator"

            elif is_designer:
                # مصمم فقط
                self.set_user_type_advanced(user.id, "designer")
                print(f"🎨 تم التعرف على {user.username} كمصمم")
                return "designer"

            # إذا لم يكن له أي صلاحيات خاصة، فهو زائر
            self.set_user_type_advanced(user.id, "visitor")
            print(f"👤 تم التعرف على {user.username} كزائر")
            return "visitor"

        except Exception as e:
            print(f"⚠️ خطأ في فحص صلاحيات {user.username}: {e}")

            # كحل احتياطي للمطور فقط
            if user.username == self.owner_username:
                print(f"🔧 حل احتياطي: {user.username} مطور البوت")
                return "bot_developer"

            # فحص قائمة المالكين المعروفين كحل احتياطي
            if user.username in self.known_room_owners:
                self.room_owner = user.id
                self.set_user_type_advanced(user.id, "room_owner")
                print(f"🔧 حل احتياطي: {user.username} مالك الغرفة")
                return "room_owner"

            # باقي المستخدمين يصبحوا زوار
            self.set_user_type_advanced(user.id, "visitor")
            print(f"🔧 حل احتياطي: {user.username} زائر")
            return "visitor"

    def get_fallback_user_type(self, user: User):
        """نظام احتياطي لتحديد نوع المستخدم عند فشل get_room_privilege"""
        # فحص المطور
        if user.username == self.owner_username:
            return "bot_developer"
        
        # فحص قائمة المالكين المعروفين
        if user.username in self.known_room_owners:
            self.room_owner = user.id
            self.set_user_type_advanced(user.id, "room_owner")
            return "room_owner"
        
        # فحص القائمة اليدوية للمشرفين
        if user.username in self.moderators_list:
            return "moderator"
        
        # المستخدم العادي
        return "visitor"

    async def batch_check_room_privileges(self, bot, users_list):
        """
        فحص صلاحيات مجموعة من المستخدمين دفعة واحدة
        """
        results = {}
        
        for user, _ in users_list:
            try:
                user_type = await self.check_room_privileges_advanced(bot, user)
                results[user.id] = {
                    "username": user.username,
                    "user_type": user_type,
                    "success": True
                }
                
                # تأخير صغير لتجنب الضغط على API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ خطأ في فحص صلاحيات {user.username}: {e}")
                results[user.id] = {
                    "username": user.username,
                    "user_type": self.get_fallback_user_type(user),
                    "success": False,
                    "error": str(e)
                }
        
        return results

    def get_user_type_advanced(self, user: User):
        """
        تحديد نوع المستخدم بناءً على النظام المتقدم
        """
        user_id = user.id

        # المطور الأساسي للبوت
        if user.username == self.owner_username:
            return "bot_developer"

        # الملك والملكة - أولوية عالية
        if self.room_king and user_id == self.room_king:
            return "room_king"

        if self.room_queen and user_id == self.room_queen:
            return "room_queen"

        # مالك الغرفة من إعدادات Highrise
        if self.room_owner and user_id == self.room_owner:
            return "room_owner"

        # مشرفي الغرفة من إعدادات Highrise
        if user_id in self.room_moderators:
            return "moderator"

        # مشرفي الغرفة من القائمة اليدوية
        if user.username in self.moderators_list:
            return "moderator"

        # التحقق من قاعدة البيانات للأنواع الأخرى
        user_data = self.get_user_info(user_id)
        if user_data:
            stored_type = user_data.get("user_type", "visitor")
            if stored_type in ["moderator_designer", "designer", "room_owner", "room_king", "room_queen"]:
                return stored_type

        # إذا لم يكن له أي صلاحيات، فهو زائر
        return "visitor"

    def is_moderator_advanced(self, user: User) -> bool:
        """التحقق من كون المستخدم مشرف - النسخة المتقدمة"""
        if not user:
            return False

        user_type = self.get_user_type_advanced(user)

        # جميع أنواع المشرفين
        moderator_types = [
            "bot_developer", "room_owner", "moderator", 
            "moderator_designer", "room_king", "room_queen"
        ]

        # فحص مباشر من قائمة المشرفين الحقيقية
        is_real_moderator = user.id in self.room_moderators
        is_manual_moderator = user.username in self.moderators_list

        return (user_type in moderator_types or is_real_moderator or is_manual_moderator)

    def check_permissions_advanced(self, user: User, required_permission: str):
        """
        فحص صلاحيات المستخدم - النسخة المتقدمة
        """
        user_type = self.get_user_type_advanced(user)

        print(f"🔍 فحص صلاحيات {user.username}: نوع المستخدم = {user_type}, الصلاحية المطلوبة = {required_permission}")

        # المطور له جميع الصلاحيات
        if user_type == "bot_developer":
            print(f"✅ {user.username} صلاحيات {required_permission}: True (مطور)")
            return True

        # صلاحيات المطور
        if required_permission == "developer":
            result = user_type == "bot_developer"
            print(f"{'✅' if result else '❌'} {user.username} صلاحيات المطور: {result}")
            return result

        # مالك الغرفة
        if required_permission == "owner":
            result = user_type in ["bot_developer", "room_owner"]
            print(f"{'✅' if result else '❌'} {user.username} صلاحيات المالك: {result}")
            return result

        # صلاحيات الإشراف
        if required_permission == "moderate":
            # فحص مباشر من قائمة المشرفين الحقيقية
            is_real_moderator = user.id in self.room_moderators
            is_manual_moderator = user.username in self.moderators_list

            result = (user_type in ["bot_developer", "room_owner", "moderator", "moderator_designer", "room_king", "room_queen"] 
                     or is_real_moderator or is_manual_moderator)

            print(f"{'✅' if result else '❌'} {user.username} صلاحيات الإشراف: {result}")
            print(f"  📋 في قائمة Highrise: {is_real_moderator}")
            print(f"  📝 في القائمة اليدوية: {is_manual_moderator}")
            print(f"  📊 نوع المستخدم: {user_type}")

            return result

        return False

    def set_user_type_advanced(self, user_id: str, user_type: str):
        """تحديد نوع المستخدم - النسخة المتقدمة"""
        if user_id in self.users:
            self.users[user_id]["user_type"] = user_type
            self.save_users_data()

        if user_id in self.people_data:
            self.people_data[user_id]["user_type"] = user_type
            self.save_people_data()

        return True

    def set_room_king(self, user_id: str):
        """تعيين ملك الغرفة"""
        self.room_king = user_id
        self.set_user_type_advanced(user_id, "room_king")
        self.save_moderators_data()
        return True

    def set_room_queen(self, user_id: str):
        """تعيين ملكة الغرفة"""
        self.room_queen = user_id
        self.set_user_type_advanced(user_id, "room_queen")
        self.save_moderators_data()
        return True

    def remove_room_king(self):
        """إزالة ملك الغرفة"""
        if self.room_king:
            self.set_user_type_advanced(self.room_king, "visitor")
        self.room_king = None
        self.save_moderators_data()
        return True

    def remove_room_queen(self):
        """إزالة ملكة الغرفة"""
        if self.room_queen:
            self.set_user_type_advanced(self.room_queen, "visitor")
        self.room_queen = None
        self.save_moderators_data()
        return True

    def get_permission_text_advanced(self, user: User):
        """نص الصلاحيات للمستخدم - النسخة المتقدمة"""
        user_type = self.get_user_type_advanced(user)

        permissions_text = {
            "visitor": "👤 زائر",
            "designer": "🎨 مصمم الغرفة",
            "moderator": "👮‍♂️ مشرف الغرفة", 
            "moderator_designer": "👮‍♂️🎨 مشرف ومصمم",
            "room_owner": "👑 مالك الغرفة",
            "room_king": "🤴 ملك الغرفة",
            "room_queen": "👸 ملكة الغرفة",
            "bot_developer": "🔱 مطور البوت"
        }

        return permissions_text.get(user_type, "👤 زائر")

    def get_all_moderators_advanced(self):
        """الحصول على قائمة جميع المشرفين - النسخة المتقدمة"""
        moderators_info = []

        # مشرفي الغرفة من إعدادات Highrise
        for mod_id in self.room_moderators:
            user_data = self.get_user_info(mod_id)
            if user_data:
                moderators_info.append({
                    "user_id": mod_id,
                    "username": user_data.get("username", "غير معروف"),
                    "user_type": user_data.get("user_type", "moderator"),
                    "source": "highrise_settings"
                })

        # المشرفين من القائمة اليدوية
        for username in self.moderators_list:
            # البحث عن معرف المستخدم
            user_id = None
            for uid, data in self.people_data.items():
                if data.get("username") == username:
                    user_id = uid
                    break

            moderators_info.append({
                "user_id": user_id or "unknown",
                "username": username,
                "user_type": "moderator",
                "source": "manual_list"
            })

        return moderators_info

    # الحفاظ على التوافق مع النظام القديم
    async def check_user_on_join(self, user: User, bot=None):
        """فحص المستخدم عند الدخول مع الفحص المتقدم"""
        return await self.add_user_to_room(user, bot)

    def add_user(self, user: User):
        """إضافة مستخدم جديد (للتوافق مع النظام القديم)"""
        return self.add_user_to_room(user)

    def remove_user(self, user: User):
        """إزالة مستخدم عند الخروج (للتوافق مع النظام القديم)"""
        self.remove_user_from_room(user)

    def is_moderator(self, username: str) -> bool:
        """التحقق من كون المستخدم مشرف (للتوافق مع النظام القديم)"""
        if not username:
            return False
        return username in self.moderators_list

    def is_owner(self, username: str) -> bool:
        """التحقق من كون المستخدم صاحب البوت"""
        return username == self.owner_username

    def is_developer(self, username: str) -> bool:
        """التحقق من كون المستخدم مطور"""
        return username == self.owner_username

    def is_owner_by_id(self, user_id: str) -> bool:
        """التحقق من كون المستخدم صاحب البوت بالمعرف"""
        return user_id == self.owner_id

    def is_bot(self, user_id: str) -> bool:
        """التحقق من كون المستخدم هو البوت نفسه"""
        return user_id == self.bot_id

    def get_user_type(self, username: str, user_id: str = None) -> str:
        """تحديد نوع المستخدم (للتوافق مع النظام القديم)"""
        # التحقق من فريق EDX أولاً
        try:
            from modules.edx_team_manager import edx_manager
            if edx_manager.is_edx_member(username):
                member_info = edx_manager.get_member_info(username)
                if member_info and member_info.get("level", 0) >= 999:
                    return "edx_founder"
                else:
                    return "edx_developer"
        except:
            pass
        
        if user_id == self.owner_id or username == self.owner_username:
            return "owner"
        elif username == self.room_king:
            return "room_king"
        elif username in self.moderators_list:
            return "moderator"
        else:
            return "user"

    def get_user_emoji(self, username: str) -> str:
        """الحصول على إيموجي حسب نوع المستخدم"""
        user_type = self.get_user_type(username)
        emojis = {
            "edx_founder": "🏆",
            "edx_developer": "💎",
            "owner": "👑",
            "room_king": "🔱",
            "moderator": "👮‍♂️",
            "user": "👤",
            "bot_developer": "🔱",
            "room_owner": "👑",
            "room_queen": "👸",
            "moderator_designer": "👮‍♂️🎨",
            "designer": "🎨",
            "visitor": "👤"
        }
        return emojis.get(user_type, "👤")

    def add_moderator(self, username: str) -> str:
        """إضافة مشرف جديد"""
        try:
            if not username:
                return "❌ اسم المستخدم مطلوب"

            if username in self.moderators_list:
                return f"❌ {username} مشرف بالفعل"

            # إضافة للقائمة
            self.moderators_list.append(username)

            # تحديث نوع المستخدم في البيانات الحية
            for user_id, user_data in self.users.items():
                if user_data.get("username") == username:
                    user_data["user_type"] = "moderator"
                    break

            # تحديث نوع المستخدم في السجل التاريخي
            for user_id, user_data in self.people_data.items():
                if user_data.get("username") == username:
                    user_data["user_type"] = "moderator"
                    break

            # حفظ البيانات
            self.save_moderators_data()
            self.save_users_data()
            self.save_people_data()

            print(f"✅ تم إضافة {username} كمشرف")
            return f"✅ تم تعيين {username} كمشرف بنجاح"

        except Exception as e:
            return f"❌ خطأ في إضافة المشرف: {str(e)}"

    def remove_moderator(self, username: str) -> str:
        """إزالة مشرف"""
        try:
            if not username:
                return "❌ اسم المستخدم مطلوب"

            if username == self.owner_username:
                return "❌ لا يمكن إزالة صاحب البوت"

            if username == self.room_king:
                return "❌ لا يمكن إزالة صاحب الروم"

            if username not in self.moderators_list:
                return f"❌ {username} ليس مشرفاً"

            # إزالة من القائمة
            self.moderators_list.remove(username)

            # تحديث نوع المستخدم في البيانات الحية
            for user_id, user_data in self.users.items():
                if user_data.get("username") == username:
                    user_data["user_type"] = "user"
                    break

            # تحديث نوع المستخدم في السجل التاريخي
            for user_id, user_data in self.people_data.items():
                if user_data.get("username") == username:
                    user_data["user_type"] = "user"
                    break

            # حفظ البيانات
            self.save_moderators_data()
            self.save_users_data()
            self.save_people_data()

            return f"✅ تم إزالة {username} من المشرفين بنجاح"

        except Exception as e:
            return f"❌ خطأ في إزالة المشرف: {str(e)}"

    def get_user_permissions_info(self, username: str) -> str:
        """معلومات صلاحيات المستخدم"""
        try:
            is_owner = self.is_owner(username)
            is_moderator = self.is_moderator(username)
            user_type = self.get_user_type(username)
            emoji = self.get_user_emoji(username)

            info = f"{emoji} معلومات المستخدم {username}:\n"
            info += f"🏷️ النوع: {user_type}\n"

            if is_owner:
                info += "👑 مالك البوت - كل الصلاحيات متاحة\n"
                info += "✅ إدارة المشرفين\n"
                info += "✅ جميع أوامر البوت"
            elif is_moderator:
                info += "👮‍♂️ مشرف - صلاحيات محدودة\n"
                info += "✅ أوامر الإدارة\n"
                info += "✅ إدارة المستخدمين\n"
                info += "❌ لا يمكن إدارة المشرفين"
            else:
                info += "👤 مستخدم عادي\n"
                info += "✅ الأوامر العامة فقط\n"
                info += "❌ لا يمكن استخدام أوامر الإدارة"

            return info

        except Exception as e:
            print(f"خطأ في get_user_permissions_info: {e}")
            return f"❌ خطأ في فحص صلاحيات المستخدم {username}: {str(e)}"

    def get_room_statistics(self) -> str:
        """الحصول على إحصائيات الغرفة"""
        active_count = len(self.users)  # المستخدمين النشطين في الغرفة
        total_people_count = len(self.people_data)  # إجمالي من دخل الغرفة

        stats = [
            "📊 إحصائيات الغرفة:",
            f"🟢 المستخدمين في الغرفة الآن: {active_count}",
            f"👥 إجمالي من دخل الغرفة: {total_people_count}",
            f"👮‍♂️ المشرفين اليدويين: {len(self.moderators_list)}",
            f"👮‍♂️ مشرفي Highrise: {len(self.room_moderators)}",
            f"👑 مالك الغرفة: {'نعم' if self.room_owner else 'لا'}",
            f"🤴 ملك الغرفة: {'نعم' if self.room_king else 'لا'}",
            f"👸 ملكة الغرفة: {'نعم' if self.room_queen else 'لا'}"
        ]
        return "\n".join(stats)

    def get_moderators_list(self) -> list:
        """الحصول على قائمة المشرفين"""
        return self.moderators_list.copy()

    def get_user_info_from_people(self, username: str) -> dict:
        """الحصول على معلومات المستخدم من السجل التاريخي"""
        for user_id, user_data in self.people_data.items():
            if user_data.get("username") == username:
                return user_data
        return None

    def get_user_info(self, username: str) -> dict:
        """الحصول على معلومات المستخدم من البيانات الحية"""
        for user_id, user_data in self.users.items():
            if user_data.get("username") == username:
                return user_data
        return None

    def is_user_in_room(self, username: str) -> bool:
        """التحقق من وجود المستخدم في الغرفة حالياً"""
        for user_data in self.users.values():
            if user_data.get("username") == username:
                return True
        return False

    def add_moderator(self, username: str) -> str:
        """إضافة مشرف جديد"""
        try:
            # التأكد من أن username هو نص وليس كائن
            if not isinstance(username, str):
                print(f"❌ خطأ: username ليس نص، نوعه: {type(username)}")
                return "❌ خطأ في نوع البيانات"

            if not username or username.strip() == "":
                return "❌ اسم المستخدم مطلوب"

            # تنظيف اسم المستخدم
            clean_username = username.strip()

            if clean_username in self.moderators_list:
                return f"❌ {clean_username} مشرف بالفعل"

            # إضافة للقائمة
            self.moderators_list.append(clean_username)

            # تحديث نوع المستخدم في البيانات الحية
            for user_id, user_data in self.users.items():
                if isinstance(user_data, dict) and user_data.get("username") == clean_username:
                    user_data["user_type"] = "moderator"
                    break

            # تحديث نوع المستخدم في السجل التاريخي
            for user_id, user_data in self.people_data.items():
                if isinstance(user_data, dict) and user_data.get("username") == clean_username:
                    user_data["user_type"] = "moderator"
                    break

            # حفظ البيانات
            self.save_moderators_data()
            self.save_users_data()
            self.save_people_data()

            print(f"✅ تم إضافة {clean_username} كمشرف")
            return f"✅ تم تعيين {clean_username} كمشرف بنجاح"

        except Exception as e:
            print(f"❌ خطأ في إضافة المشرف: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ خطأ في إضافة المشرف: {str(e)}"

    def remove_moderator(self, username: str) -> str:
        """إزالة مشرف"""
        try:
            # التأكد من أن username هو نص وليس كائن
            if not isinstance(username, str):
                print(f"❌ خطأ: username ليس نص، نوعه: {type(username)}")
                return "❌ خطأ في نوع البيانات"

            if not username or username.strip() == "":
                return "❌ اسم المستخدم مطلوب"

            # تنظيف اسم المستخدم
            clean_username = username.strip()

            if clean_username == self.owner_username:
                return "❌ لا يمكن إزالة صاحب البوت"

            if hasattr(self, 'room_king') and clean_username == self.room_king:
                return "❌ لا يمكن إزالة صاحب الروم"

            if clean_username not in self.moderators_list:
                return f"❌ {clean_username} ليس مشرفاً"

            # إزالة من القائمة
            self.moderators_list.remove(clean_username)

            # تحديث نوع المستخدم في البيانات الحية
            for user_id, user_data in self.users.items():
                if isinstance(user_data, dict) and user_data.get("username") == clean_username:
                    user_data["user_type"] = "visitor"
                    break

            # تحديث نوع المستخدم في السجل التاريخي
            for user_id, user_data in self.people_data.items():
                if isinstance(user_data, dict) and user_data.get("username") == clean_username:
                    user_data["user_type"] = "visitor"
                    break

            # حفظ البيانات
            self.save_moderators_data()
            self.save_users_data()
            self.save_people_data()

            print(f"✅ تم إزالة {clean_username} من المشرفين")
            return f"✅ تم إزالة {clean_username} من المشرفين بنجاح"

        except Exception as e:
            print(f"❌ خطأ في إزالة المشرف: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ خطأ في إزالة المشرف: {str(e)}"

    def get_user_stats(self, username: str) -> str:
        """الحصول على إحصائيات المستخدم"""
        # معلومات من السجل التاريخي
        people_info = self.get_user_info_from_people(username)
        # معلومات من البيانات الحية
        current_info = self.get_user_info(username)

        if not people_info:
            return f"❌ لم يتم العثور على بيانات للمستخدم {username}"

        user_type = self.get_user_type(username)
        emoji = self.get_user_emoji(username)

        stats = [
            f"{emoji} معلومات {username}:",
            f"📊 عدد الزيارات: {people_info.get('visit_count', 0)}",
            f"📅 أول زيارة: {people_info.get('first_visit', 'غير محدد')[:10]}",
            f"🕐 آخر زيارة: {people_info.get('last_visit', 'غير محدد')[:10]}",
            f"🏷️ النوع: {user_type}",
            f"🟢 في الغرفة الآن: {'نعم' if current_info else 'لا'}"
        ]

        return "\n".join(stats)

    def get_active_users_count(self) -> int:
        """عدد المستخدمين النشطين في الغرفة"""
        return len(self.users)

    def get_total_users_count(self) -> int:
        """إجمالي عدد الأشخاص الذين دخلوا الغرفة"""
        return len(self.people_data)

    async def sync_with_room_users(self, room_users_list, bot=None):
        """مزامنة البيانات مع قائمة المستخدمين الفعلية في الغرفة مع فحص متقدم"""
        current_user_ids = set(self.users.keys())
        actual_user_ids = set()
        updated_users = 0

        # إضافة وتحديث المستخدمين
        for user, _ in room_users_list:
            actual_user_ids.add(user.id)
            if user.id not in self.users:
                print(f"🔄 مزامنة: إضافة مستخدم جديد {user.username}")
                await self.add_user_to_room(user, bot)
                updated_users += 1
            else:
                # تحديث الصلاحيات للمستخدمين الموجودين
                if bot and updated_users < 5:  # تحديد عدد المستخدمين للفحص لتجنب الضغط على API
                    try:
                        old_type = self.users[user.id].get("user_type", "visitor")
                        new_type = await self.check_room_privileges_advanced(bot, user)
                        if old_type != new_type:
                            self.users[user.id]["user_type"] = new_type
                            print(f"🔄 تحديث صلاحيات {user.username}: {old_type} → {new_type}")
                            updated_users += 1
                    except Exception as e:
                        print(f"⚠️ خطأ في تحديث صلاحيات {user.username}: {e}")

        # إزالة المستخدمين الذين خرجوا
        users_to_remove = current_user_ids - actual_user_ids
        for user_id in users_to_remove:
            if user_id in self.users:
                username = self.users[user_id].get("username", "مجهول")
                print(f"🔄 مزامنة: إزالة مستخدم {username}")
                del self.users[user_id]

        if users_to_remove or updated_users > 0:
            self.save_users_data()

        print(f"✅ مزامنة مكتملة: {len(actual_user_ids)} مستخدم في الغرفة، {updated_users} تحديث صلاحيات")

    async def monitor_privilege_changes(self, bot):
        """
        مراقبة تغييرات الصلاحيات للمستخدمين الموجودين
        """
        try:
            room_users = await bot.highrise.get_room_users()
            changes_detected = []
            
            for user, _ in room_users.content:
                if user.id in self.users:
                    try:
                        # فحص الصلاحيات الحالية
                        privileges = await bot.highrise.get_room_privilege(user.id)
                        current_type = self.users[user.id].get("user_type", "visitor")
                        new_type = await self.check_room_privileges_advanced(bot, user)
                        
                        if current_type != new_type:
                            changes_detected.append({
                                "username": user.username,
                                "old_type": current_type,
                                "new_type": new_type,
                                "privileges": str(privileges)
                            })
                            
                            # تحديث نوع المستخدم
                            self.users[user.id]["user_type"] = new_type
                            print(f"🔄 تغيير صلاحيات {user.username}: {current_type} → {new_type}")
                        
                        # تأخير قصير
                        await asyncio.sleep(0.2)
                        
                    except Exception as e:
                        print(f"⚠️ خطأ في مراقبة صلاحيات {user.username}: {e}")
                        continue
            
            if changes_detected:
                self.save_users_data()
                return changes_detected
            
            return []
            
        except Exception as e:
            print(f"❌ خطأ في مراقبة تغييرات الصلاحيات: {e}")
            return []

    async def auto_detect_and_add_moderators(self, bot):
        """
        فحص تلقائي لجميع المستخدمين في الغرفة واكتشاف المشرفين غير المضافين
        """
        try:
            print("🔍 بدء الفحص التلقائي لاكتشاف المشرفين...")
            
            room_users = await bot.highrise.get_room_users()
            newly_detected = []
            
            for user, _ in room_users.content:
                # تجنب فحص البوت نفسه
                if user.id == self.bot_id:
                    continue
                    
                try:
                    # فحص صلاحيات المستخدم من Highrise
                    privileges = await bot.highrise.get_room_privilege(user.id)
                    
                    # تحليل الصلاحيات
                    is_moderator = False
                    is_designer = False
                    is_owner = False
                    
                    if hasattr(privileges, 'moderator') and hasattr(privileges, 'designer'):
                        is_moderator = privileges.moderator
                        is_designer = privileges.designer
                    elif hasattr(privileges, 'privilege'):
                        if privileges.privilege == "owner":
                            is_owner = True
                        elif privileges.privilege == "moderator":
                            is_moderator = True
                    
                    # إذا كان المستخدم مشرف أو مالك وغير موجود في القائمة اليدوية
                    if (is_moderator or is_owner or is_designer) and user.username not in self.moderators_list:
                        # إضافة للقائمة اليدوية
                        self.moderators_list.append(user.username)
                        
                        # إضافة للقائمة الفنية أيضاً
                        if user.id not in self.room_moderators:
                            self.room_moderators.append(user.id)
                        
                        # تحديد نوع المشرف
                        mod_type = "مالك الغرفة" if is_owner else "مشرف ومصمم" if (is_moderator and is_designer) else "مشرف"
                        
                        newly_detected.append({
                            "username": user.username,
                            "user_id": user.id,
                            "type": mod_type,
                            "is_owner": is_owner,
                            "is_moderator": is_moderator,
                            "is_designer": is_designer
                        })
                        
                        print(f"✨ تم اكتشاف {mod_type} جديد: {user.username}")
                    
                    # تأخير صغير لتجنب الضغط على API
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"⚠️ خطأ في فحص صلاحيات {user.username}: {e}")
                    continue
            
            # حفظ التحديثات إذا تم اكتشاف مشرفين جدد
            if newly_detected:
                self.save_moderators_data()
                self.save_users_data()
                
                # إرسال رسالة تأكيد في الروم
                if len(newly_detected) == 1:
                    mod = newly_detected[0]
                    await bot.highrise.chat(f"🎯 تم اكتشاف {mod['type']} جديد: {mod['username']} وإضافته تلقائياً!")
                else:
                    await bot.highrise.chat(f"🎯 تم اكتشاف {len(newly_detected)} مشرف جديد وإضافتهم تلقائياً!")
                
                # طباعة تقرير مفصل
                print(f"📊 تقرير الاكتشاف التلقائي:")
                print(f"   🔍 تم فحص {len(room_users.content)} مستخدم")
                print(f"   ✨ تم اكتشاف {len(newly_detected)} مشرف جديد")
                for mod in newly_detected:
                    print(f"   📋 {mod['type']}: {mod['username']}")
            else:
                print("✅ الفحص التلقائي مكتمل - لا يوجد مشرفين جدد")
            
            return newly_detected
            
        except Exception as e:
            print(f"❌ خطأ في الفحص التلقائي للمشرفين: {e}")
            return []

    def log_privilege_change(self, user_id: str, username: str, old_type: str, new_type: str, privileges_data: str):
        """
        تسجيل تغييرات الصلاحيات في ملف منفصل
        """
        try:
            import os
            from datetime import datetime
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "username": username,
                "old_type": old_type,
                "new_type": new_type,
                "privileges": privileges_data,
                "change_reason": "automatic_detection"
            }
            
            log_file = "data/privilege_changes.json"
            logs = []
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            # الاحتفاظ بآخر 100 تغيير فقط
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
            print(f"📝 تم تسجيل تغيير صلاحيات {username}")
            
        except Exception as e:
            print(f"❌ خطأ في تسجيل تغيير الصلاحيات: {e}")

    def is_vip(self, user_id: str) -> bool:
        """التحقق من كون المستخدم VIP"""
        return user_id in self.vip_users

    def add_vip(self, username: str, user_id: str = None) -> str:
        """إضافة مستخدم VIP جديد"""
        try:
            if not username:
                return "❌ اسم المستخدم مطلوب"

            # البحث عن معرف المستخدم إذا لم يتم توفيره
            if not user_id:
                # البحث في البيانات الحية
                for uid, user_data in self.users.items():
                    if user_data.get("username", "").lower() == username.lower():
                        user_id = uid
                        break

                # البحث في السجل التاريخي
                if not user_id:
                    for uid, user_data in self.people_data.items():
                        if user_data.get("username", "").lower() == username.lower():
                            user_id = uid
                            break

            if not user_id:
                return f"❌ لم يتم العثور على معرف المستخدم '{username}'"

            if user_id in self.vip_users:
                return f"❌ {username} مستخدم VIP بالفعل"

            # إضافة للقائمة
            self.vip_users[user_id] = {
                "username": username,
                "added_at": datetime.now().isoformat(),
                "status": "active"
            }

            # تحديث نوع المستخدم في البيانات
            if user_id in self.users:
                self.users[user_id]["is_vip"] = True

            if user_id in self.people_data:
                self.people_data[user_id]["is_vip"] = True

            # حفظ البيانات
            self.save_vip_data()
            self.save_users_data()
            self.save_people_data()

            print(f"✅ تم إضافة {username} كمستخدم VIP")
            return f"✅ تم تعيين {username} كمستخدم VIP بنجاح"

        except Exception as e:
            print(f"❌ خطأ في إضافة VIP: {e}")
            return f"❌ خطأ في إضافة VIP: {str(e)}"

    def remove_vip(self, username: str, user_id: str = None) -> str:
        """إزالة مستخدم VIP"""
        try:
            if not username:
                return "❌ اسم المستخدم مطلوب"

            # البحث عن معرف المستخدم إذا لم يتم توفيره
            if not user_id:
                # البحث في قائمة VIP أولاً
                for uid, vip_data in self.vip_users.items():
                    if vip_data.get("username", "").lower() == username.lower():
                        user_id = uid
                        break

                # البحث في البيانات الحية
                if not user_id:
                    for uid, user_data in self.users.items():
                        if user_data.get("username", "").lower() == username.lower():
                            user_id = uid
                            break

            if not user_id:
                return f"❌ لم يتم العثور على المستخدم '{username}'"

            if user_id not in self.vip_users:
                return f"❌ {username} ليس مستخدم VIP"

            # إزالة من القائمة
            del self.vip_users[user_id]

            # تحديث البيانات
            if user_id in self.users:
                self.users[user_id]["is_vip"] = False

            if user_id in self.people_data:
                self.people_data[user_id]["is_vip"] = False

            # حفظ البيانات
            self.save_vip_data()
            self.save_users_data()
            self.save_people_data()

            print(f"✅ تم إزالة {username} من VIP")
            return f"✅ تم إزالة {username} من قائمة VIP بنجاح"

        except Exception as e:
            print(f"❌ خطأ في إزالة VIP: {e}")
            return f"❌ خطأ في إزالة VIP: {str(e)}"

    def get_vip_list(self) -> str:
        """الحصول على قائمة مستخدمي VIP"""
        try:
            if not self.vip_users:
                return "👑 لا يوجد مستخدمين VIP حالياً"

            vip_list = []
            active_count = 0

            for user_id, vip_data in self.vip_users.items():
                username = vip_data.get("username", "غير معروف")
                status = vip_data.get("status", "active")
                
                if status == "active":
                    vip_list.append(username)
                    active_count += 1

            if not vip_list:
                return "👑 لا يوجد مستخدمين VIP نشطين حالياً"

            users_text = " | ".join(vip_list[:15])
            result = f"👑 قائمة مستخدمي VIP ({active_count}): {users_text}"
            
            if len(vip_list) > 15:
                result += f" + {len(vip_list) - 15} آخرين"

            return result

        except Exception as e:
            return f"❌ خطأ في عرض قائمة VIP: {str(e)}"

    def get_vip_info(self, username: str) -> str:
        """الحصول على معلومات VIP للمستخدم"""
        try:
            # البحث عن المستخدم
            user_id = None
            for uid, vip_data in self.vip_users.items():
                if vip_data.get("username", "").lower() == username.lower():
                    user_id = uid
                    break

            if not user_id:
                return f"❌ {username} ليس مستخدم VIP"

            vip_data = self.vip_users[user_id]
            added_date = vip_data.get("added_at", "غير محدد")[:10]
            status = vip_data.get("status", "active")

            result = f"👑 معلومات VIP لـ {username}:\n"
            result += f"📅 تاريخ الإضافة: {added_date}\n"
            result += f"📊 الحالة: {status}\n"
            result += f"🔑 المعرف: {user_id[:8]}..."

            return result

        except Exception as e:
            return f"❌ خطأ في عرض معلومات VIP: {str(e)}"