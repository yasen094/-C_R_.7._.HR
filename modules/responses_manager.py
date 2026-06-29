
"""
مدير الردود التلقائية - نظام إدارة الردود الترحيبية والوداعية
"""
import json
import os
import random
from datetime import datetime

class ResponsesManager:
    def __init__(self):
        self.responses_file = "data/responses_data.json"
        self.responses_data = self.load_responses()
    
    def load_responses(self):
        """تحميل بيانات الردود من الملف"""
        try:
            if os.path.exists(self.responses_file):
                with open(self.responses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_responses()
        except Exception as e:
            print(f"❌ خطأ في تحميل الردود: {e}")
            return self.get_default_responses()
    
    def get_default_responses(self):
        """الحصول على الردود الافتراضية"""
        return {
            "welcome_responses": {
                "user": ["🤗 أهلاً وسهلاً بك {username}! 😊"],
                "moderator": ["👮‍♂️ أهلاً بالمشرف {username}! منور الغرفة"],
                "bot_developer": ["🔱 مرحباً بالمطور {username}! أهلاً وسهلاً"],
                "room_owner": ["👑 أهلاً بمالك الغرفة {username}! منور البيت"],
                "room_king": ["🤴 أهلاً بملك الغرفة {username}! نورت المملكة"],
                "room_queen": ["👸 أهلاً بملكة الغرفة {username}! نورتِ المملكة"]
            },
            "farewell_messages": {
                "user": [
                    "👋 وداعاً {username}! كان من الممتع وجودك معنا",
                    "🚪 {username} غادر الغرفة. نراك قريباً!",
                    "👋 إلى اللقاء {username}! اهتم بنفسك"
                ],
                "moderator": [
                    "👮‍♂️ وداعاً المشرف {username}! شكراً لك على خدمتك",
                    "👋 إلى اللقاء {username}! الغرفة ستفتقدك"
                ],
                "bot_developer": [
                    "🔱 وداعاً المطور {username}! عودة موفقة",
                    "👋 إلى اللقاء {username}! شكراً لك على كل شيء"
                ],
                "room_owner": [
                    "👑 وداعاً مالك الغرفة {username}! عودة قريبة",
                    "👋 إلى اللقاء {username}! البيت بيتك دائماً"
                ],
                "room_king": [
                    "🤴 وداعاً جلالة الملك {username}! عودة موفقة للمملكة"
                ],
                "room_queen": [
                    "👸 وداعاً جلالة الملكة {username}! عودة موفقة للمملكة"
                ]
            },
            "settings": {
                "welcome_enabled": True,
                "farewell_enabled": True,
                "random_selection": True
            }
        }
    
    def save_responses(self):
        """حفظ بيانات الردود"""
        try:
            os.makedirs(os.path.dirname(self.responses_file), exist_ok=True)
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(self.responses_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الردود: {e}")
            return False
    
    def get_welcome_message(self, username, user_type, visit_info=None):
        """الحصول على رسالة ترحيب حسب نوع المستخدم"""
        if not self.responses_data.get("settings", {}).get("welcome_enabled", True):
            return None
        
        # تحديد نوع الرسالة حسب حالة الزيارة
        if visit_info:
            if visit_info.get("visit_count", 1) == 1:
                messages = self.responses_data.get("special_messages", {}).get("first_visit", [])
            elif visit_info.get("visit_count", 1) > 10:
                messages = self.responses_data.get("special_messages", {}).get("frequent_visitor", [])
            else:
                messages = self.responses_data.get("special_messages", {}).get("return_visit", [])
            
            if messages:
                message = self._select_message(messages)
                return message.format(username=username)
        
        # الحصول على رسالة حسب نوع المستخدم
        user_messages = self.responses_data.get("welcome_responses", {}).get(user_type, [])
        
        if not user_messages:
            # استخدام رسائل المستخدم العادي كاحتياطي
            user_messages = self.responses_data.get("welcome_responses", {}).get("user", [])
        
        if user_messages:
            message = self._select_message(user_messages)
            return message.format(username=username)
        
        return None
    
    def get_farewell_message(self, username, user_type):
        """الحصول على رسالة وداع حسب نوع المستخدم"""
        if not self.responses_data.get("settings", {}).get("farewell_enabled", True):
            return None
        
        user_messages = self.responses_data.get("farewell_messages", {}).get(user_type, [])
        
        if not user_messages:
            # استخدام رسائل المستخدم العادي كاحتياطي
            user_messages = self.responses_data.get("farewell_messages", {}).get("user", [])
        
        if user_messages:
            message = self._select_message(user_messages)
            return message.format(username=username)
        
        return None
    
    def get_reaction_message(self, reaction_type):
        """الحصول على رسالة لإرسال التفاعلات"""
        reaction_messages = self.responses_data.get("reaction_messages", {}).get(reaction_type, [])
        
        if reaction_messages:
            return self._select_message(reaction_messages)
        
        return None
    
    def _select_message(self, messages):
        """اختيار رسالة من القائمة"""
        if not messages:
            return None
        
        if self.responses_data.get("settings", {}).get("random_selection", True):
            return random.choice(messages)
        else:
            return messages[0]
    
    def add_welcome_message(self, user_type, message):
        """إضافة رسالة ترحيب جديدة"""
        if "welcome_responses" not in self.responses_data:
            self.responses_data["welcome_responses"] = {}
        
        # التأكد من أن نوع المستخدم صحيح
        valid_user_types = ['user', 'moderator', 'bot_developer', 'vip_user']
        if user_type not in valid_user_types:
            print(f"⚠️ نوع مستخدم غير معروف: {user_type}")
            return False
        
        if user_type not in self.responses_data["welcome_responses"]:
            self.responses_data["welcome_responses"][user_type] = []
        
        # التأكد من عدم تكرار الرسالة
        if message not in self.responses_data["welcome_responses"][user_type]:
            self.responses_data["welcome_responses"][user_type].append(message)
            print(f"✅ تم إضافة رسالة جديدة لـ {user_type}: {message}")
            return self.save_responses()
        else:
            print(f"⚠️ الرسالة موجودة مسبقاً لـ {user_type}")
            return False
    
    def add_farewell_message(self, user_type, message):
        """إضافة رسالة وداع جديدة"""
        if "farewell_messages" not in self.responses_data:
            self.responses_data["farewell_messages"] = {}
        
        # أنواع المستخدمين المسموحة لرسائل الوداع
        valid_user_types = ['user', 'moderator', 'bot_developer', 'room_owner', 'room_king', 'room_queen', 'vip_user']
        if user_type not in valid_user_types:
            print(f"⚠️ نوع مستخدم غير معروف: {user_type}")
            return False
        
        if user_type not in self.responses_data["farewell_messages"]:
            self.responses_data["farewell_messages"][user_type] = []
        
        # التأكد من عدم تكرار الرسالة
        if message not in self.responses_data["farewell_messages"][user_type]:
            self.responses_data["farewell_messages"][user_type].append(message)
            print(f"✅ تم إضافة رسالة وداع جديدة لـ {user_type}: {message}")
            return self.save_responses()
        else:
            print(f"⚠️ رسالة الوداع موجودة مسبقاً لـ {user_type}")
            return False
    
    def remove_welcome_message(self, user_type, message):
        """حذف رسالة ترحيب"""
        try:
            if user_type in self.responses_data.get("welcome_responses", {}):
                if message in self.responses_data["welcome_responses"][user_type]:
                    self.responses_data["welcome_responses"][user_type].remove(message)
                    return self.save_responses()
            return False
        except Exception:
            return False
    
    def remove_farewell_message(self, user_type, message):
        """حذف رسالة وداع"""
        try:
            if user_type in self.responses_data.get("farewell_messages", {}):
                if message in self.responses_data["farewell_messages"][user_type]:
                    self.responses_data["farewell_messages"][user_type].remove(message)
                    return self.save_responses()
            return False
        except Exception:
            return False
    
    def get_all_responses(self):
        """الحصول على جميع الردود"""
        return self.responses_data
    
    def update_settings(self, settings):
        """تحديث إعدادات الردود"""
        if "settings" not in self.responses_data:
            self.responses_data["settings"] = {}
        
        self.responses_data["settings"].update(settings)
        return self.save_responses()
    
    def toggle_welcome(self):
        """تفعيل/إيقاف الردود الترحيبية"""
        current = self.responses_data.get("settings", {}).get("welcome_enabled", True)
        self.responses_data.setdefault("settings", {})["welcome_enabled"] = not current
        self.save_responses()
        return not current
    
    def toggle_farewell(self):
        """تفعيل/إيقاف الردود الوداعية"""
        current = self.responses_data.get("settings", {}).get("farewell_enabled", True)
        self.responses_data.setdefault("settings", {})["farewell_enabled"] = not current
        self.save_responses()
        return not current

# إنشاء مثيل عام للاستخدام
responses_manager = ResponsesManager()
