"""
🏆 مدير فريق EDX - نظام صلاحيات محمي
من تطوير فريق EDX المصري

هذا الملف محمي ولا يمكن تعديله إلا من قبل أعضاء فريق EDX
"""

import json
import os
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any

class EDXTeamManager:
    def __init__(self):
        self.config_file = "data/edx_team_config.json"
        self.team_data = self.load_team_config()
        self.protection_enabled = True

    def load_team_config(self) -> Dict[str, Any]:
        """تحميل تكوين فريق EDX مع الحماية"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # التحقق من سلامة الملف
                    if self.verify_file_integrity(data):
                        return data
                    else:
                        print("⚠️ تحذير: ملف فريق EDX قد تم العبث به!")
                        return self.create_default_config()
            else:
                return self.create_default_config()
        except Exception as e:
            print(f"❌ خطأ في تحميل تكوين فريق EDX: {e}")
            return self.create_default_config()

    def create_default_config(self) -> Dict[str, Any]:
        """إنشاء التكوين الافتراضي لفريق EDX مع تشفير الأسماء"""
        # أسماء مشفرة بـ base64 لحماية إضافية
        encrypted_members = {
            base64.b64encode("VECTOR000".encode()).decode(): {
                "role": "مؤسس الفريق", 
                "level": 999, 
                "badge": "👑",
                "encrypted": True
            },
            base64.b64encode("A.OPY".encode()).decode(): {
                "role": "مطور رئيسي", 
                "level": 998, 
                "badge": "💎",
                "encrypted": True
            },
            base64.b64encode("A.OXG".encode()).decode(): {
                "role": "مطور رئيسي", 
                "level": 998, 
                "badge": "💎",
                "encrypted": True
            },
            base64.b64encode("VECTOR001".encode()).decode(): {
                "role": "مطور رئيسي", 
                "level": 998, 
                "badge": "💎",
                "encrypted": True
            }
        }

        default_config = {
            "edx_team": {
                "name": "فريق EDX",
                "encrypted_members": encrypted_members,
                "security": {
                    "file_protection": True, 
                    "modification_lock": True,
                    "encryption_enabled": True,
                    "last_verification": datetime.now().isoformat()
                }
            },
            "file_info": {
                "protected": True, 
                "security_hash": self.generate_security_hash(),
                "access_level": "RESTRICTED_EDX_ONLY"
            }
        }
        return default_config

    def generate_security_hash(self) -> str:
        """توليد هاش أمان فريد"""
        timestamp = str(datetime.now().timestamp())
        unique_data = f"EDX_TEAM_SECURE_{timestamp}_2025"
        return hashlib.sha256(unique_data.encode()).hexdigest()[:32]

    def encrypt_username(self, username: str) -> str:
        """تشفير اسم المستخدم"""
        return base64.b64encode(username.encode()).decode()

    def decrypt_username(self, encrypted_username: str) -> str:
        """فك تشفير اسم المستخدم"""
        try:
            return base64.b64decode(encrypted_username.encode()).decode()
        except Exception:
            return encrypted_username  # إرجاع الاسم كما هو إذا فشل فك التشفير

    def get_decrypted_members(self) -> Dict[str, Dict[str, Any]]:
        """الحصول على قائمة الأعضاء مع فك التشفير"""
        team_data = self.team_data.get("edx_team", {})

        # دعم الطريقة القديمة والجديدة
        if "encrypted_members" in team_data:
            decrypted_members = {}
            for encrypted_name, info in team_data["encrypted_members"].items():
                real_name = self.decrypt_username(encrypted_name)
                decrypted_members[real_name] = info
            return decrypted_members
        else:
            # الطريقة القديمة للتوافق مع الملفات الموجودة
            return team_data.get("members", {})

    def verify_file_integrity(self, data: Dict[str, Any]) -> bool:
        """التحقق من سلامة ملف التكوين"""
        try:
            # التحقق من وجود العناصر الأساسية
            if "edx_team" not in data or "file_info" not in data:
                return False

            # التحقق من أعضاء الفريق الأساسيين
            required_members = ["VECTOR000", "A.OPY", "A.OXG", "VECTOR001"]
            team_members = data["edx_team"].get("members", {})

            for member in required_members:
                if member not in team_members:
                    return False

            # التحقق من الحماية
            if not data["file_info"].get("protected", False):
                return False

            return True
        except Exception:
            return False

    def is_edx_member(self, username: str) -> bool:
        """التحقق من كون المستخدم عضو في فريق EDX مع دعم التشفير"""
        if not username:
            return False

        # الحصول على الأعضاء مع فك التشفير
        decrypted_members = self.get_decrypted_members()

        # التحقق بدون حساسية لحالة الأحرف
        return username.upper() in [member.upper() for member in decrypted_members.keys()]

    def get_member_info(self, username: str) -> Optional[Dict[str, Any]]:
        """الحصول على معلومات عضو الفريق مع دعم التشفير"""
        if not self.is_edx_member(username):
            return None

        # الحصول على الأعضاء مع فك التشفير
        decrypted_members = self.get_decrypted_members()

        # البحث بدون حساسية لحالة الأحرف
        for member_name, member_info in decrypted_members.items():
            if member_name.upper() == username.upper():
                return {
                    "username": member_name,
                    "role": member_info.get("role", "عضو فريق"),
                    "level": member_info.get("level", 998),
                    "badge": member_info.get("badge", "💎"),
                    "title": member_info.get("title", f"عضو فريق EDX - {member_info.get('role', '')}"),
                    "permissions": member_info.get("permissions", "*"),
                    "secure_access": True
                }
        return None

    def get_member_level(self, username: str) -> int:
        """الحصول على مستوى العضو"""
        member_info = self.get_member_info(username)
        return member_info.get("level", 0) if member_info else 0

    def has_permission(self, username: str, permission: str = "*") -> bool:
        """التحقق من صلاحيات العضو"""
        if not self.is_edx_member(username):
            return False

        member_info = self.get_member_info(username)
        if not member_info:
            return False

        # أعضاء فريق EDX لديهم جميع الصلاحيات
        member_permissions = member_info.get("permissions", "*")
        return member_permissions == "*" or permission in member_permissions

    def get_team_status(self) -> str:
        """الحصول على حالة فريق EDX مع دعم التشفير"""
        team_info = self.team_data.get("edx_team", {})
        decrypted_members = self.get_decrypted_members()

        status = f"🏆 **حالة فريق EDX المصري**\n"
        status += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        status += f"👥 عدد الأعضاء: {len(decrypted_members)}\n"
        status += f"🔒 حالة الحماية: {'مفعلة' if self.protection_enabled else 'معطلة'}\n"
        status += f"🔐 التشفير: {'مفعل' if team_info.get('security', {}).get('encryption_enabled') else 'معطل'}\n\n"

        status += "**🎖️ أعضاء الفريق:**\n"
        for member_name, member_info in decrypted_members.items():
            badge = member_info.get("badge", "💎")
            role = member_info.get("role", "عضو فريق")
            level = member_info.get("level", 998)
            status += f"{badge} **{member_name}** - {role} (المستوى: {level})\n"

        return status

    def get_team_members_list(self) -> List[str]:
        """الحصول على قائمة أعضاء الفريق مع فك التشفير"""
        decrypted_members = self.get_decrypted_members()
        return list(decrypted_members.keys())

    def log_team_action(self, username: str, action: str, details: str = ""):
        """تسجيل إجراءات الفريق"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "member": username,
                "action": action,
                "details": details
            }

            # إضافة إلى سجل التعديلات
            if "modification_history" not in self.team_data["file_info"]:
                self.team_data["file_info"]["modification_history"] = []

            self.team_data["file_info"]["modification_history"].append(log_entry)

            # الاحتفاظ بآخر 50 إدخال فقط
            if len(self.team_data["file_info"]["modification_history"]) > 50:
                self.team_data["file_info"]["modification_history"] = \
                    self.team_data["file_info"]["modification_history"][-50:]

            print(f"📝 سجل فريق EDX: {username} - {action}")

        except Exception as e:
            print(f"❌ خطأ في تسجيل إجراء الفريق: {e}")

    def check_command_override(self, username: str, command: str) -> Dict[str, Any]:
        """فحص تجاوز صلاحيات الأوامر لفريق EDX"""
        result = {
            "is_edx_member": False,
            "override_granted": False,
            "member_info": None,
            "message": None
        }

        if self.is_edx_member(username):
            result["is_edx_member"] = True
            result["override_granted"] = True
            result["member_info"] = self.get_member_info(username)

            # تسجيل استخدام الأمر
            self.log_team_action(username, f"استخدام أمر: {command}")

            badge = result["member_info"].get("badge", "💎")
            title = result["member_info"].get("title", "عضو فريق EDX")

            result["message"] = f"{badge} مرحباً {username} - {title}\n✅ تم منح صلاحيات فريق EDX لتنفيذ الأمر"

        return result

    def get_edx_commands_help(self) -> str:
        """الحصول على مساعدة أوامر فريق EDX"""
        help_text = "🏆 **أوامر فريق EDX الخاصة:**\n\n"

        commands = {
            "edx_status": "📊 عرض حالة فريق EDX",
            "edx_members": "👥 عرض أعضاء الفريق",
            "edx_override": "🔓 تجاوز القيود (للفريق فقط)",
            "edx_debug": "🐛 وضع التطوير المتقدم",
            "edx_admin": "👑 صلاحيات إدارية خاصة",
            "edx_log": "📝 عرض سجل أنشطة الفريق"
        }

        for cmd, desc in commands.items():
            help_text += f"• `{cmd}` - {desc}\n"

        help_text += f"\n💡 **ملاحظة:** هذه الأوامر متاحة حصرياً لأعضاء فريق EDX المصري"

        return help_text

    def protect_file(self):
        """حماية ملف التكوين من التعديل"""
        try:
            # تعديل صلاحيات الملف (للقراءة فقط)
            if os.path.exists(self.config_file):
                os.chmod(self.config_file, 0o444)  # قراءة فقط
            print("🔒 تم تفعيل حماية ملف فريق EDX")
        except Exception as e:
            print(f"⚠️ تحذير: لم يتم تفعيل حماية الملف: {e}")

        """حفظ إعدادات الفريق مع حماية إضافية"""
        try:
            # إنشاء نسخة احتياطية قبل الحفظ
            if os.path.exists(self.config_file):
                backup_path = f"{self.config_file}.backup"
                import shutil
                shutil.copy2(self.config_file, backup_path)

            # تحديث هاش الأمان قبل الحفظ
            self.team_data["file_info"]["security_hash"] = self.generate_security_hash()
            self.team_data["file_info"]["last_modified"] = datetime.now().isoformat()

            # حفظ البيانات
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.team_data, f, ensure_ascii=False, indent=2)

            print("🔒 تم حفظ إعدادات فريق EDX بأمان")
            return True

        except Exception as e:
            print(f"❌ خطأ في حفظ إعدادات فريق EDX: {e}")
            return False

    def verify_team_access(self, username: str) -> Dict[str, Any]:
        """التحقق من صلاحية الوصول مع تفاصيل الأمان"""
        if not self.is_edx_member(username):
            return {
                "access_granted": False,
                "reason": "ليس عضو في فريق EDX",
                "security_level": "DENIED"
            }

        member_info = self.get_member_info(username)
        return {
            "access_granted": True,
            "member_info": member_info,
            "security_level": "FULL_ACCESS",
            "permissions": "*",
            "verification_time": datetime.now().isoformat()
        }

    def save_team_config_secure(self):
        """حفظ إعدادات الفريق مع حماية إضافية"""
        try:
            # إنشاء نسخة احتياطية قبل الحفظ
            if os.path.exists(self.config_file):
                backup_path = f"{self.config_file}.backup"
                import shutil
                shutil.copy2(self.config_file, backup_path)

            # تحديث هاش الأمان قبل الحفظ
            self.team_data["file_info"]["security_hash"] = self.generate_security_hash()
            self.team_data["file_info"]["last_modified"] = datetime.now().isoformat()

            # حفظ البيانات
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.team_data, f, ensure_ascii=False, indent=2)

            print("🔒 تم حفظ إعدادات فريق EDX بأمان")
            return True

        except Exception as e:
            print(f"❌ خطأ في حفظ إعدادات فريق EDX: {e}")
            return False

# إنشاء مثيل مدير فريق EDX
edx_manager = EDXTeamManager()