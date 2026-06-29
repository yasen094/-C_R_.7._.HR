"""
نظام كشف المشرفين المتقدم - تحليل رسائل النظام والأنماط
"""
import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

"""
نظام فحص المشرفين المتقدم
"""
import json
import os
import asyncio
from datetime import datetime, timedelta

class AdvancedModeratorDetector:
    def __init__(self):
        self.console_patterns_file = "data/console_patterns.json"
        self.message_patterns_file = "data/message_patterns.json"
        self.detected_moderators = {}

        # أنماط رسائل المشرفين في النظام
        self.moderator_console_patterns = [
            r"moderator",
            r"admin",
            r"staff",
            r"kicked",
            r"banned",
            r"muted",
            r"warned",
            r"promoted",
            r"room_privilege",
            r"permission_granted",
            r"access_level",
            r"elevated_user"
        ]

        # أنماط رسائل المشرفين في الشات
        self.moderator_chat_patterns = [
            r"^\[MOD\]",
            r"^\[ADMIN\]", 
            r"^\[STAFF\]",
            r"has been kicked",
            r"has been banned",
            r"has been muted",
            r"room settings changed",
            r"user promoted",
            r"permissions updated"
        ]

        # كلمات مفتاحية تدل على المشرفين
        self.moderator_keywords = [
            "mod", "admin", "staff", "manager", "owner", "creator",
            "vip", "premium", "elite", "leader", "supervisor"
        ]

        # نمط تحليل الأذونات
        self.permission_indicators = [
            "can_kick", "can_ban", "can_mute", "can_promote",
            "room_admin", "room_mod", "elevated_privileges"
        ]

        self.load_patterns()
        print("🔍 نظام كشف المشرفين المتقدم جاهز")

    def load_patterns(self):
        """تحميل الأنماط المحفوظة"""
        try:
            if os.path.exists(self.console_patterns_file):
                with open(self.console_patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.moderator_console_patterns.extend(data.get("patterns", []))
        except Exception as e:
            print(f"خطأ في تحميل أنماط الكونسول: {e}")

    def save_patterns(self):
        """حفظ الأنماط المكتشفة"""
        try:
            os.makedirs("data", exist_ok=True)
            console_data = {
                "patterns": list(set(self.moderator_console_patterns)),
                "last_updated": datetime.now().isoformat()
            }
            with open(self.console_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(console_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ الأنماط: {e}")

    def analyze_console_message(self, message: str, username: str = None) -> Optional[Dict]:
        """تحليل رسالة من console للكشف عن المشرفين"""
        try:
            message_lower = message.lower()
            moderator_score = 0
            detected_patterns = []

            # فحص الأنماط المباشرة
            for pattern in self.moderator_console_patterns:
                if re.search(pattern, message_lower):
                    moderator_score += 2
                    detected_patterns.append(pattern)

            # فحص الكلمات المفتاحية
            for keyword in self.moderator_keywords:
                if keyword in message_lower:
                    moderator_score += 1
                    detected_patterns.append(f"keyword:{keyword}")

            # فحص مؤشرات الصلاحيات
            for indicator in self.permission_indicators:
                if indicator in message_lower:
                    moderator_score += 3
                    detected_patterns.append(f"permission:{indicator}")

            # تحليل رسائل الإجراءات الإدارية
            admin_actions = [
                r"user.*kicked", r"user.*banned", r"user.*muted",
                r"room.*settings.*changed", r"permissions.*updated",
                r"user.*promoted", r"access.*granted"
            ]

            for action in admin_actions:
                if re.search(action, message_lower):
                    moderator_score += 4
                    detected_patterns.append(f"admin_action:{action}")

            # إذا كانت النتيجة عالية، قم بتسجيل المشرف المحتمل
            if moderator_score >= 3:
                return {
                    "score": moderator_score,
                    "patterns": detected_patterns,
                    "message": message,
                    "detected_at": datetime.now().isoformat(),
                    "detection_method": "console_analysis"
                }

            return None

        except Exception as e:
            print(f"خطأ في تحليل رسالة الكونسول: {e}")
            return None

    def analyze_chat_message(self, username: str, message: str) -> Optional[Dict]:
        """تحليل رسالة شات للكشف عن المشرفين"""
        try:
            message_lower = message.lower()
            moderator_score = 0
            detected_patterns = []

            # فحص أنماط رسائل المشرفين
            for pattern in self.moderator_chat_patterns:
                if re.search(pattern, message):
                    moderator_score += 3
                    detected_patterns.append(f"chat_pattern:{pattern}")

            # فحص الأوامر الإدارية
            admin_commands = [
                r"^/kick", r"^/ban", r"^/mute", r"^/warn",
                r"^!kick", r"^!ban", r"^!mute", r"^!warn"
            ]

            for command in admin_commands:
                if re.search(command, message):
                    moderator_score += 5
                    detected_patterns.append(f"admin_command:{command}")

            # فحص كلمات المشرفين في اسم المستخدم
            username_lower = username.lower()
            for keyword in self.moderator_keywords:
                if keyword in username_lower:
                    moderator_score += 2
                    detected_patterns.append(f"username_keyword:{keyword}")

            # فحص رسائل النظام الخاصة بالمشرفين
            system_messages = [
                r"has been kicked by", r"has been banned by",
                r"room settings updated by", r"user promoted by"
            ]

            for sys_msg in system_messages:
                if re.search(sys_msg, message_lower):
                    # البحث عن اسم المشرف في الرسالة
                    if username in message:
                        moderator_score += 4
                        detected_patterns.append(f"system_action:{sys_msg}")

            if moderator_score >= 3:
                return {
                    "username": username,
                    "score": moderator_score,
                    "patterns": detected_patterns,
                    "message": message,
                    "detected_at": datetime.now().isoformat(),
                    "detection_method": "chat_analysis"
                }

            return None

        except Exception as e:
            print(f"خطأ في تحليل رسالة الشات: {e}")
            return None

    def analyze_user_behavior_patterns(self, username: str, user_data: Dict) -> Optional[Dict]:
        """تحليل أنماط سلوك المستخدم للكشف عن المشرفين"""
        try:
            behavior_score = 0
            behavior_indicators = []

            # تحليل تكرار الزيارات
            visit_count = user_data.get('visit_count', 0)
            if visit_count > 200:
                behavior_score += 3
                behavior_indicators.append(f"high_visits:{visit_count}")
            elif visit_count > 100:
                behavior_score += 2
                behavior_indicators.append(f"moderate_visits:{visit_count}")

            # تحليل قدم الحساب
            first_seen = user_data.get('first_seen', '')
            if first_seen:
                try:
                    first_date = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
                    days_old = (datetime.now() - first_date).days

                    if days_old > 365:  # أكثر من سنة
                        behavior_score += 3
                        behavior_indicators.append(f"old_account:{days_old}days")
                    elif days_old > 180:  # أكثر من 6 شهور
                        behavior_score += 2
                        behavior_indicators.append(f"established_account:{days_old}days")
                except:
                    pass

            # تحليل النشاط المنتظم
            if user_data.get('is_active', False):
                behavior_score += 1
                behavior_indicators.append("currently_active")

            # تحليل نمط النشاط
            last_seen = user_data.get('last_seen', '')
            if last_seen and first_seen:
                try:
                    last_date = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    first_date = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))

                    # حساب معدل النشاط
                    days_span = (last_date - first_date).days
                    if days_span > 0:
                        activity_rate = visit_count / days_span
                        if activity_rate > 1:  # أكثر من زيارة يومياً
                            behavior_score += 2
                            behavior_indicators.append(f"high_activity_rate:{activity_rate:.2f}")
                except:
                    pass

            if behavior_score >= 5:
                return {
                    "username": username,
                    "score": behavior_score,
                    "indicators": behavior_indicators,
                    "detected_at": datetime.now().isoformat(),
                    "detection_method": "behavior_analysis"
                }

            return None

        except Exception as e:
            print(f"خطأ في تحليل سلوك المستخدم: {e}")
            return None

    def cross_reference_detection(self, username: str, detection_results: List[Dict]) -> Dict:
        """تحليل متقاطع لنتائج الكشف المختلفة"""
        try:
            total_score = 0
            all_patterns = []
            detection_methods = []
            confidence_level = "منخفض"

            for result in detection_results:
                total_score += result.get('score', 0)
                all_patterns.extend(result.get('patterns', []))
                all_patterns.extend(result.get('indicators', []))
                detection_methods.append(result.get('detection_method', 'unknown'))

            # تحديد مستوى الثقة
            if total_score >= 15:
                confidence_level = "عالي جداً"
            elif total_score >= 10:
                confidence_level = "عالي"
            elif total_score >= 7:
                confidence_level = "متوسط"
            elif total_score >= 5:
                confidence_level = "منخفض"

            return {
                "username": username,
                "total_score": total_score,
                "confidence_level": confidence_level,
                "detection_methods": list(set(detection_methods)),
                "all_patterns": list(set(all_patterns)),
                "detected_at": datetime.now().isoformat(),
                "is_likely_moderator": total_score >= 7
            }

        except Exception as e:
            print(f"خطأ في التحليل المتقاطع: {e}")
            return {}

    def analyze_room_system_messages(self, system_messages: List[str]) -> Dict[str, Dict]:
        """تحليل رسائل النظام للغرفة لاستخراج المشرفين"""
        try:
            detected_moderators = {}

            for message in system_messages:
                # البحث عن رسائل الإجراءات الإدارية
                kick_pattern = r"(.+?)\s+kicked\s+(.+)"
                ban_pattern = r"(.+?)\s+banned\s+(.+)"
                mute_pattern = r"(.+?)\s+muted\s+(.+)"

                patterns = [
                    (kick_pattern, "kick_action"),
                    (ban_pattern, "ban_action"), 
                    (mute_pattern, "mute_action")
                ]

                for pattern, action_type in patterns:
                    match = re.search(pattern, message)
                    if match:
                        moderator_username = match.group(1).strip()

                        if moderator_username not in detected_moderators:
                            detected_moderators[moderator_username] = {
                                "username": moderator_username,
                                "actions": [],
                                "score": 0,
                                "detection_method": "system_messages"
                            }

                        detected_moderators[moderator_username]["actions"].append(action_type)
                        detected_moderators[moderator_username]["score"] += 5

            return detected_moderators

        except Exception as e:
            print(f"خطأ في تحليل رسائل النظام: {e}")
            return {}

    def get_detection_report(self, username: str) -> str:
        """إنتاج تقرير مفصل عن كشف المشرف"""
        if username not in self.detected_moderators:
            return f"❌ لم يتم العثور على بيانات كشف للمستخدم {username}"

        data = self.detected_moderators[username]

        report_lines = [
            f"📋 تقرير كشف المشرف: {username}",
            f"🎯 النتيجة الإجمالية: {data.get('total_score', 0)}",
            f"📊 مستوى الثقة: {data.get('confidence_level', 'غير محدد')}",
            f"🔍 طرق الكشف: {', '.join(data.get('detection_methods', []))}",
            f"✅ مشرف محتمل: {'نعم' if data.get('is_likely_moderator', False) else 'لا'}",
            f"📅 تاريخ الكشف: {data.get('detected_at', 'غير محدد')[:16]}"
        ]

        patterns = data.get('all_patterns', [])
        if patterns:
            report_lines.append(f"🔍 الأنماط المكتشفة: {', '.join(patterns[:5])}")
            if len(patterns) > 5:
                report_lines.append(f"   + {len(patterns) - 5} نمط إضافي")

        return "\n".join(report_lines)

    def update_moderator_confidence(self, username: str, additional_evidence: Dict):
        """تحديث مستوى الثقة في المشرف بناءً على أدلة إضافية"""
        try:
            if username not in self.detected_moderators:
                self.detected_moderators[username] = {
                    "username": username,
                    "total_score": 0,
                    "confidence_level": "منخفض",
                    "detection_methods": [],
                    "all_patterns": [],
                    "detected_at": datetime.now().isoformat(),
                    "is_likely_moderator": False
                }

            # إضافة الأدلة الجديدة
            current_data = self.detected_moderators[username]
            current_data["total_score"] += additional_evidence.get("score", 0)
            current_data["detection_methods"].extend(additional_evidence.get("methods", []))
            current_data["all_patterns"].extend(additional_evidence.get("patterns", []))

            # إعادة تقييم مستوى الثقة
            score = current_data["total_score"]
            if score >= 15:
                current_data["confidence_level"] = "عالي جداً"
            elif score >= 10:
                current_data["confidence_level"] = "عالي"
            elif score >= 7:
                current_data["confidence_level"] = "متوسط"
            else:
                current_data["confidence_level"] = "منخفض"

            current_data["is_likely_moderator"] = score >= 7
            current_data["last_updated"] = datetime.now().isoformat()

            print(f"🔄 تم تحديث مستوى الثقة للمستخدم {username}: {current_data['confidence_level']}")

        except Exception as e:
            print(f"خطأ في تحديث مستوى الثقة: {e}")

    def get_all_detected_moderators(self) -> List[Dict]:
        """الحصول على جميع المشرفين المكتشفين"""
        moderators = []
        for username, data in self.detected_moderators.items():
            if data.get('is_likely_moderator', False):
                moderators.append(data)

        # ترتيب حسب النتيجة
        moderators.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        return moderators

    def save_detection_results(self):
        """حفظ نتائج الكشف"""
        try:
            results_file = "data/moderator_detection_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.detected_moderators, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ نتائج الكشف: {e}")

    def load_detection_results(self):
        """تحميل نتائج الكشف المحفوظة"""
        try:
            results_file = "data/moderator_detection_results.json"
            if os.path.exists(results_file):
                with open(results_file, 'r', encoding='utf-8') as f:
                    self.detected_moderators = json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل نتائج الكشف: {e}")