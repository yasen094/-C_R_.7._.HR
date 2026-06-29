
"""
مدير AI Assistant المتقدم باستخدام Google Gemini
يوفر واجهة ذكية لإنشاء الأوامر وإصلاح الأخطاء
"""
import os
import json
import re
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class AIAssistantManager:
    def __init__(self):
        self.gemini_client = None
        self.model_name = "gemini-2.0-flash"
        self.conversation_history = []
        self.pending_code_changes = {}
        
        # تهيئة Google Gemini AI
        self._initialize_gemini()
        
        # مسارات الملفات المهمة
        self.project_structure = {
            "main.py": "الملف الرئيسي للبوت",
            "run.py": "ملف تشغيل الخادم والبوت", 
            "modules/": "مجلد الوحدات والمكونات",
            "templates/": "قوالب HTML للواجهات",
            "static/": "ملفات CSS و JavaScript",
            "data/": "ملفات البيانات والإعدادات"
        }
        
        print("🤖 تم تهيئة AI Assistant Manager مع Google Gemini")

    def _initialize_gemini(self):
        """تهيئة عميل Google Gemini AI"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("⚠️ لم يتم العثور على GEMINI_API_KEY")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_client = genai.GenerativeModel(self.model_name)
            
            # اختبار الاتصال
            test_response = self.gemini_client.generate_content("مرحبا")
            if test_response:
                print("✅ تم تهيئة Google Gemini AI للمساعد بنجاح!")
            
        except Exception as e:
            print(f"❌ خطأ في تهيئة Google Gemini AI: {e}")

    def process_request(self, user_message: str, history: List[Dict] = None) -> Dict:
        """معالجة طلب المستخدم وإنتاج الرد مع التغييرات المطلوبة"""
        try:
            if not self.gemini_client:
                return {
                    "success": False,
                    "error": "Google Gemini AI غير متاح حالياً"
                }

            # إنشاء prompt متقدم للمساعد
            system_prompt = self._create_assistant_prompt()
            
            # إضافة السياق والتاريخ
            conversation_context = self._build_conversation_context(history or [])
            
            # تحليل نوع الطلب
            request_type = self._analyze_request_type(user_message)
            
            # إنشاء الـ prompt النهائي
            full_prompt = f"""
{system_prompt}

=== نوع الطلب المتوقع ===
{request_type}

=== تاريخ المحادثة ===
{conversation_context}

=== طلب المستخدم الحالي ===
{user_message}

=== تعليمات خاصة ===
1. إذا كان الطلب يتطلب إنشاء أو تعديل كود، قدم الكود كاملاً
2. اشرح ما تفعله بوضوح
3. اقترح التحسينات المناسبة
4. استخدم أفضل الممارسات في البرمجة
5. تأكد من توافق الكود مع البنية الحالية

يرجى الرد بتنسيق JSON التالي:
{{
    "response": "الرد النصي للمستخدم",
    "code_changes": [
        {{
            "file_path": "مسار الملف",
            "content": "محتوى الكود الجديد أو المحدث",
            "description": "وصف التغيير",
            "change_type": "create/modify/insert/delete/replace",
            "old_content": "النص المراد استبداله (للتعديل فقط)",
            "line_number": "رقم السطر للإدراج (للإدراج فقط)",
            "start_line": "السطر الأول للحذف (للحذف فقط)",
            "end_line": "السطر الأخير للحذف (للحذف فقط)"
        }}
    ],
    "explanation": "شرح مفصل للتغييرات"
}}

=== أنواع التغييرات المتاحة ===
- create: إنشاء ملف جديد
- modify: تعديل جزء من الكود الموجود (يتطلب old_content)
- insert: إدراج كود في سطر محدد (يتطلب line_number)
- delete: حذف أسطر محددة (يتطلب start_line وend_line)
- replace: استبدال كامل للملف
"""

            # إرسال الطلب إلى Gemini
            response = self.gemini_client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 2000,
                }
            )

            if not response or not response.text:
                return {
                    "success": False,
                    "error": "لم أتمكن من إنتاج رد مناسب"
                }

            # معالجة الرد
            return self._process_gemini_response(response.text, user_message)

        except Exception as e:
            print(f"❌ خطأ في معالجة طلب AI Assistant: {e}")
            return {
                "success": False,
                "error": f"خطأ في المعالجة: {str(e)}"
            }

    def _create_assistant_prompt(self) -> str:
        """إنشاء prompt متقدم للمساعد"""
        return f"""أنت AI Assistant متقدم متخصص في تطوير بوت Highrise باستخدام Python.

