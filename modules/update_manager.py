"""
مدير التحديثات - نظام إدارة وتطبيق التحديثات التلقائية
"""
import json
import os
import zipfile
import shutil
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path

class UpdateManager:
    def __init__(self):
        self.updates_dir = "updates"
        self.updates_data_file = "data/updates_data.json"
        self.current_version = "3.0.0"
        self.developer_code = "01018"

        # الملفات المحمية التي لن يتم تحديثها
        self.protected_files = {
            "data/users_data.json",
            "data/people.json", 
            "data/moderators.json",
            "data/positions_data.json",
            "data/user_locations.json",
            "data/auto_dance_users.json",
            "data/room_permissions.json"
        }

        # الملفات التي يُسمح بتحديثها
        self.updatable_files = {
            "main.py",
            "run.py",
            "modules/",
            "templates/",
            "static/",
            "data/emotes_data.json",
            "data/emote_timings.json"
        }

        self.ensure_directories()
        self.load_updates_data()
        print("🔄 مدير التحديثات جاهز")

    def ensure_directories(self):
        """إنشاء المجلدات المطلوبة"""
        os.makedirs(self.updates_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("backups", exist_ok=True)

    def load_updates_data(self):
        """تحميل بيانات التحديثات"""
        try:
            if os.path.exists(self.updates_data_file):
                with open(self.updates_data_file, 'r', encoding='utf-8') as f:
                    self.updates_data = json.load(f)
            else:
                self.updates_data = {
                    "current_version": self.current_version,
                    "updates": [],
                    "installed_updates": [],
                    "last_check": None
                }
                self.save_updates_data()
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات التحديثات: {e}")
            self.updates_data = {
                "current_version": self.current_version,
                "updates": [],
                "installed_updates": [],
                "last_check": None
            }

    def save_updates_data(self):
        """حفظ بيانات التحديثات"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(self.updates_data_file), exist_ok=True)

            # إضافة timestamp للحفظ
            self.updates_data["last_saved"] = datetime.now().isoformat()

            with open(self.updates_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.updates_data, f, ensure_ascii=False, indent=2)
            print(f"💾 تم حفظ بيانات التحديثات - المجموع: {len(self.updates_data.get('updates', []))}")
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات التحديثات: {e}")

    def verify_developer_code(self, code: str) -> bool:
        """التحقق من كود المطور"""
        return code == self.developer_code

    def upload_update(self, file_path: str, version: str, title: str, description: str, changelog: str = "") -> dict:
        """رفع تحديث جديد"""
        try:
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                return {"success": False, "error": "الملف غير موجود"}

            # التحقق من صحة الملف
            if not zipfile.is_zipfile(file_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            # التأكد من وجود المجلدات
            self.ensure_directories()

            # إنشاء معرف فريد للتحديث
            timestamp = int(datetime.now().timestamp())
            update_id = f"update_{version.replace('.', '_')}_{timestamp}"

            # نسخ الملف لمجلد التحديثات
            update_file_path = os.path.join(self.updates_dir, f"{update_id}.zip")
            shutil.copy2(file_path, update_file_path)

            # التحقق من نجاح النسخ
            if not os.path.exists(update_file_path):
                return {"success": False, "error": "فشل في نسخ ملف التحديث"}

            # حساب hash الملف
            file_hash = self.calculate_file_hash(update_file_path)
            file_size = os.path.getsize(update_file_path)

            # إنشاء بيانات التحديث
            update_data = {
                "id": update_id,
                "version": version,
                "title": title,
                "description": description,
                "changelog": changelog,
                "file_path": update_file_path,
                "file_hash": file_hash,
                "size": self.format_file_size(file_size),
                "size_bytes": file_size,
                "release_date": datetime.now().isoformat(),
                "is_active": True,
                "upload_timestamp": timestamp
            }

            # إضافة التحديث للقائمة
            if "updates" not in self.updates_data:
                self.updates_data["updates"] = []

            self.updates_data["updates"].append(update_data)

            # حفظ البيانات
            self.save_updates_data()

            # التحقق من حفظ البيانات
            if not os.path.exists(self.updates_data_file):
                return {"success": False, "error": "فشل في حفظ بيانات التحديث"}

            print(f"✅ تم رفع التحديث {version} بنجاح - ID: {update_id}")
            print(f"📁 مسار الملف: {update_file_path}")
            print(f"📊 حجم الملف: {self.format_file_size(file_size)}")

            return {
                "success": True, 
                "update_id": update_id,
                "message": f"تم رفع التحديث {version} بنجاح"
            }

        except Exception as e:
            print(f"❌ خطأ في رفع التحديث: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def get_available_updates(self) -> list:
        """الحصول على التحديثات المتاحة"""
        try:
            available_updates = []
            installed_ids = [u["id"] for u in self.updates_data.get("installed_updates", [])]

            for update in self.updates_data.get("updates", []):
                if update["is_active"] and update["id"] not in installed_ids:
                    # التحقق من وجود الملف
                    if os.path.exists(update["file_path"]):
                        available_updates.append(update)
                    else:
                        update["is_active"] = False

            # ترتيب حسب تاريخ الإصدار (الأحدث أولاً)
            available_updates.sort(key=lambda x: x["release_date"], reverse=True)

            self.updates_data["last_check"] = datetime.now().isoformat()
            self.save_updates_data()

            return available_updates

        except Exception as e:
            print(f"❌ خطأ في الحصول على التحديثات: {e}")
            return []

    def apply_update(self, update_id: str) -> dict:
        """تطبيق تحديث معين - متاح للجميع"""
        try:
            # البحث عن التحديث
            update = None
            for u in self.updates_data.get("updates", []):
                if u["id"] == update_id:
                    update = u
                    break

            if not update:
                return {"success": False, "error": "التحديث غير موجود"}

            if not os.path.exists(update["file_path"]):
                return {"success": False, "error": "ملف التحديث غير موجود"}

            # التحقق من hash الملف
            current_hash = self.calculate_file_hash(update["file_path"])
            if current_hash != update["file_hash"]:
                return {"success": False, "error": "ملف التحديث تالف"}

            # إنشاء نسخة احتياطية
            backup_result = self.create_backup()
            if not backup_result["success"]:
                return {"success": False, "error": f"فشل في إنشاء النسخة الاحتياطية: {backup_result['error']}"}

            # تطبيق التحديث
            update_result = self.extract_and_apply_update(update["file_path"])
            if not update_result["success"]:
                # استعادة النسخة الاحتياطية
                self.restore_backup(backup_result["backup_path"])
                return {"success": False, "error": f"فشل في تطبيق التحديث: {update_result['error']}"}

            # تسجيل التحديث كمطبق
            self.updates_data["installed_updates"].append({
                "id": update["id"],
                "version": update["version"],
                "installed_date": datetime.now().isoformat(),
                "backup_path": backup_result["backup_path"]
            })

            self.updates_data["current_version"] = update["version"]
            self.save_updates_data()

            print(f"✅ تم تطبيق التحديث {update['version']} بنجاح")
            return {"success": True, "message": "تم تطبيق التحديث بنجاح"}

        except Exception as e:
            print(f"❌ خطأ في تطبيق التحديث: {e}")
            return {"success": False, "error": str(e)}

    def create_backup(self) -> dict:
        """إنشاء نسخة احتياطية من الملفات الحالية"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_name)

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # نسخ احتياطية للملفات القابلة للتحديث فقط
                for updatable_path in self.updatable_files:
                    if os.path.exists(updatable_path):
                        if os.path.isfile(updatable_path):
                            backup_zip.write(updatable_path)
                        elif os.path.isdir(updatable_path):
                            for root, dirs, files in os.walk(updatable_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    backup_zip.write(file_path)

            print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
            return {"success": True, "backup_path": backup_path}

        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
            return {"success": False, "error": str(e)}

    def extract_and_apply_update(self, update_file_path: str) -> dict:
        """استخراج وتطبيق ملفات التحديث مع تحليل متقدم"""
        try:
            update_summary = {
                "new_files": [],
                "updated_files": [],
                "new_features": [],
                "changes_detected": []
            }

            with zipfile.ZipFile(update_file_path, 'r') as update_zip:
                # استخراج لمجلد مؤقت أولاً
                with tempfile.TemporaryDirectory() as temp_dir:
                    print(f"🔍 فك ضغط التحديث إلى: {temp_dir}")
                    update_zip.extractall(temp_dir)

                    # تحليل محتويات التحديث
                    self._analyze_update_contents(temp_dir, update_summary)

                    # نسخ الملفات المسموح بتحديثها فقط
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            source_path = os.path.join(root, file)
                            # تحديد المسار النسبي
                            rel_path = os.path.relpath(source_path, temp_dir)

                            # التحقق من أن الملف مسموح بتحديثه
                            if self.is_file_updatable(rel_path):
                                # التحقق من وجود الملف سابقاً
                                if os.path.exists(rel_path):
                                    update_summary["updated_files"].append(rel_path)
                                    print(f"🔄 تحديث: {rel_path}")
                                else:
                                    update_summary["new_files"].append(rel_path)
                                    print(f"✨ ملف جديد: {rel_path}")

                                # إنشاء المجلد إذا لم يكن موجوداً
                                dest_dir = os.path.dirname(rel_path)
                                if dest_dir:
                                    os.makedirs(dest_dir, exist_ok=True)

                                # نسخ الملف
                                shutil.copy2(source_path, rel_path)

            # إنشاء تقرير التحديث
            self._create_update_report(update_summary)

            return {
                "success": True, 
                "summary": update_summary,
                "report": self._format_update_summary(update_summary)
            }

        except Exception as e:
            print(f"❌ خطأ في استخراج التحديث: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_update_contents(self, temp_dir: str, summary: dict):
        """تحليل محتويات التحديث للبحث عن الميزات الجديدة"""
        try:
            print("🔍 تحليل محتويات التحديث...")

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)

                    if file.endswith('.py'):
                        self._analyze_python_file(file_path, rel_path, summary)
                    elif file.endswith('.html'):
                        self._analyze_html_file(file_path, rel_path, summary)
                    elif file.endswith('.js'):
                        self._analyze_js_file(file_path, rel_path, summary)

        except Exception as e:
            print(f"⚠️ خطأ في تحليل التحديث: {e}")

    def _analyze_python_file(self, file_path: str, rel_path: str, summary: dict):
        """تحليل ملفات Python للبحث عن الميزات الجديدة"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # البحث عن أوامر جديدة
            import re

            # البحث عن أوامر elif message == 
            command_patterns = re.findall(r'elif message == ["\']([^"\']+)["\']', content)
            if command_patterns:
                for cmd in command_patterns:
                    summary["new_features"].append(f"🎯 أمر جديد: {cmd} في {rel_path}")

            # البحث عن دوال جديدة
            function_patterns = re.findall(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(', content)
            if function_patterns:
                for func in function_patterns:
                    if not func.startswith('_'):  # تجاهل الدوال الخاصة
                        summary["new_features"].append(f"🔧 دالة جديدة: {func}() في {rel_path}")

            # البحث عن كلاسات جديدة
            class_patterns = re.findall(r'class ([A-Z][a-zA-Z0-9_]*)', content)
            if class_patterns:
                for cls in class_patterns:
                    summary["new_features"].append(f"📦 كلاس جديد: {cls} في {rel_path}")

        except Exception as e:
            print(f"⚠️ خطأ في تحليل ملف Python {rel_path}: {e}")

    def _analyze_html_file(self, file_path: str, rel_path: str, summary: dict):
        """تحليل ملفات HTML للبحث عن صفحات جديدة"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # البحث عن عناوين الصفحات
            import re
            title_match = re.search(r'<title>([^<]+)</title>', content)
            if title_match:
                title = title_match.group(1)
                summary["new_features"].append(f"🌐 صفحة جديدة: {title} ({rel_path})")

        except Exception as e:
            print(f"⚠️ خطأ في تحليل ملف HTML {rel_path}: {e}")

    def _analyze_js_file(self, file_path: str, rel_path: str, summary: dict):
        """تحليل ملفات JavaScript للبحث عن وظائف جديدة"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # البحث عن دوال JavaScript
            import re
            function_patterns = re.findall(r'function ([a-zA-Z_][a-zA-Z0-9_]*)\(', content)
            if function_patterns:
                for func in function_patterns:
                    summary["new_features"].append(f"⚙️ دالة JS جديدة: {func}() في {rel_path}")

        except Exception as e:
            print(f"⚠️ خطأ في تحليل ملف JS {rel_path}: {e}")

    def _create_update_report(self, summary: dict):
        """إنشاء تقرير مفصل عن التحديث"""
        try:
            report_path = f"updates/update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs("updates", exist_ok=True)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("📋 تقرير التحديث التلقائي\n")
                f.write("=" * 50 + "\n")
                f.write(f"⏰ وقت التطبيق: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                f.write(f"📁 الملفات الجديدة ({len(summary['new_files'])}):\n")
                for file in summary['new_files']:
                    f.write(f"  + {file}\n")
                f.write("\n")

                f.write(f"🔄 الملفات المحدثة ({len(summary['updated_files'])}):\n")
                for file in summary['updated_files']:
                    f.write(f"  ~ {file}\n")
                f.write("\n")

                f.write(f"✨ الميزات الجديدة ({len(summary['new_features'])}):\n")
                for feature in summary['new_features']:
                    f.write(f"  {feature}\n")
                f.write("\n")

            print(f"📄 تم إنشاء تقرير التحديث: {report_path}")

        except Exception as e:
            print(f"⚠️ خطأ في إنشاء تقرير التحديث: {e}")

    def _format_update_summary(self, summary: dict) -> str:
        """تنسيق ملخص التحديث للعرض"""
        lines = ["📋 ملخص التحديث:"]

        if summary["new_files"]:
            lines.append(f"📁 ملفات جديدة: {len(summary['new_files'])}")

        if summary["updated_files"]:
            lines.append(f"🔄 ملفات محدثة: {len(summary['updated_files'])}")

        if summary["new_features"]:
            lines.append(f"✨ ميزات جديدة: {len(summary['new_features'])}")
            lines.append("🎯 أهم الإضافات:")
            for feature in summary["new_features"][:5]:  # عرض أول 5 ميزات
                lines.append(f"  • {feature}")

        return "\n".join(lines)

    def is_file_updatable(self, file_path: str) -> bool:
        """التحقق من إمكانية تحديث الملف"""
        # تحويل مسارات Windows لـ Unix
        file_path = file_path.replace('\\', '/')

        # التحقق من الملفات المحمية
        if file_path in self.protected_files:
            return False

        # التحقق من المجلدات والملفات المسموح بتحديثها
        for updatable in self.updatable_files:
            if file_path.startswith(updatable) or file_path == updatable:
                return True

        return False

    def restore_backup(self, backup_path: str) -> dict:
        """استعادة النسخة الاحتياطية"""
        try:
            if not os.path.exists(backup_path):
                return {"success": False, "error": "ملف النسخة الاحتياطية غير موجود"}

            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                backup_zip.extractall('.')

            print(f"✅ تم استعادة النسخة الاحتياطية من: {backup_path}")
            return {"success": True}

        except Exception as e:
            print(f"❌ خطأ في استعادة النسخة الاحتياطية: {e}")
            return {"success": False, "error": str(e)}

    def calculate_file_hash(self, file_path: str) -> str:
        """حساب hash للملف"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"❌ خطأ في حساب hash الملف: {e}")
            return ""

    def format_file_size(self, size_bytes: int) -> str:
        """تنسيق حجم الملف"""
        try:
            if size_bytes == 0:
                return "0 بايت"

            size_names = ["بايت", "كيلوبايت", "ميجابايت", "جيجابايت"]
            i = 0
            while size_bytes >= 1024.0 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1

            return f"{size_bytes:.1f} {size_names[i]}"
        except:
            return "غير معروف"

    def get_system_info(self) -> dict:
        """الحصول على معلومات النظام"""
        try:
            return {
                "current_version": self.updates_data.get("current_version", self.current_version),
                "total_updates": len(self.updates_data.get("updates", [])),
                "installed_updates": len(self.updates_data.get("installed_updates", [])),
                "last_check": self.updates_data.get("last_check"),
                "last_update": self.get_last_installed_update()
            }
        except Exception as e:
            print(f"❌ خطأ في الحصول على معلومات النظام: {e}")
            return {}

    def get_last_installed_update(self) -> str:
        """الحصول على آخر تحديث مثبت"""
        try:
            installed = self.updates_data.get("installed_updates", [])
            if installed:
                last_update = max(installed, key=lambda x: x.get("installed_date", ""))
                return last_update.get("installed_date", "غير معروف")
            return "لم يتم التحديث بعد"
        except:
            return "غير معروف"

    def extract_zip_file(self, zip_path: str, extract_to: str = None, password: str = None) -> dict:
        """فك ضغط ملف ZIP مع إمكانيات متقدمة"""
        try:
            if extract_to is None:
                extract_to = os.path.splitext(zip_path)[0]

            if not os.path.exists(zip_path):
                return {"success": False, "error": "ملف ZIP غير موجود"}

            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            # إنشاء مجلد الاستخراج
            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # التحقق من وجود كلمة مرور
                if password:
                    zip_ref.setpassword(password.encode())

                # الحصول على قائمة الملفات
                file_list = zip_ref.namelist()

                # فك الضغط
                zip_ref.extractall(extract_to)

                print(f"✅ تم فك ضغط {len(file_list)} ملف إلى: {extract_to}")

                return {
                    "success": True,
                    "extract_path": extract_to,
                    "files_extracted": len(file_list),
                    "file_list": file_list
                }

        except zipfile.BadZipFile:
            return {"success": False, "error": "ملف ZIP تالف"}
        except RuntimeError as e:
            if "Bad password" in str(e):
                return {"success": False, "error": "كلمة مرور خاطئة"}
            return {"success": False, "error": f"خطأ في فك الضغط: {str(e)}"}
        except Exception as e:
            print(f"❌ خطأ في فك ضغط الملف: {e}")
            return {"success": False, "error": str(e)}

    def create_zip_file(self, source_path: str, zip_path: str, compression_level: int = 6) -> dict:
        """إنشاء ملف ZIP من مجلد أو ملف"""
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zip_ref:
                if os.path.isfile(source_path):
                    # ملف واحد
                    zip_ref.write(source_path, os.path.basename(source_path))
                    files_added = 1
                elif os.path.isdir(source_path):
                    # مجلد كامل
                    files_added = 0
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_path)
                            zip_ref.write(file_path, arcname)
                            files_added += 1
                else:
                    return {"success": False, "error": "المسار غير صحيح"}

            file_size = self.format_file_size(os.path.getsize(zip_path))
            print(f"✅ تم إنشاء ملف ZIP: {zip_path} ({file_size})")

            return {
                "success": True,
                "zip_path": zip_path,
                "files_added": files_added,
                "size": file_size
            }

        except Exception as e:
            print(f"❌ خطأ في إنشاء ملف ZIP: {e}")
            return {"success": False, "error": str(e)}

    def list_zip_contents(self, zip_path: str) -> dict:
        """عرض محتويات ملف ZIP دون فك الضغط"""
        try:
            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_info = []
                total_size = 0
                compressed_size = 0

                for info in zip_ref.infolist():
                    file_info.append({
                        "filename": info.filename,
                        "size": info.file_size,
                        "compressed_size": info.compress_size,
                        "date_time": datetime(*info.date_time).isoformat() if info.date_time else None,
                        "is_dir": info.is_dir()
                    })
                    total_size += info.file_size
                    compressed_size += info.compress_size

                compression_ratio = ((total_size - compressed_size) / total_size * 100) if total_size > 0 else 0

                return {
                    "success": True,
                    "files": file_info,
                    "total_files": len(file_info),
                    "total_size": self.format_file_size(total_size),
                    "compressed_size": self.format_file_size(compressed_size),
                    "compression_ratio": f"{compression_ratio:.1f}%"
                }

        except Exception as e:
            print(f"❌ خطأ في قراءة محتويات ZIP: {e}")
            return {"success": False, "error": str(e)}

    def extract_specific_files(self, zip_path: str, file_patterns: list, extract_to: str = None) -> dict:
        """فك ضغط ملفات معينة فقط من ZIP"""
        try:
            if extract_to is None:
                extract_to = "extracted_files"

            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            os.makedirs(extract_to, exist_ok=True)
            extracted_files = []

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # التحقق من تطابق النمط
                    for pattern in file_patterns:
                        if pattern in file_info.filename or file_info.filename.endswith(pattern):
                            zip_ref.extract(file_info, extract_to)
                            extracted_files.append(file_info.filename)
                            break

            print(f"✅ تم استخراج {len(extracted_files)} ملف متطابق")

            return {
                "success": True,
                "extracted_files": extracted_files,
                "extract_path": extract_to,
                "count": len(extracted_files)
            }

        except Exception as e:
            print(f"❌ خطأ في استخراج الملفات المحددة: {e}")
            return {"success": False, "error": str(e)}

    def validate_zip_integrity(self, zip_path: str) -> dict:
        """التحقق من سلامة ملف ZIP"""
        try:
            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # اختبار كل ملف
                corrupt_files = []
                tested_files = 0

                for file_info in zip_ref.infolist():
                    if not file_info.is_dir():
                        try:
                            # محاولة قراءة الملف
                            with zip_ref.open(file_info.filename) as f:
                                f.read()
                            tested_files += 1
                        except Exception as e:
                            corrupt_files.append({
                                "filename": file_info.filename,
                                "error": str(e)
                            })

                is_valid = len(corrupt_files) == 0

                return {
                    "success": True,
                    "is_valid": is_valid,
                    "tested_files": tested_files,
                    "corrupt_files": corrupt_files,
                    "status": "ملف سليم" if is_valid else f"وجد {len(corrupt_files)} ملف تالف"
                }

        except Exception as e:
            print(f"❌ خطأ في فحص سلامة ZIP: {e}")
            return {"success": False, "error": str(e)}

    def cleanup_old_backups(self, max_backups: int = 5):
        """تنظيف النسخ الاحتياطية القديمة"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                return

            # الحصول على جميع ملفات النسخ الاحتياطية
            backup_files = []
            for file in os.listdir(backup_dir):
                if file.startswith("backup_") and file.endswith(".zip"):
                    file_path = os.path.join(backup_dir, file)
                    backup_files.append((file_path, os.path.getctime(file_path)))

            # ترتيب حسب تاريخ الإنشاء (الأقدم أولاً)
            backup_files.sort(key=lambda x: x[1])

            # حذف الملفات الزائدة
            while len(backup_files) > max_backups:
                old_backup = backup_files.pop(0)
                os.remove(old_backup[0])
                print(f"🗑️ تم حذف نسخة احتياطية قديمة: {old_backup[0]}")

        except Exception as e:
            print(f"❌ خطأ في تنظيف النسخ الاحتياطية: {e}")

    def auto_extract_and_apply_updates(self):
        """فحص مجلد updates تلقائياً وتطبيق أي تحديثات جديدة مع التطبيق المباشر"""
        try:
            updates_dir = "updates"
            if not os.path.exists(updates_dir):
                return None

            # البحث عن ملفات ZIP جديدة
            zip_files = [f for f in os.listdir(updates_dir) if f.endswith('.zip')]

            if not zip_files:
                return None

            # ترتيب الملفات حسب تاريخ التعديل (الأحدث أولاً)
            zip_files_with_time = []
            for zip_file in zip_files:
                zip_path = os.path.join(updates_dir, zip_file)
                mod_time = os.path.getmtime(zip_path)
                zip_files_with_time.append((zip_file, mod_time, zip_path))

            zip_files_with_time.sort(key=lambda x: x[1], reverse=True)

            # تطبيق آخر ملف ZIP
            latest_zip = zip_files_with_time[0]
            zip_filename = latest_zip[0]
            zip_path = latest_zip[2]

            print(f"🔍 تم العثور على ملف تحديث جديد: {zip_filename}")

            # التحقق من أن هذا الملف لم يتم تطبيقه من قبل
            applied_files = self.get_applied_local_updates()
            if zip_filename in applied_files:
                print(f"⚠️ الملف {zip_filename} تم تطبيقه مسبقاً")
                return None

            # تطبيق التحديث التلقائي مع التطبيق المباشر
            result = self.auto_extract_and_apply_direct(zip_path, zip_filename)

            if result["success"]:
                print(f"✅ تم تطبيق التحديث التلقائي والمباشر من {zip_filename}")
                return {
                    "filename": zip_filename,
                    "result": result,
                    "message": f"تم تطبيق التحديث التلقائي والمباشر من {zip_filename}"
                }
            else:
                print(f"❌ فشل في تطبيق التحديث التلقائي: {result.get('error')}")
                return None

        except Exception as e:
            print(f"❌ خطأ في الفحص التلقائي للتحديثات: {e}")
            return None

    def auto_extract_and_apply_direct(self, zip_path: str, filename: str):
        """فك ضغط وتطبيق التحديث مباشرة بدون مجلدات مؤقتة"""
        try:
            # التحقق من صحة الملف
            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            print(f"🔄 بدء التطبيق المباشر للتحديث: {filename}")

            # إنشاء نسخة احتياطية
            backup_result = self.create_backup()
            if not backup_result["success"]:
                return {"success": False, "error": f"فشل في إنشاء النسخة الاحتياطية: {backup_result['error']}"}

            # تطبيق التحديث مباشرة
            update_result = self.extract_and_apply_update_direct(zip_path)

            if not update_result["success"]:
                # استعادة النسخة الاحتياطية في حالة الفشل
                self.restore_backup(backup_result["backup_path"])
                return {"success": False, "error": f"فشل في تطبيق التحديث: {update_result['error']}"}

            # تسجيل التحديث المطبق
            current_time = datetime.now().isoformat()
            local_update_data = {
                "id": f"auto_direct_update_{int(datetime.now().timestamp())}",
                "version": "تلقائي مباشر",
                "source": "تطبيق تلقائي مباشر من مجلد updates",
                "filename": filename,
                "applied_date": current_time,
                "backup_path": backup_result["backup_path"],
                "analysis": update_result.get("summary", {}),
                "report": update_result.get("report", ""),
                "auto_applied": True,
                "direct_application": True
            }

            # إضافة التحديث لسجل التحديثات المطبقة
            if "installed_updates" not in self.updates_data:
                self.updates_data["installed_updates"] = []

            self.updates_data["installed_updates"].append(local_update_data)
            self.save_updates_data()

            print(f"✅ تم التطبيق المباشر بنجاح لـ {filename}")

            return {
                "success": True,
                "message": f"تم التطبيق التلقائي المباشر من {filename}",
                "filename": filename,
                "backup_path": backup_result["backup_path"],
                "analysis": update_result.get("summary", {}),
                "report": update_result.get("report", ""),
                "direct_applied": True
            }

        except Exception as e:
            print(f"❌ خطأ في التطبيق المباشر للتحديث: {e}")
            return {"success": False, "error": str(e)}

    def extract_and_apply_update_direct(self, update_file_path: str) -> dict:
        """استخراج وتطبيق ملفات التحديث مباشرة مع تحليل متقدم"""
        try:
            update_summary = {
                "new_files": [],
                "updated_files": [],
                "new_features": [],
                "changes_detected": [],
                "total_applied": 0
            }

            print(f"🔄 بدء التطبيق المباشر من الملف: {update_file_path}")

            with zipfile.ZipFile(update_file_path, 'r') as update_zip:
                # التطبيق المباشر بدون استخراج لمجلد مؤقت
                for file_info in update_zip.infolist():
                    if file_info.is_dir():
                        continue

                    file_path = file_info.filename
                    # تحويل مسارات Windows لـ Unix
                    file_path = file_path.replace('\\', '/')

                    # التحقق من أن الملف مسموح بتحديثه
                    if self.is_file_updatable(file_path):
                        try:
                            # قراءة محتوى الملف من ZIP
                            with update_zip.open(file_info) as source_file:
                                file_content = source_file.read()

                            # التحقق من وجود الملف سابقاً
                            if os.path.exists(file_path):
                                update_summary["updated_files"].append(file_path)
                                print(f"🔄 تحديث مباشر: {file_path}")
                            else:
                                update_summary["new_files"].append(file_path)
                                print(f"✨ ملف جديد مباشر: {file_path}")

                            # إنشاء المجلد إذا لم يكن موجوداً
                            dest_dir = os.path.dirname(file_path)
                            if dest_dir:
                                os.makedirs(dest_dir, exist_ok=True)

                            # كتابة الملف مباشرة
                            with open(file_path, 'wb') as dest_file:
                                dest_file.write(file_content)

                            update_summary["total_applied"] += 1

                            # تحليل محتوى الملف للبحث عن ميزات جديدة
                            if file_path.endswith('.py'):
                                self._analyze_python_content(file_content.decode('utf-8', errors='ignore'), file_path, update_summary)

                        except Exception as file_error:
                            print(f"⚠️ خطأ في تطبيق الملف {file_path}: {file_error}")
                            continue

            # إنشاء تقرير التحديث
            self._create_update_report_direct(update_summary)

            print(f"✅ تم التطبيق المباشر لـ {update_summary['total_applied']} ملف")

            return {
                "success": True, 
                "summary": update_summary,
                "report": self._format_update_summary_direct(update_summary)
            }

        except Exception as e:
            print(f"❌ خطأ في التطبيق المباشر: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_python_content(self, content: str, file_path: str, summary: dict):
        """تحليل محتوى ملفات Python للبحث عن الميزات الجديدة"""
        try:
            import re

            # البحث عن أوامر جديدة
            command_patterns = re.findall(r'elif message == ["\']([^"\']+)["\']', content)
            for cmd in command_patterns:
                summary["new_features"].append(f"🎯 أمر جديد: {cmd} في {file_path}")

            # البحث عن دوال جديدة
            function_patterns = re.findall(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(', content)
            for func in function_patterns:
                if not func.startswith('_'):
                    summary["new_features"].append(f"🔧 دالة جديدة: {func}() في {file_path}")

            # البحث عن كلاسات جديدة
            class_patterns = re.findall(r'class ([A-Z][a-zA-Z0-9_]*)', content)
            for cls in class_patterns:
                summary["new_features"].append(f"📦 كلاس جديد: {cls} في {file_path}")

        except Exception as e:
            print(f"⚠️ خطأ في تحليل محتوى Python {file_path}: {e}")

    def _create_update_report_direct(self, summary: dict):
        """إنشاء تقرير مفصل عن التطبيق المباشر"""
        try:
            report_path = f"updates/direct_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs("updates", exist_ok=True)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("📋 تقرير التطبيق المباشر للتحديث\n")
                f.write("=" * 50 + "\n")
                f.write(f"⏰ وقت التطبيق: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"🔄 طريقة التطبيق: مباشرة (بدون مجلدات مؤقتة)\n\n")

                f.write(f"📁 الملفات الجديدة ({len(summary['new_files'])}):\n")
                for file in summary['new_files']:
                    f.write(f"  + {file}\n")
                f.write("\n")

                f.write(f"🔄 الملفات المحدثة ({len(summary['updated_files'])}):\n")
                for file in summary['updated_files']:
                    f.write(f"  ~ {file}\n")
                f.write("\n")

                f.write(f"✨ الميزات المكتشفة ({len(summary['new_features'])}):\n")
                for feature in summary['new_features']:
                    f.write(f"  {feature}\n")
                f.write("\n")

                f.write(f"📊 إجمالي الملفات المطبقة: {summary['total_applied']}\n")

            print(f"📄 تم إنشاء تقرير التطبيق المباشر: {report_path}")

        except Exception as e:
            print(f"⚠️ خطأ في إنشاء تقرير التطبيق المباشر: {e}")

    def _format_update_summary_direct(self, summary: dict) -> str:
        """تنسيق ملخص التطبيق المباشر للعرض"""
        lines = ["📋 ملخص التطبيق المباشر:"]

        lines.append(f"📊 إجمالي الملفات المطبقة: {summary['total_applied']}")

        if summary["new_files"]:
            lines.append(f"📁 ملفات جديدة: {len(summary['new_files'])}")

        if summary["updated_files"]:
            lines.append(f"🔄 ملفات محدثة: {len(summary['updated_files'])}")

        if summary["new_features"]:
            lines.append(f"✨ ميزات مكتشفة: {len(summary['new_features'])}")
            lines.append("🎯 أهم الإضافات:")
            for feature in summary["new_features"][:5]:
                lines.append(f"  • {feature}")

        lines.append("⚡ تم التطبيق مباشرة بدون مجلدات مؤقتة")

        return "\n".join(lines)

    def apply_local_update_file(self, zip_path: str, filename: str):
        """تطبيق تحديث محلي من ملف ZIP مع تحليل متقدم"""
        try:
            # التحقق من صحة الملف
            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            # إنشاء نسخة احتياطية
            backup_result = self.create_backup()
            if not backup_result["success"]:
                return {"success": False, "error": f"فشل في إنشاء النسخة الاحتياطية: {backup_result['error']}"}

            # تطبيق التحديث مع التحليل المتقدم
            update_result = self.extract_and_apply_update(zip_path)

            if not update_result["success"]:
                # استعادة النسخة الاحتياطية في حالة الفشل
                self.restore_backup(backup_result["backup_path"])
                return {"success": False, "error": f"فشل في تطبيق التحديث: {update_result['error']}"}

            # تسجيل التحديث المحلي مع تفاصيل التحليل
            current_time = datetime.now().isoformat()
            local_update_data = {
                "id": f"auto_local_update_{int(datetime.now().timestamp())}",
                "version": "تلقائي محلي",
                "source": "تطبيق تلقائي من مجلد updates",
                "filename": filename,
                "applied_date": current_time,
                "backup_path": backup_result["backup_path"],
                "analysis": update_result.get("summary", {}),
                "report": update_result.get("report", "")
            }

            # إضافة التحديث المحلي لسجل التحديثات المطبقة
            if "installed_updates" not in self.updates_data:
                self.updates_data["installed_updates"] = []

            self.updates_data["installed_updates"].append(local_update_data)
            self.save_updates_data()

            return {
                "success": True,
                "message": f"تم تطبيق التحديث التلقائي من {filename}",
                "filename": filename,
                "backup_path": backup_result["backup_path"],
                "analysis": update_result.get("summary", {}),
                "report": update_result.get("report", "")
            }

        except Exception as e:
            print(f"❌ خطأ في تطبيق التحديث المحلي: {e}")
            return {"success": False, "error": str(e)}

    def get_applied_local_updates(self):
        """الحصول على قائمة التحديثات المحلية المطبقة"""
        try:
            applied_files = []
            installed_updates = self.updates_data.get("installed_updates", [])

            for update in installed_updates:
                filename = update.get("filename")
                if filename:
                    applied_files.append(filename)

            return applied_files
        except:
            return []

    def apply_local_update(self, zip_filename: str):
        """فك ضغط وتحليل ملف ZIP (للاستخدام اليدوي)"""
        try:
            # البحث عن الملف في مجلد updates أو المجلد الرئيسي
            zip_paths = [
                f"updates/{zip_filename}",
                zip_filename,
                f"{zip_filename}.zip"
            ]

            zip_path = None
            for path in zip_paths:
                if os.path.exists(path):
                    zip_path = path
                    break

            if not zip_path:
                return f"❌ لم يتم العثور على الملف: {zip_filename}"

            # تطبيق التحديث
            result = self.apply_local_update_file(zip_path, zip_filename)

            if result["success"]:
                info = f"✅ {result['message']}\n"
                if result.get("report"):
                    info += f"\n📋 تقرير التحديث:\n{result['report']}"
                return info
            else:
                return f"❌ فشل في تطبيق التحديث: {result.get('error', 'خطأ غير معروف')}"

        except Exception as e:
            return f"❌ خطأ في تطبيق التحديث: {str(e)}"

    def extract_to_custom_folder(self, zip_filename: str, folder_name: str = None):
        """فك ضغط ملف ZIP في مجلد خاص دون تطبيق التحديث"""
        try:
            # البحث عن الملف في مجلد backups أو updates أو المجلد الرئيسي
            zip_paths = [
                f"backups/{zip_filename}",
                f"updates/{zip_filename}",
                zip_filename,
                f"backups/{zip_filename}.zip",
                f"updates/{zip_filename}.zip",
                f"{zip_filename}.zip"
            ]

            zip_path = None
            for path in zip_paths:
                if os.path.exists(path):
                    zip_path = path
                    break

            if not zip_path:
                return f"❌ لم يتم العثور على الملف: {zip_filename}"

            # تحديد اسم المجلد
            if not folder_name:
                # استخدام اسم الملف بدون امتداد مع timestamp
                base_name = os.path.splitext(os.path.basename(zip_filename))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder_name = f"extracted_{base_name}_{timestamp}"

            # إنشاء مجلد الاستخراج
            extract_path = f"extracted_files/{folder_name}"
            os.makedirs(extract_path, exist_ok=True)

            # فك الضغط مع التحليل
            analysis_result = self.extract_and_analyze_zip(zip_path, extract_path)

            if analysis_result["success"]:
                return f"""✅ تم فك ضغط الملف بنجاح!

📁 مسار الاستخراج: {extract_path}
📊 عدد الملفات: {analysis_result['files_count']}
📂 المجلدات: {analysis_result['folders_count']}
💾 الحجم الإجمالي: {analysis_result['total_size']}

🔍 تحليل المحتوى:
{analysis_result['analysis_summary']}

📝 ملاحظة: الملفات مُستخرجة في مجلد منفصل ولم يتم تطبيقها على النظام."""
            else:
                return f"❌ فشل في فك الضغط: {analysis_result.get('error', 'خطأ غير معروف')}"

        except Exception as e:
            return f"❌ خطأ في فك الضغط: {str(e)}"

    def extract_and_analyze_zip(self, zip_path: str, extract_path: str):
        """فك ضغط وتحليل محتويات ملف ZIP"""
        try:
            if not zipfile.is_zipfile(zip_path):
                return {"success": False, "error": "الملف ليس ملف ZIP صحيح"}

            analysis_summary = {
                "python_files": [],
                "html_files": [],
                "js_files": [],
                "json_files": [],
                "other_files": [],
                "new_features": []
            }

            files_count = 0
            folders_count = 0
            total_size = 0

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # استخراج جميع الملفات
                zip_ref.extractall(extract_path)

                # تحليل المحتويات
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        folders_count += 1
                    else:
                        files_count += 1
                        total_size += file_info.file_size

                        # تصنيف الملفات
                        filename = file_info.filename.lower()
                        if filename.endswith('.py'):
                            analysis_summary["python_files"].append(file_info.filename)
                            # تحليل ملف Python
                            try:
                                with zip_ref.open(file_info) as f:
                                    content = f.read().decode('utf-8', errors='ignore')
                                    self._analyze_python_content_for_display(content, file_info.filename, analysis_summary)
                            except:
                                pass
                        elif filename.endswith(('.html', '.htm')):
                            analysis_summary["html_files"].append(file_info.filename)
                        elif filename.endswith('.js'):
                            analysis_summary["js_files"].append(file_info.filename)
                        elif filename.endswith('.json'):
                            analysis_summary["json_files"].append(file_info.filename)
                        else:
                            analysis_summary["other_files"].append(file_info.filename)

            # تنسيق ملخص التحليل
            summary_text = self._format_analysis_summary(analysis_summary)

            return {
                "success": True,
                "files_count": files_count,
                "folders_count": folders_count,
                "total_size": self.format_file_size(total_size),
                "analysis_summary": summary_text,
                "extract_path": extract_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_python_content_for_display(self, content: str, file_path: str, summary: dict):
        """تحليل محتوى ملفات Python للعرض"""
        try:
            import re

            # البحث عن أوامر جديدة
            command_patterns = re.findall(r'elif message == ["\']([^"\']+)["\']', content)
            for cmd in command_patterns:
                summary["new_features"].append(f"🎯 أمر: {cmd} في {file_path}")

            # البحث عن دوال جديدة
            function_patterns = re.findall(r'def ([a-zA-Z_][a-zA-Z0-9_]*)\(', content)
            for func in function_patterns[:5]:  # أول 5 دوال فقط
                if not func.startswith('_'):
                    summary["new_features"].append(f"🔧 دالة: {func}() في {file_path}")

            # البحث عن كلاسات جديدة
            class_patterns = re.findall(r'class ([A-Z][a-zA-Z0-9_]*)', content)
            for cls in class_patterns:
                summary["new_features"].append(f"📦 كلاس: {cls} في {file_path}")

        except:
            pass

    def _format_analysis_summary(self, analysis: dict) -> str:
        """تنسيق ملخص التحليل للعرض"""
        lines = []

        if analysis["python_files"]:
            lines.append(f"🐍 ملفات Python: {len(analysis['python_files'])}")
            for file in analysis["python_files"][:3]:
                lines.append(f"   • {file}")
            if len(analysis["python_files"]) > 3:
                lines.append(f"   • ... و {len(analysis['python_files']) - 3} ملف آخر")

        if analysis["html_files"]:
            lines.append(f"🌐 ملفات HTML: {len(analysis['html_files'])}")

        if analysis["js_files"]:
            lines.append(f"⚙️ ملفات JavaScript: {len(analysis['js_files'])}")

        if analysis["json_files"]:
            lines.append(f"📄 ملفات JSON: {len(analysis['json_files'])}")

        if analysis["other_files"]:
            lines.append(f"📁 ملفات أخرى: {len(analysis['other_files'])}")

        if analysis["new_features"]:
            lines.append(f"\n✨ المميزات المكتشفة:")
            for feature in analysis["new_features"][:8]:  # أول 8 ميزات
                lines.append(f"   • {feature}")
            if len(analysis["new_features"]) > 8:
                lines.append(f"   • ... و {len(analysis['new_features']) - 8} ميزة أخرى")

        return "\n".join(lines) if lines else "لا توجد معلومات تحليل متاحة"

    def list_extracted_folders(self):
        """عرض قائمة المجلدات المُستخرجة"""
        try:
            extracted_dir = "extracted_files"
            if not os.path.exists(extracted_dir):
                return "❌ لا توجد مجلدات مُستخرجة"

            folders = [f for f in os.listdir(extracted_dir) if os.path.isdir(os.path.join(extracted_dir, f))]

            if not folders:
                return "❌ لا توجد مجلدات مُستخرجة"

            # ترتيب المجلدات حسب تاريخ الإنشاء (الأحدث أولاً)
            folders_with_time = []
            for folder in folders:
                folder_path = os.path.join(extracted_dir, folder)
                create_time = os.path.getctime(folder_path)
                folders_with_time.append((folder, create_time))

            folders_with_time.sort(key=lambda x: x[1], reverse=True)

            result = "📁 المجلدات المُستخرجة:\n"
            for i, (folder, create_time) in enumerate(folders_with_time, 1):
                folder_path = os.path.join(extracted_dir, folder)
                
                # حساب عدد الملفات
                file_count = 0
                for root, dirs, files in os.walk(folder_path):
                    file_count += len(files)

                # تنسيق التاريخ
                create_date = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M")
                
                result += f"{i}. 📂 {folder}\n"
                result += f"   📅 تاريخ الإنشاء: {create_date}\n"
                result += f"   📄 عدد الملفات: {file_count}\n"

            return result.strip()

        except Exception as e:
            return f"❌ خطأ في عرض المجلدات: {str(e)}"