=== هويتك ومهامك ===
- مطور بوت محترف ومساعد ذكي
- خبير في Python، Flask، والبرمجة المتقدمة
- تساعد في إنشاء أوامر جديدة وإصلاح الأخطاء
- تطور ميزات جديدة وتحسن الأداء

=== معرفتك بالمشروع ===
- بوت Highrise مطور بـ Python
- يستخدم Flask للواجهات الويب
- هيكل المشروع: {json.dumps(self.project_structure, ensure_ascii=False)}
- يحتوي على أوامر للمستخدمين والمشرفين
- يدعم الرقصات، التنقل، وإدارة المستخدمين

=== قدراتك المتقدمة ===
✅ إنشاء أوامر مخصصة جديدة
✅ إصلاح الأخطاء تلقائياً
✅ تطوير ميزات جديدة
✅ تحسين الأداء والكود
✅ إنشاء واجهات ويب
✅ شرح الكود بالتفصيل
✅ النسخ الاحتياطي التلقائي

=== إرشادات الكود ===
- استخدم أفضل الممارسات في Python
- اتبع النمط الحالي للمشروع
- أضف تعليقات واضحة بالعربية
- تأكد من التوافق مع الوحدات الموجودة
- اختبر الكود قبل التطبيق

=== نمط الردود ===
- اشرح ما تفعله بوضوح
- قدم الكود كاملاً قابل للتطبيق
- اقترح تحسينات إضافية
- استخدم اللغة العربية بشكل طبيعي"""

    def _build_conversation_context(self, history: List[Dict]) -> str:
        """بناء سياق المحادثة من التاريخ"""
        if not history:
            return "لا يوجد تاريخ محادثة سابق"
        
        context_lines = []
        for msg in history[-6:]:  # آخر 6 رسائل
            role = "المستخدم" if msg.get('role') == 'user' else "المساعد"
            content = msg.get('content', '')[:200]  # أول 200 حرف
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)

    def _analyze_request_type(self, message: str) -> str:
        """تحليل نوع الطلب من الرسالة"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["أنشئ", "اعمل", "أضف", "صمم", "أريد"]):
            return "إنشاء أو إضافة جديدة"
        elif any(word in message_lower for word in ["أصلح", "خطأ", "مشكلة", "لا يعمل", "فشل"]):
            return "إصلاح خطأ أو مشكلة"
        elif any(word in message_lower for word in ["حسن", "طور", "أداء", "سرعة", "تحديث"]):
            return "تحسين وتطوير"
        elif any(word in message_lower for word in ["اشرح", "كيف", "ما هو", "وضح"]):
            return "شرح وتوضيح"
        elif any(word in message_lower for word in ["واجهة", "صفحة", "html", "css"]):
            return "تطوير واجهة ويب"
        else:
            return "طلب عام أو استفسار"

    def _process_gemini_response(self, response_text: str, original_request: str) -> Dict:
        """معالجة رد Gemini واستخراج المعلومات"""
        try:
            # محاولة استخراج JSON من الرد
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed_response = json.loads(json_match.group())
                    
                    # تخزين التغييرات المقترحة
                    change_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if 'code_changes' in parsed_response and parsed_response['code_changes']:
                        self.pending_code_changes[change_id] = parsed_response['code_changes']
                    
                    return {
                        "success": True,
                        "response": parsed_response.get('response', 'تم إنتاج الرد بنجاح'),
                        "code_changes": parsed_response.get('code_changes', []),
                        "explanation": parsed_response.get('explanation', ''),
                        "change_id": change_id
                    }
                    
                except json.JSONDecodeError:
                    pass
            
            # إذا لم يكن JSON، معالجة كنص عادي
            return {
                "success": True,
                "response": response_text,
                "code_changes": [],
                "explanation": "رد نصي من AI Assistant"
            }
            
        except Exception as e:
            print(f"❌ خطأ في معالجة رد Gemini: {e}")
            return {
                "success": False,
                "error": f"خطأ في معالجة الرد: {str(e)}"
            }

    def apply_code_changes(self, change_id: str, file_path: str) -> Dict:
        """تطبيق التغييرات على الملفات"""
        try:
            if change_id not in self.pending_code_changes:
                return {
                    "success": False,
                    "error": "لم يتم العثور على التغييرات المطلوبة"
                }
            
            changes = self.pending_code_changes[change_id]
            target_change = None
            
            # البحث عن التغيير المطلوب
            for change in changes:
                if change.get('file_path') == file_path:
                    target_change = change
                    break
            
            if not target_change:
                return {
                    "success": False,
                    "error": f"لم يتم العثور على تغيير للملف {file_path}"
                }
            
            # إنشاء نسخة احتياطية
            backup_result = self._create_backup(file_path)
            if not backup_result["success"]:
                return backup_result
            
            # تطبيق التغيير حسب النوع
            try:
                change_type = target_change.get('change_type', 'create')
                
                if change_type == 'modify':
                    return self._apply_modification(file_path, target_change)
                elif change_type == 'insert':
                    return self._apply_insertion(file_path, target_change)
                elif change_type == 'delete':
                    return self._apply_deletion(file_path, target_change)
                else:  # create or replace
                    return self._apply_replacement(file_path, target_change)
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"فشل في تطبيق التغيير: {str(e)}"
                }
            
        except Exception as e:
            print(f"❌ خطأ في تطبيق التغييرات: {e}")
            return {
                "success": False,
                "error": f"خطأ في تطبيق التغيير: {str(e)}"
            }

    def _apply_modification(self, file_path: str, change: Dict) -> Dict:
        """تطبيق تعديل على جزء من الكود"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"الملف {file_path} غير موجود للتعديل"
                }
            
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # البحث عن النص المراد استبداله
            old_text = change.get('old_content', '')
            new_text = change.get('content', '')
            
            if not old_text:
                return {
                    "success": False,
                    "error": "لم يتم تحديد النص المراد استبداله"
                }
            
            # التحقق من وجود النص المراد استبداله
            if old_text not in current_content:
                return {
                    "success": False,
                    "error": f"لم يتم العثور على النص المحدد في الملف"
                }
            
            # استبدال النص
            updated_content = current_content.replace(old_text, new_text, 1)  # استبدال أول تطابق فقط
            
            # كتابة المحتوى المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ تم تعديل الملف {file_path}")
            
            return {
                "success": True,
                "message": f"تم تعديل {file_path} بنجاح",
                "change_type": "modification"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في تعديل الملف: {str(e)}"
            }

    def _apply_insertion(self, file_path: str, change: Dict) -> Dict:
        """إدراج كود في سطر محدد"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"الملف {file_path} غير موجود للإدراج"
                }
            
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # الحصول على رقم السطر والكود المراد إدراجه
            line_number = change.get('line_number', len(lines))
            new_code = change.get('content', '')
            
            # التأكد من أن رقم السطر صحيح
            if line_number < 0:
                line_number = 0
            elif line_number > len(lines):
                line_number = len(lines)
            
            # إدراج الكود في السطر المحدد
            if not new_code.endswith('\n'):
                new_code += '\n'
            
            lines.insert(line_number, new_code)
            
            # كتابة المحتوى المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ تم إدراج الكود في السطر {line_number} في الملف {file_path}")
            
            return {
                "success": True,
                "message": f"تم إدراج الكود في السطر {line_number} في {file_path}",
                "change_type": "insertion",
                "line_number": line_number
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في إدراج الكود: {str(e)}"
            }

    def _apply_deletion(self, file_path: str, change: Dict) -> Dict:
        """حذف سطر أو مجموعة أسطر"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"الملف {file_path} غير موجود للحذف"
                }
            
            # قراءة الملف الحالي
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # الحصول على أرقام الأسطر المراد حذفها
            start_line = change.get('start_line', 0)
            end_line = change.get('end_line', start_line)
            
            # التأكد من صحة أرقام الأسطر
            if start_line < 0 or start_line >= len(lines):
                return {
                    "success": False,
                    "error": f"رقم السطر {start_line} غير صحيح"
                }
            
            if end_line < start_line or end_line >= len(lines):
                end_line = start_line
            
            # حذف الأسطر المحددة
            del lines[start_line:end_line + 1]
            
            # كتابة المحتوى المحدث
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            deleted_count = end_line - start_line + 1
            print(f"✅ تم حذف {deleted_count} سطر من الملف {file_path}")
            
            return {
                "success": True,
                "message": f"تم حذف {deleted_count} سطر من {file_path}",
                "change_type": "deletion",
                "deleted_lines": deleted_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في حذف الأسطر: {str(e)}"
            }

    def _apply_replacement(self, file_path: str, change: Dict) -> Dict:
        """استبدال كامل للملف أو إنشاء ملف جديد"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # كتابة المحتوى الجديد
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(change['content'])
            
            print(f"✅ تم استبدال/إنشاء الملف {file_path}")
            
            return {
                "success": True,
                "message": f"تم تطبيق التغيير على {file_path} بنجاح",
                "change_type": "replacement"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"فشل في كتابة الملف: {str(e)}"
            }

    def _create_backup(self, file_path: str) -> Dict:
        """إنشاء نسخة احتياطية من الملف"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": True,
                    "message": "ملف جديد - لا حاجة للنسخة الاحتياطية",
                    "backup_path": None
                }
            
            # إنشاء مجلد النسخ الاحتياطية
            backup_dir = "backups/ai_assistant"
            os.makedirs(backup_dir, exist_ok=True)
            
            # إنشاء اسم الملف الاحتياطي
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, f"{timestamp}_{file_name}")
            
            # نسخ الملف
            shutil.copy2(file_path, backup_path)
            
            return {
                "success": True,
                "message": f"تم إنشاء نسخة احتياطية: {backup_path}",
                "backup_path": backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"فشل في إنشاء النسخة الاحتياطية: {str(e)}"
            }

    def read_file_with_line_numbers(self, file_path: str) -> Dict:
        """قراءة محتوى ملف مع عرض أرقام الأسطر"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"الملف {file_path} غير موجود"
                }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # إنشاء محتوى مع أرقام الأسطر
            numbered_content = ""
            for i, line in enumerate(lines, 1):
                numbered_content += f"{i:4d} | {line}"
            
            return {
                "success": True,
                "file_path": file_path,
                "content": numbered_content,
                "total_lines": len(lines),
                "raw_lines": lines
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في قراءة الملف: {str(e)}"
            }

    def find_code_in_file(self, file_path: str, search_text: str) -> Dict:
        """البحث عن كود محدد في الملف وإرجاع رقم السطر"""
        try:
            file_data = self.read_file_with_line_numbers(file_path)
            if not file_data["success"]:
                return file_data
            
            lines = file_data["raw_lines"]
            found_lines = []
            
            for i, line in enumerate(lines, 1):
                if search_text.strip() in line.strip():
                    found_lines.append({
                        "line_number": i,
                        "content": line.strip(),
                        "full_line": f"{i:4d} | {line}"
                    })
            
            return {
                "success": True,
                "file_path": file_path,
                "search_text": search_text,
                "found_lines": found_lines,
                "total_matches": len(found_lines)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في البحث: {str(e)}"
            }

    def get_project_status(self) -> Dict:
        """الحصول على حالة المشروع الحالية"""
        try:
            status = {
                "files_count": 0,
                "modules_count": 0,
                "templates_count": 0,
                "data_files_count": 0,
                "recent_changes": [],
                "ai_capabilities": "Google Gemini AI متصل" if self.gemini_client else "AI غير متاح"
            }
            
            # عدد الملفات في كل مجلد
            for root, dirs, files in os.walk("."):
                if "modules" in root:
                    status["modules_count"] += len([f for f in files if f.endswith('.py')])
                elif "templates" in root:
                    status["templates_count"] += len([f for f in files if f.endswith('.html')])
                elif "data" in root:
                    status["data_files_count"] += len([f for f in files if f.endswith('.json')])
                
                status["files_count"] += len(files)
            
            return {
                "success": True,
                "status": status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في الحصول على حالة المشروع: {str(e)}"
            }

    def analyze_code_quality(self, file_path: str = None) -> Dict:
        """تحليل جودة الكود وإعطاء اقتراحات"""
        try:
            if not self.gemini_client:
                return {
                    "success": False,
                    "error": "Google Gemini AI غير متاح للتحليل"
                }
            
            # تحديد الملفات للتحليل
            files_to_analyze = []
            if file_path:
                if os.path.exists(file_path):
                    files_to_analyze.append(file_path)
            else:
                # تحليل الملفات الرئيسية
                main_files = ["main.py", "run.py", "modules/commands_handler.py"]
                files_to_analyze = [f for f in main_files if os.path.exists(f)]
            
            if not files_to_analyze:
                return {
                    "success": False,
                    "error": "لا توجد ملفات للتحليل"
                }
            
            analysis_results = []
            
            for file in files_to_analyze:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # تحليل الكود باستخدام Gemini
                    analysis_prompt = f"""
حلل هذا الكود واعطني تقرير مفصل:

ملف: {file}

```python
{code_content[:2000]}  # أول 2000 حرف
```

قدم التحليل في شكل:
1. نقاط القوة
2. المشاكل المحتملة  
3. اقتراحات التحسين
4. أفضل الممارسات المفقودة
5. تقييم الأداء (1-10)
"""
                    
                    response = self.gemini_client.generate_content(analysis_prompt)
                    
                    if response and response.text:
                        analysis_results.append({
                            "file": file,
                            "analysis": response.text
                        })
                    
                except Exception as e:
                    analysis_results.append({
                        "file": file,
                        "error": f"خطأ في تحليل {file}: {str(e)}"
                    })
            
            return {
                "success": True,
                "analysis": analysis_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في تحليل جودة الكود: {str(e)}"
            }

# إنشاء مثيل المدير
ai_assistant_manager = AIAssistantManager()
