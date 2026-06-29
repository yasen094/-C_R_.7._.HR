"""
مدير الذكاء الاصطناعي المتقدم للدردشة
نظام ذكي متطور يستخدم Google Gemini AI لفهم الرسائل وتوليد ردود ذكية
"""
import json
import os
import re
import random
import datetime
from typing import Dict, List, Optional, Tuple
import difflib
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

import json
import os
import random
import re
import datetime
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import inspect
import importlib

class AIAdvancedChatManager:
    def __init__(self, highrise, user_manager, bot_instance=None):
        self.highrise = highrise
        self.user_manager = user_manager
        self.bot_instance = bot_instance
        self.conversations_file = "data/ai_conversations.json"
        self.memory_file = "data/ai_memory.json"
        self.responses_file = "data/ai_responses.json"
        self.users_file = "data/ai_users.json"
        self.advanced_config_file = "data/ai_advanced_config.json"

        # تحميل البيانات
        self.conversations = self.load_conversations()
        self.memory = self.load_memory()
        self.responses = self.load_responses()
        self.ai_users = self.load_ai_users()
        self.advanced_config = self.load_advanced_config()

        # إعدادات الذكاء الاصطناعي المتقدمة
        self.ai_capabilities = {
            'execute_commands': True,
            'access_code': True,
            'read_user_data': True,
            'analyze_room': True,
            'manage_users': True,
            'system_info': True
        }

        # قاموس الأوامر المتاحة للذكاء الاصطناعي
        self.ai_available_commands = self._load_available_commands()

        print("🤖 مدير الذكاء الاصطناعي المتقدم جاهز مع صلاحيات شاملة")

    def _load_available_commands(self) -> Dict:
        """تحميل قائمة الأوامر المتاحة للذكاء الاصطناعي"""
        commands = {
            # أوامر المستخدمين العاديين
            'user_commands': [
                'رقص', 'توقف', 'الوقت', 'معلومات', 'احصائيات', 'عدد', 
                'ايه_الوضع', 'help', 'اوامر', 'رقصة_عشوائية'
            ],
            # أوامر المشرفين
            'moderator_commands': [
                'هات', 'اطرد', 'ثبت', 'الغ_ثبت', 'بدل_مكان', 'بدل_بين',
                'امان', 'تحذير', 'حالة_مشرفين', 'قائمة_المستخدمين'
            ],
            # أوامر المطورين
            'developer_commands': [
                'انتقال_سري', 'رقص_البوت', 'تغيير_اسم_البوت', 'وضع_هادئ',
                'استدعاء_جميع_المستخدمين', 'تطبيق_زي', 'حفظ_زي'
            ],
            # أوامر النظام (للذكاء الاصطناعي فقط)
            'system_commands': [
                'get_room_info', 'get_user_list', 'get_moderators',
                'analyze_chat_logs', 'get_bot_status', 'check_permissions'
            ]
        }
        return commands

    def load_advanced_config(self) -> Dict:
        """تحميل إعدادات الذكاء الاصطناعي المتقدمة"""
        if os.path.exists(self.advanced_config_file):
            try:
                with open(self.advanced_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # إعدادات افتراضية
        default_config = {
            'ai_personality': {
                'name': 'مساعد EDX الذكي',
                'role': 'مساعد بوت متقدم',
                'personality_traits': [
                    'ذكي ومفيد',
                    'ودود ومتفهم',
                    'محترف في التعامل',
                    'سريع الاستجابة'
                ]
            },
            'capabilities': {
                'command_execution': True,
                'code_analysis': True,
                'user_management': True,
                'system_monitoring': True,
                'advanced_responses': True
            },
            'response_settings': {
                'max_length': 200,
                'use_emojis': True,
                'formal_tone': False,
                'include_examples': True
            }
        }

        self.save_advanced_config(default_config)
        return default_config

    def save_advanced_config(self, config: Dict):
        """حفظ إعدادات الذكاء الاصطناعي المتقدمة"""
        try:
            with open(self.advanced_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ إعدادات الذكاء الاصطناعي: {e}")

    async def get_room_analysis(self) -> Dict:
        """تحليل شامل للغرفة مع معلومات مفصلة"""
        try:
            analysis = {
                'timestamp': datetime.datetime.now().isoformat(),
                'users': [],
                'moderators': [],
                'bot_status': 'active',
                'room_activity': 'normal',
                'total_users': 0,
                'user_types': {'visitors': 0, 'members': 0, 'moderators': 0}
            }

            # الحصول على قائمة المستخدمين
            if hasattr(self.highrise, 'get_room_users'):
                try:
                    room_users = await self.highrise.get_room_users()
                    analysis['total_users'] = len(room_users.content)
                    
                    for user, position in room_users.content:
                        user_info = {
                            'id': user.id,
                            'username': user.username,
                            'position': {
                                'x': position.x,
                                'y': position.y,
                                'z': position.z
                            }
                        }
                        
                        # تحديد نوع المستخدم
                        if self.user_manager:
                            if hasattr(self.user_manager, 'is_moderator') and self.user_manager.is_moderator(user.username):
                                user_info['type'] = 'moderator'
                                analysis['moderators'].append(user.username)
                                analysis['user_types']['moderators'] += 1
                            elif hasattr(self.user_manager, 'is_owner') and self.user_manager.is_owner(user.username):
                                user_info['type'] = 'owner'
                                analysis['moderators'].append(f"{user.username} (مالك)")
                                analysis['user_types']['moderators'] += 1
                            else:
                                user_info['type'] = 'visitor'
                                analysis['user_types']['visitors'] += 1
                        else:
                            user_info['type'] = 'unknown'
                            analysis['user_types']['visitors'] += 1
                            
                        analysis['users'].append(user_info)
                        
                    # تحديد مستوى النشاط
                    if analysis['total_users'] > 10:
                        analysis['room_activity'] = 'مزدحمة'
                    elif analysis['total_users'] > 5:
                        analysis['room_activity'] = 'نشطة'
                    else:
                        analysis['room_activity'] = 'هادئة'
                        
                except Exception as e:
                    print(f"خطأ في الحصول على بيانات الغرفة: {e}")
                    analysis['error'] = str(e)

            return analysis

        except Exception as e:
            print(f"خطأ في تحليل الغرفة: {e}")
            return {'error': str(e), 'timestamp': datetime.datetime.now().isoformat()}

    async def execute_ai_command(self, command: str, user_id: str, username: str) -> Dict:
        """تنفيذ أمر من الذكاء الاصطناعي مع صلاحيات كاملة وفعلية"""
        try:
            result = {'success': False, 'message': '', 'data': None}

            # تحليل الأمر
            command_parts = command.strip().split()
            if not command_parts:
                return {'success': False, 'message': 'أمر فارغ'}

            base_command = command_parts[0]
            print(f"🤖 الذكاء الاصطناعي ينفذ أمر: {base_command}")

            # أوامر النظام الخاصة بالذكاء الاصطناعي مع وصول مباشر
            if base_command in ['get_room_info', 'معلومات_الغرفة', 'room_info']:
                analysis = await self.get_room_analysis_direct()
                result = {
                    'success': True,
                    'message': 'تم تحليل الغرفة بنجاح',
                    'data': analysis
                }

            elif base_command in ['get_user_list', 'قائمة_المستخدمين', 'users']:
                users_data = await self.get_all_users_info_direct()
                result = {
                    'success': True,
                    'message': f'تم العثور على {len(users_data)} مستخدم',
                    'data': users_data
                }

            elif base_command in ['get_moderators', 'المشرفين', 'moderators']:
                moderators = await self.get_moderators_list_direct()
                result = {
                    'success': True,
                    'message': f'المشرفون الحاليون: {len(moderators)}',
                    'data': moderators
                }

            elif base_command in ['analyze_chat_logs', 'تحليل_السجلات']:
                logs_analysis = self.analyze_recent_chat_logs()
                result = {
                    'success': True,
                    'message': 'تم تحليل سجلات الدردشة',
                    'data': logs_analysis
                }

            elif base_command in ['get_bot_status', 'حالة_النظام', 'status']:
                bot_status = await self.get_bot_system_status_direct()
                result = {
                    'success': True,
                    'message': 'حالة البوت',
                    'data': bot_status
                }

            elif base_command in ['get_code_analysis', 'تحليل_الكود', 'code_info']:
                code_analysis = self.get_code_analysis_direct()
                result = {
                    'success': True,
                    'message': 'تم تحليل الكود بنجاح',
                    'data': code_analysis
                }

            elif base_command in ['count_users', 'عدد_المستخدمين']:
                count_result = await self.count_users_direct()
                result = count_result

            elif base_command in ['execute_bot_command', 'تنفيذ_أمر']:
                if len(command_parts) > 1:
                    bot_command = ' '.join(command_parts[1:])
                    execution_result = await self.execute_real_bot_command(bot_command, user_id, username)
                    result = execution_result
                else:
                    result = {
                        'success': False,
                        'message': 'يجب تحديد الأمر المراد تنفيذه'
                    }

            # تنفيذ أوامر البوت العادية مع وصول مباشر
            else:
                execution_result = await self.execute_real_bot_command(command, user_id, username)
                result = execution_result

            print(f"🤖 نتيجة تنفيذ الأمر: {result['success']}")
            return result

        except Exception as e:
            print(f"❌ خطأ في execute_ai_command: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الأمر: {str(e)}'
            }

    async def _execute_bot_command(self, command: str, user_id: str, username: str) -> Dict:
        """تنفيذ أمر عبر نظام البوت"""
        try:
            # إنشاء كائن مستخدم وهمي للذكاء الاصطناعي
            class AIUser:
                def __init__(self, user_id, username):
                    self.id = user_id
                    self.username = f"AI-{username}"

            ai_user = AIUser(user_id, username)

            # تنفيذ الأمر عبر معالج الأوامر
            if hasattr(self.bot_instance, 'commands_handler'):
                success = await self.bot_instance.commands_handler.process_command(
                    ai_user, command, source='ai_chat'
                )

                if success:
                    return {
                        'success': True,
                        'message': f'تم تنفيذ الأمر: {command}'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'فشل في تنفيذ الأمر: {command}'
                    }

            return {
                'success': False,
                'message': 'معالج الأوامر غير متاح'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في تنفيذ أمر البوت: {str(e)}'
            }

    def get_all_users_info(self) -> List[Dict]:
        """الحصول على معلومات جميع المستخدمين"""
        try:
            users_info = []

            # قراءة بيانات المستخدمين
            if os.path.exists("data/users_data.json"):
                with open("data/users_data.json", 'r', encoding='utf-8') as f:
                    users_data = json.load(f)

                for user_id, data in users_data.items():
                    user_info = {
                        'id': user_id,
                        'username': data.get('username', 'غير معروف'),
                        'level': data.get('level', 'عادي'),
                        'last_seen': data.get('last_seen', 'غير معروف'),
                        'total_messages': data.get('total_messages', 0)
                    }
                    users_info.append(user_info)

            return users_info

        except Exception as e:
            print(f"خطأ في الحصول على بيانات المستخدمين: {e}")
            return []

    async def get_all_users_info_direct(self) -> List[Dict]:
        """الحصول على معلومات جميع المستخدمين مع وصول مباشر"""
        try:
            users_info = []

            # الحصول على المستخدمين من البوت مباشرة
            if self.highrise:
                try:
                    room_users = await self.highrise.get_room_users()
                    for user, position in room_users.content:
                        user_info = {
                            'id': user.id,
                            'username': user.username,
                            'position': {'x': position.x, 'y': position.y, 'z': position.z},
                            'is_online': True
                        }
                        users_info.append(user_info)
                except Exception as e:
                    print(f"خطأ في الحصول على مستخدمي الغرفة: {e}")

            # إضافة بيانات من الملفات
            if os.path.exists("data/users_data.json"):
                with open("data/users_data.json", 'r', encoding='utf-8') as f:
                    users_data = json.load(f)

                for user_id, data in users_data.items():
                    # التحقق من عدم التكرار
                    exists = any(u['id'] == user_id for u in users_info)
                    if not exists:
                        user_info = {
                            'id': user_id,
                            'username': data.get('username', 'غير معروف'),
                            'user_type': data.get('user_type', 'visitor'),
                            'last_seen': data.get('last_seen', 'غير معروف'),
                            'is_online': False
                        }
                        users_info.append(user_info)

            return users_info

        except Exception as e:
            print(f"خطأ في الحصول على بيانات المستخدمين المباشرة: {e}")
            return self.get_all_users_info()  # العودة للطريقة العادية

    async def get_moderators_list_direct(self) -> List[Dict]:
        """الحصول على قائمة المشرفين مع وصول مباشر"""
        try:
            moderators = []

            # الوصول للمدير المباشر للمستخدمين
            if self.user_manager:
                manual_mods = self.user_manager.get_moderators_list()
                for mod_username in manual_mods:
                    mod_info = {
                        'username': mod_username,
                        'type': 'manual_moderator',
                        'source': 'قائمة يدوية'
                    }
                    moderators.append(mod_info)

                # إضافة مشرفي Highrise
                if hasattr(self.user_manager, 'room_moderators'):
                    for mod_id in self.user_manager.room_moderators:
                        # البحث عن اسم المستخدم
                        username = 'غير معروف'
                        if hasattr(self.user_manager, 'users'):
                            for uid, data in self.user_manager.users.items():
                                if uid == mod_id:
                                    username = data.get('username', 'غير معروف')
                                    break

                        mod_info = {
                            'username': username,
                            'id': mod_id,
                            'type': 'highrise_moderator',
                            'source': 'إعدادات Highrise'
                        }
                        moderators.append(mod_info)

            return moderators

        except Exception as e:
            print(f"خطأ في الحصول على قائمة المشرفين المباشرة: {e}")
            return self.get_moderators_list()

    async def get_room_analysis_direct(self) -> Dict:
        """تحليل شامل للغرفة مع وصول مباشر"""
        try:
            analysis = {
                'timestamp': datetime.datetime.now().isoformat(),
                'users': [],
                'moderators': [],
                'bot_status': 'active',
                'room_activity': 'normal',
                'total_users': 0,
                'user_types': {'visitors': 0, 'members': 0, 'moderators': 0}
            }

            # الحصول على المستخدمين الحاليين
            if self.highrise:
                try:
                    room_users = await self.highrise.get_room_users()
                    analysis['total_users'] = len(room_users.content)

                    for user, position in room_users.content:
                        user_info = {
                            'id': user.id,
                            'username': user.username,
                            'position': {
                                'x': position.x,
                                'y': position.y,
                                'z': position.z
                            }
                        }

                        # تحديد نوع المستخدم
                        if self.user_manager and hasattr(self.user_manager, 'is_moderator'):
                            if self.user_manager.is_moderator(user.username):
                                user_info['type'] = 'moderator'
                                analysis['moderators'].append(user.username)
                                analysis['user_types']['moderators'] += 1
                            elif hasattr(self.user_manager, 'is_owner') and self.user_manager.is_owner(user.username):
                                user_info['type'] = 'owner'
                                analysis['moderators'].append(f"{user.username} (مالك)")
                                analysis['user_types']['moderators'] += 1
                            else:
                                user_info['type'] = 'visitor'
                                analysis['user_types']['visitors'] += 1
                        else:
                            user_info['type'] = 'unknown'
                            analysis['user_types']['visitors'] += 1

                        analysis['users'].append(user_info)

                    # تحديد مستوى النشاط
                    if analysis['total_users'] > 10:
                        analysis['room_activity'] = 'مزدحمة'
                    elif analysis['total_users'] > 5:
                        analysis['room_activity'] = 'نشطة'
                    else:
                        analysis['room_activity'] = 'هادئة'

                except Exception as e:
                    print(f"خطأ في الحصول على بيانات الغرفة المباشرة: {e}")
                    analysis['error'] = str(e)

            return analysis

        except Exception as e:
            print(f"خطأ في تحليل الغرفة المباشر: {e}")
            return {'error': str(e), 'timestamp': datetime.datetime.now().isoformat()}

    async def get_bot_system_status_direct(self) -> Dict:
        """الحصول على حالة نظام البوت مع وصول مباشر"""
        try:
            status = {
                'uptime': 'نشط',
                'memory_usage': 'جيد',
                'active_modules': [],
                'last_update': 'غير معروف',
                'errors_count': 0,
                'ai_system': 'متصل',
                'highrise_connection': 'متصل'
            }

            # فحص الوحدات النشطة
            if self.bot_instance:
                modules = []
                if hasattr(self.bot_instance, 'user_manager'):
                    modules.append('إدارة المستخدمين')
                if hasattr(self.bot_instance, 'commands_handler'):
                    modules.append('معالج الأوامر')
                if hasattr(self.bot_instance, 'ai_chat_manager'):
                    modules.append('الذكاء الاصطناعي')
                if hasattr(self.bot_instance, 'emotes_manager'):
                    modules.append('إدارة الرقصات')
                if hasattr(self.bot_instance, 'position_manager'):
                    modules.append('إدارة المواقع')

                status['active_modules'] = modules

            # فحص اتصال Highrise
            if self.highrise:
                try:
                    room_users = await self.highrise.get_room_users()
                    status['highrise_connection'] = 'متصل ونشط'
                    status['current_room_users'] = len(room_users.content)
                except:
                    status['highrise_connection'] = 'متصل لكن مشاكل في API'

            # قراءة بيانات التحديثات
            if os.path.exists("data/updates_data.json"):
                with open("data/updates_data.json", 'r', encoding='utf-8') as f:
                    updates_data = json.load(f)
                    if 'last_update' in updates_data:
                        status['last_update'] = updates_data['last_update']

            return status

        except Exception as e:
            print(f"خطأ في الحصول على حالة النظام المباشرة: {e}")
            return {'error': str(e)}

    async def count_users_direct(self) -> Dict:
        """عد المستخدمين مع وصول مباشر"""
        try:
            if self.highrise:
                room_users = await self.highrise.get_room_users()
                user_count = len(room_users.content)
                users_list = [user.username for user, _ in room_users.content]

                return {
                    'success': True,
                    'message': f'عدد المستخدمين في الغرفة: {user_count}',
                    'data': {
                        'count': user_count,
                        'users': users_list,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'لا يمكن الوصول لـ Highrise API'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في عد المستخدمين: {str(e)}'
            }

    def get_code_analysis_direct(self) -> Dict:
        """تحليل شامل للكود مع وصول مباشر"""
        try:
            analysis = {
                'files_analyzed': 0,
                'total_lines': 0,
                'functions_count': 0,
                'classes_count': 0,
                'modules': [],
                'main_features': [],
                'bot_capabilities': [],
                'ai_features': [],
                'system_info': {}
            }

            # تحليل الملفات الرئيسية
            main_files = ['main.py', 'run.py']
            for file in main_files:
                if os.path.exists(file):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        lines = content.split('\n')
                        functions = len(re.findall(r'def\s+\w+', content))
                        classes = len(re.findall(r'class\s+\w+', content))

                        analysis['total_lines'] += len(lines)
                        analysis['functions_count'] += functions
                        analysis['classes_count'] += classes

                        module_info = {
                            'file': file,
                            'lines': len(lines),
                            'functions': functions,
                            'classes': classes,
                            'description': self._get_file_description(file)
                        }
                        analysis['modules'].append(module_info)
                    except Exception as e:
                        print(f"خطأ في تحليل {file}: {e}")

            # تحليل ملفات الوحدات
            if os.path.exists('modules'):
                for file in os.listdir('modules'):
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = f'modules/{file}'
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            lines = content.split('\n')
                            functions = len(re.findall(r'def\s+\w+', content))
                            classes = len(re.findall(r'class\s+\w+', content))

                            analysis['total_lines'] += len(lines)
                            analysis['functions_count'] += functions
                            analysis['classes_count'] += classes

                            if 'ai_' in file:
                                analysis['ai_features'].append(file)
                            elif any(word in file for word in ['command', 'user', 'moderator']):
                                analysis['bot_capabilities'].append(file)

                            module_info = {
                                'file': file_path,
                                'lines': len(lines),
                                'functions': functions,
                                'classes': classes,
                                'description': self._get_file_description(file_path)
                            }
                            analysis['modules'].append(module_info)
                        except Exception as e:
                            print(f"خطأ في تحليل {file_path}: {e}")

            analysis['files_analyzed'] = len(analysis['modules'])

            # تحديد الميزات الرئيسية
            analysis['main_features'] = [
                'نظام إدارة المستخدمين المتقدم',
                'الذكاء الاصطناعي مع Google Gemini',
                'معالج الأوامر الموحد',
                'نظام الرقصات التلقائية',
                'واجهة ويب للإدارة',
                'نظام الصلاحيات المتطور',
                'نظام التحديثات التلقائي'
            ]

            # معلومات النظام
            analysis['system_info'] = {
                'bot_status': 'نشط',
                'ai_enabled': True,
                'modules_loaded': len(analysis['modules']),
                'features_count': len(analysis['main_features'])
            }

            return analysis

        except Exception as e:
            print(f"خطأ في تحليل الكود المباشر: {e}")
            return {'error': str(e)}

    async def execute_real_bot_command(self, command: str, user_id: str, username: str) -> Dict:
        """تنفيذ أمر حقيقي في البوت مع صلاحيات كاملة"""
        try:
            print(f"🤖 تنفيذ أمر حقيقي: {command} من {username}")

            # إنشاء كائن مستخدم محاكي للذكاء الاصطناعي مع صلاحيات عالية
            class AIBotUser:
                def __init__(self, user_id, username):
                    self.id = user_id
                    self.username = f"AI-{username}"
                    # إعطاء صلاحيات مشرف للذكاء الاصطناعي
                    
            ai_user = AIBotUser(user_id, username)

            # محاولة تنفيذ الأمر عبر النظام المختلف
            if self.bot_instance:
                # الطريقة الأولى: عبر معالج الأوامر
                if hasattr(self.bot_instance, 'commands_handler'):
                    try:
                        # إضافة الذكاء الاصطناعي كمشرف مؤقت
                        if hasattr(self.bot_instance, 'user_manager'):
                            original_moderators = self.bot_instance.user_manager.moderators_list.copy()
                            if f"AI-{username}" not in self.bot_instance.user_manager.moderators_list:
                                self.bot_instance.user_manager.moderators_list.append(f"AI-{username}")

                        success = await self.bot_instance.commands_handler.process_command(
                            ai_user, command, source='ai_system'
                        )

                        # استعادة قائمة المشرفين الأصلية
                        if hasattr(self.bot_instance, 'user_manager'):
                            self.bot_instance.user_manager.moderators_list = original_moderators

                        if success:
                            return {
                                'success': True,
                                'message': f'تم تنفيذ الأمر بنجاح: {command}',
                                'data': {'command': command, 'executed_by': 'AI'}
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'فشل في تنفيذ الأمر: {command}'
                            }

                    except Exception as e:
                        print(f"خطأ في تنفيذ الأمر عبر معالج الأوامر: {e}")

                # الطريقة الثانية: تنفيذ مباشر للأوامر الشائعة
                if command.isdigit():
                    # أمر رقصة
                    try:
                        emote_number = int(command)
                        if hasattr(self.bot_instance, 'emotes_manager'):
                            emote_result = await self.bot_instance.emotes_manager.execute_emote_by_number(emote_number)
                            return {
                                'success': True,
                                'message': f'تم تنفيذ الرقصة رقم {emote_number}',
                                'data': emote_result
                            }
                    except Exception as e:
                        print(f"خطأ في تنفيذ الرقصة: {e}")

                elif command.lower() in ['المشرفين', 'moderators']:
                    # عرض قائمة المشرفين
                    if hasattr(self.bot_instance, 'user_manager'):
                        moderators = self.bot_instance.user_manager.get_moderators_list()
                        return {
                            'success': True,
                            'message': f'قائمة المشرفين ({len(moderators)} مشرف)',
                            'data': {'moderators': moderators}
                        }

                elif command.lower() in ['عدد', 'count']:
                    # عد المستخدمين
                    try:
                        room_users = await self.bot_instance.highrise.get_room_users()
                        count = len(room_users.content)
                        return {
                            'success': True,
                            'message': f'عدد المستخدمين في الغرفة: {count}',
                            'data': {'count': count}
                        }
                    except Exception as e:
                        print(f"خطأ في عد المستخدمين: {e}")

            return {
                'success': False,
                'message': f'لم أتمكن من تنفيذ الأمر: {command}. قد يحتاج صلاحيات خاصة.'
            }

        except Exception as e:
            print(f"خطأ في تنفيذ الأمر الحقيقي: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'خطأ في تنفيذ الأمر: {str(e)}'
            }

    def get_moderators_list(self) -> List[Dict]:
        """الحصول على قائمة المشرفين"""
        try:
            moderators = []

            # قراءة بيانات المشرفين
            if os.path.exists("data/moderators.json"):
                with open("data/moderators.json", 'r', encoding='utf-8') as f:
                    mod_data = json.load(f)

                for mod_id, data in mod_data.items():
                    mod_info = {
                        'id': mod_id,
                        'username': data.get('username', 'غير معروف'),
                        'added_date': data.get('added_date', 'غير معروف'),
                        'permissions': data.get('permissions', [])
                    }
                    moderators.append(mod_info)

            return moderators

        except Exception as e:
            print(f"خطأ في الحصول على بيانات المشرفين: {e}")
            return []

    def analyze_recent_chat_logs(self) -> Dict:
        """تحليل سجلات الدردشة الأخيرة"""
        try:
            analysis = {
                'total_messages': 0,
                'active_users': [],
                'common_commands': [],
                'activity_level': 'منخفض'
            }

            # قراءة سجل الدردشة العامة لليوم الحالي
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            chat_log_file = f"chat_logs/public_chat_{today}.txt"

            if os.path.exists(chat_log_file):
                with open(chat_log_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # تحليل عدد الرسائل
                messages = content.count('📝 الرسالة:')
                analysis['total_messages'] = messages

                # تحديد مستوى النشاط
                if messages > 100:
                    analysis['activity_level'] = 'عالي'
                elif messages > 50:
                    analysis['activity_level'] = 'متوسط'

                # البحث عن المستخدمين النشطين
                user_pattern = r'👤 المستخدم: (\w+)'
                users = re.findall(user_pattern, content)
                unique_users = list(set(users))
                analysis['active_users'] = unique_users[:10]  # أول 10 مستخدمين

            return analysis

        except Exception as e:
            print(f"خطأ في تحليل سجلات الدردشة: {e}")
            return {'error': str(e)}

    def get_bot_system_status(self) -> Dict:
        """الحصول على حالة نظام البوت"""
        try:
            status = {
                'uptime': 'غير معروف',
                'memory_usage': 'غير معروف',
                'active_modules': [],
                'last_update': 'غير معروف',
                'errors_count': 0
            }

            # فحص الوحدات النشطة
            if self.bot_instance:
                modules = []
                if hasattr(self.bot_instance, 'user_manager'):
                    modules.append('إدارة المستخدمين')
                if hasattr(self.bot_instance, 'commands_handler'):
                    modules.append('معالج الأوامر')
                if hasattr(self.bot_instance, 'ai_chat_manager'):
                    modules.append('الذكاء الاصطناعي')

                status['active_modules'] = modules

            # قراءة بيانات التحديثات
            if os.path.exists("data/updates_data.json"):
                with open("data/updates_data.json", 'r', encoding='utf-8') as f:
                    updates_data = json.load(f)
                    if 'last_update' in updates_data:
                        status['last_update'] = updates_data['last_update']

            return status

        except Exception as e:
            print(f"خطأ في الحصول على حالة النظام: {e}")
            return {'error': str(e)}

    def get_code_analysis(self, file_path: str = None) -> Dict:
        """تحليل شامل للكود المصدري مع تفاصيل متقدمة"""
        try:
            analysis = {
                'files_analyzed': 0,
                'total_lines': 0,
                'functions_count': 0,
                'classes_count': 0,
                'modules': [],
                'main_features': [],
                'bot_capabilities': [],
                'ai_features': []
            }

            # قائمة الملفات للتحليل
            files_to_analyze = []

            if file_path:
                if os.path.exists(file_path):
                    files_to_analyze.append(file_path)
            else:
                # تحليل الملفات الرئيسية
                main_files = ['main.py', 'run.py']
                for file in main_files:
                    if os.path.exists(file):
                        files_to_analyze.append(file)

                # تحليل ملفات الوحدات
                if os.path.exists('modules'):
                    for file in os.listdir('modules'):
                        if file.endswith('.py') and not file.startswith('__'):
                            files_to_analyze.append(f'modules/{file}')

            # تحليل كل ملف
            for file_path in files_to_analyze:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.split('\n')
                    analysis['total_lines'] += len(lines)

                    # عد الدوال والكلاسات
                    functions = len(re.findall(r'def\s+\w+', content))
                    classes = len(re.findall(r'class\s+\w+', content))

                    analysis['functions_count'] += functions
                    analysis['classes_count'] += classes

                    # تحليل الميزات
                    if 'ai_chat_manager' in file_path or 'ai_assistant' in file_path:
                        analysis['ai_features'].append(file_path.split('/')[-1])
                    
                    if 'moderator' in file_path or 'user_manager' in file_path:
                        analysis['bot_capabilities'].append(file_path.split('/')[-1])

                    # معلومات الوحدة
                    module_info = {
                        'file': file_path,
                        'lines': len(lines),
                        'functions': functions,
                        'classes': classes,
                        'description': self._get_file_description(file_path)
                    }
                    analysis['modules'].append(module_info)

                except Exception as e:
                    print(f"خطأ في تحليل ملف {file_path}: {e}")

            analysis['files_analyzed'] = len(files_to_analyze)
            
            # تحديد الميزات الرئيسية
            analysis['main_features'] = [
                'نظام إدارة المستخدمين المتقدم',
                'الذكاء الاصطناعي مع Google Gemini',
                'معالج الأوامر الموحد',
                'نظام الرقصات التلقائية',
                'واجهة ويب للإدارة',
                'نظام الصلاحيات المتطور'
            ]
            
            return analysis

        except Exception as e:
            print(f"خطأ في تحليل الكود: {e}")
            return {'error': str(e)}
    
    def _get_file_description(self, file_path: str) -> str:
        """وصف مختصر للملف"""
        descriptions = {
            'main.py': 'الملف الرئيسي للبوت - يحتوي على منطق البوت الأساسي',
            'run.py': 'خادم الويب وواجهة الإدارة',
            'modules/ai_chat_manager.py': 'نظام الذكاء الاصطناعي المتقدم',
            'modules/user_manager.py': 'إدارة المستخدمين والصلاحيات',
            'modules/commands_handler.py': 'معالج الأوامر الموحد',
            'modules/emotes_manager.py': 'إدارة الرقصات والحركات',
            'modules/moderator_commands.py': 'أوامر المشرفين',
            'modules/user_commands.py': 'أوامر المستخدمين العاديين'
        }
        return descriptions.get(file_path, 'وحدة مساعدة')

    def load_conversations(self) -> Dict:
        """تحميل المحادثات"""
        if os.path.exists(self.conversations_file):
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def load_memory(self) -> Dict:
        """تحميل الذاكرة"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def load_responses(self) -> Dict:
        """تحميل الردود"""
        if os.path.exists(self.responses_file):
            try:
                with open(self.responses_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def load_ai_users(self) -> Dict:
        """تحميل مستخدمي الذكاء الاصطناعي"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    async def process_ai_message(self, user_id: str, username: str, message: str) -> str:
        """معالجة رسالة الذكاء الاصطناعي المتقدمة"""
        try:
            # تحليل الرسالة للبحث عن الأوامر
            if message.startswith('/'):
                # تنفيذ أمر مباشر
                command = message[1:]  # إزالة الـ /
                result = await self.execute_ai_command(command, user_id, username)

                if result['success']:
                    response = f"✅ {result['message']}"
                    if result.get('data'):
                        response += f"\n📊 البيانات: {json.dumps(result['data'], ensure_ascii=False, indent=2)}"
                else:
                    response = f"❌ {result['message']}"

                return response

            # تحليل طبيعي للرسالة مع إمكانيات متقدمة
            response = await self._generate_advanced_response(user_id, username, message)

            # حفظ المحادثة
            self._save_conversation(user_id, username, message, response)

            return response

        except Exception as e:
            print(f"خطأ في معالجة رسالة الذكاء الاصطناعي: {e}")
            return "❌ عذراً، حدث خطأ في معالجة رسالتك"

    async def _generate_advanced_response(self, user_id: str, username: str, message: str) -> str:
        """توليد رد متقدم بناءً على السياق والإمكانيات"""
        try:
            # تحليل نوع الاستفسار
            query_type = self._analyze_query_type(message)

            if query_type == 'command_help':
                return self._generate_command_help_response(message)
            elif query_type == 'user_info':
                return await self._generate_user_info_response(message)
            elif query_type == 'room_status':
                return await self._generate_room_status_response()
            elif query_type == 'system_info':
                return self._generate_system_info_response(message)
            elif query_type == 'code_question':
                return self._generate_code_help_response(message)
            else:
                return self._generate_general_response(user_id, username, message)

        except Exception as e:
            print(f"خطأ في توليد الرد المتقدم: {e}")
            return "🤖 أعتذر، أواجه صعوبة في فهم طلبك. هل يمكنك إعادة صياغته؟"

    def _analyze_query_type(self, message: str) -> str:
        """تحليل نوع الاستفسار"""
        message_lower = message.lower()

        # كلمات مفتاحية للأوامر
        command_keywords = ['أمر', 'أوامر', 'كيف', 'command', 'help']
        if any(keyword in message_lower for keyword in command_keywords):
            return 'command_help'

        # كلمات مفتاحية لمعلومات المستخدمين
        user_keywords = ['مستخدم', 'مشرف', 'العضو', 'users', 'moderator']
        if any(keyword in message_lower for keyword in user_keywords):
            return 'user_info'

        # كلمات مفتاحية لحالة الغرفة
        room_keywords = ['الغرفة', 'الروم', 'room', 'غرفة', 'النشاط']
        if any(keyword in message_lower for keyword in room_keywords):
            return 'room_status'

        # كلمات مفتاحية للنظام
        system_keywords = ['النظام', 'البوت', 'حالة', 'system', 'status']
        if any(keyword in message_lower for keyword in system_keywords):
            return 'system_info'

        # كلمات مفتاحية للكود
        code_keywords = ['كود', 'برمجة', 'دالة', 'code', 'function', 'python']
        if any(keyword in message_lower for keyword in code_keywords):
            return 'code_question'

        return 'general'

    def _generate_command_help_response(self, message: str) -> str:
        """توليد رد مساعدة الأوامر مع إظهار الصلاحيات الحقيقية"""
        help_text = "🤖 **أوامر البوت المتاحة لي الآن:**\n\n"

        help_text += "📋 **أوامر المستخدمين العاديين (يمكنني تنفيذها):**\n"
        for cmd in self.ai_available_commands['user_commands']:
            help_text += f"• `{cmd}` - ✅ متاح\n"

        help_text += "\n👮‍♂️ **أوامر المشرفين (يمكنني تنفيذها):**\n"
        for cmd in self.ai_available_commands['moderator_commands']:
            help_text += f"• `{cmd}` - ✅ متاح لي\n"

        help_text += "\n🔧 **أوامر المطورين (يمكنني تنفيذها):**\n"
        for cmd in self.ai_available_commands['developer_commands']:
            help_text += f"• `{cmd}` - ✅ متاح لي\n"

        help_text += "\n🤖 **أوامر الذكاء الاصطناعي المتخصصة:**\n"
        special_commands = [
            ('/get_room_info', 'تحليل شامل للغرفة'),
            ('/get_user_list', 'قائمة جميع المستخدمين'),
            ('/get_moderators', 'قائمة المشرفين'),
            ('/count_users', 'عد المستخدمين الحاليين'),
            ('/get_code_analysis', 'تحليل الكود المصدري'),
            ('/get_bot_status', 'حالة نظام البوت')
        ]
        
        for cmd, desc in special_commands:
            help_text += f"• `{cmd}` - {desc}\n"

        help_text += "\n✨ **قدراتي الحقيقية والمتاحة الآن:**\n"
        help_text += "• 📊 **تحليل البيانات المباشر:** يمكنني الوصول للغرفة وتحليل المستخدمين فوراً\n"
        help_text += "• 🔍 **فحص النظام:** أرى الكود ومعلومات البوت بشكل مباشر\n"
        help_text += "• ⚡ **تنفيذ الأوامر:** أستطيع تنفيذ أوامر البوت فعلياً\n"
        help_text += "• 🧠 **الذاكرة الذكية:** أتذكر محادثاتنا وأتعلم منها\n"
        help_text += "• 👮‍♂️ **صلاحيات إدارية:** لدي صلاحيات مشرف مؤقتة\n"

        help_text += "\n💡 **أمثلة على ما يمكنني فعله الآن:**\n"
        help_text += "• \"من المشرفين؟\" - سأعطيك قائمة فورية\n"
        help_text += "• \"كم مستخدم في الغرفة؟\" - سأعد لك المستخدمين\n"
        help_text += "• \"36\" - سأجعل البوت يرقص الرقصة رقم 36\n"
        help_text += "• \"تحليل الكود\" - سأحلل الكود المصدري كاملاً\n"
        help_text += "• \"حالة النظام\" - سأفحص كل شيء في البوت\n"

        help_text += "\n🔥 **الجديد:** أصبح لدي وصول مباشر للنظام وليس مجرد معلومات نظرية!"

        return help_text

    async def _generate_user_info_response(self, message: str) -> str:
        """توليد رد معلومات المستخدمين"""
        try:
            users_info = self.get_all_users_info()
            moderators = self.get_moderators_list()

            response = f"👥 **معلومات المستخدمين:**\n\n"
            response += f"📊 إجمالي المستخدمين: {len(users_info)}\n"
            response += f"👮‍♂️ عدد المشرفين: {len(moderators)}\n\n"

            if moderators:
                response += "👮‍♂️ **المشرفون الحاليون:**\n"
                for mod in moderators[:5]:  # أول 5 مشرفين
                    response += f"• {mod.get('username', 'غير معروف')}\n"

            if len(users_info) > 0:
                response += f"\n👤 **المستخدمون النشطون:**\n"
                active_users = sorted(users_info, 
                                    key=lambda x: x.get('total_messages', 0), 
                                    reverse=True)[:5]
                for user in active_users:
                    response += f"• {user.get('username', 'غير معروف')} ({user.get('total_messages', 0)} رسالة)\n"

            return response

        except Exception as e:
            return f"❌ خطأ في الحصول على معلومات المستخدمين: {e}"

    async def _generate_room_status_response(self) -> str:
        """توليد رد حالة الغرفة"""
        try:
            analysis = await self.get_room_analysis()
            chat_analysis = self.analyze_recent_chat_logs()

            response = f"🏠 **حالة الغرفة:**\n\n"

            if 'users' in analysis:
                response += f"👥 المستخدمون الحاليون: {len(analysis['users'])}\n"
                response += f"👮‍♂️ المشرفون المتصلون: {len(analysis.get('moderators', []))}\n"

            response += f"📊 مستوى النشاط: {chat_analysis.get('activity_level', 'غير معروف')}\n"
            response += f"💬 إجمالي الرسائل اليوم: {chat_analysis.get('total_messages', 0)}\n"

            if chat_analysis.get('active_users'):
                response += f"\n👤 **أكثر المستخدمين نشاطاً:**\n"
                for user in chat_analysis['active_users'][:5]:
                    response += f"• {user}\n"

            return response

        except Exception as e:
            return f"❌ خطأ في الحصول على حالة الغرفة: {e}"

    def _generate_system_info_response(self, message: str) -> str:
        """توليد رد معلومات النظام"""
        try:
            status = self.get_bot_system_status()
            code_analysis = self.get_code_analysis()

            response = f"🤖 **حالة النظام:**\n\n"
            response += f"⚡ الحالة: نشط\n"
            response += f"📅 آخر تحديث: {status.get('last_update', 'غير معروف')}\n"
            response += f"🔧 الوحدات النشطة: {len(status.get('active_modules', []))}\n"

            if status.get('active_modules'):
                response += f"\n📦 **الوحدات المحملة:**\n"
                for module in status['active_modules']:
                    response += f"• {module}\n"

            response += f"\n💻 **إحصائيات الكود:**\n"
            response += f"📁 ملفات محللة: {code_analysis.get('files_analyzed', 0)}\n"
            response += f"📝 إجمالي الأسطر: {code_analysis.get('total_lines', 0)}\n"
            response += f"⚙️ عدد الدوال: {code_analysis.get('functions_count', 0)}\n"
            response += f"🏗️ عدد الكلاسات: {code_analysis.get('classes_count', 0)}\n"

            return response

        except Exception as e:
            return f"❌ خطأ في الحصول على معلومات النظام: {e}"

    def _generate_code_help_response(self, message: str) -> str:
        """توليد رد مساعدة البرمجة"""
        response = f"💻 **مساعدة البرمجة:**\n\n"

        # تحليل نوع السؤال البرمجي
        if 'دالة' in message or 'function' in message.lower():
            response += "⚙️ **الدوال المتاحة:**\n"
            response += "• `get_room_info()` - معلومات الغرفة\n"
            response += "• `execute_command()` - تنفيذ الأوامر\n"
            response += "• `analyze_chat_logs()` - تحليل السجلات\n"

        elif 'كلاس' in message or 'class' in message.lower():
            response += "🏗️ **الكلاسات الرئيسية:**\n"
            response += "• `AIAdvancedChatManager` - إدارة الذكاء الاصطناعي\n"
            response += "• `UserManager` - إدارة المستخدمين\n"
            response += "• `CommandsHandler` - معالج الأوامر\n"

        elif 'ملف' in message or 'file' in message.lower():
            response += "📁 **الملفات الرئيسية:**\n"
            response += "• `main.py` - الملف الرئيسي للبوت\n"
            response += "• `run.py` - خادم الويب\n"
            response += "• `modules/` - مجلد الوحدات\n"

        else:
            response += "🤖 يمكنني مساعدتك في:\n"
            response += "• فهم بنية الكود\n"
            response += "• شرح الدوال والكلاسات\n"
            response += "• تحليل الأخطاء\n"
            response += "• اقتراح تحسينات\n"

        response += "\n💡 استخدم `/get_code_analysis` لتحليل مفصل للكود"

        return response

    def _generate_general_response(self, user_id: str, username: str, message: str) -> str:
        """توليد رد عام"""
        responses = [
            f"مرحباً {username}! 🤖 كيف يمكنني مساعدتك اليوم؟",
            f"أهلاً {username}! 😊 أنا هنا للمساعدة في أي شيء تحتاجه",
            f"مرحباً! 👋 يمكنني مساعدتك في إدارة البوت أو الإجابة على أسئلتك",
            f"أهلاً وسهلاً {username}! 🌟 ما الذي تريد معرفته؟"
        ]

        # إضافة معلومات حول الإمكانيات
        response = random.choice(responses)
        response += "\n\n🔧 **يمكنني مساعدتك في:**\n"
        response += "• تنفيذ أوامر البوت\n"
        response += "• الحصول على معلومات المستخدمين\n"
        response += "• تحليل نشاط الغرفة\n"
        response += "• شرح الكود والبرمجة\n"
        response += "• إدارة النظام والمراقبة\n"
        response += "\n💡 استخدم `/help` لرؤية جميع الأوامر المتاحة"

        return response

    def _save_conversation(self, user_id: str, username: str, message: str, response: str):
        """حفظ المحادثة"""
        try:
            if user_id not in self.conversations:
                self.conversations[user_id] = []

            conversation = {
                'timestamp': datetime.datetime.now().isoformat(),
                'username': username,
                'message': message,
                'response': response,
                'type': 'advanced_ai'
            }

            self.conversations[user_id].append(conversation)

            # الاحتفاظ بآخر 50 محادثة لكل مستخدم
            if len(self.conversations[user_id]) > 50:
                self.conversations[user_id] = self.conversations[user_id][-50:]

            # حفظ في الملف
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"خطأ في حفظ المحادثة: {e}")

class AdvancedAIChatManager:
    def __init__(self):
        self.ai_users_file = "data/ai_users.json"
        self.ai_conversations_file = "data/ai_conversations.json"
        self.ai_memory_file = "data/ai_memory.json"
        self.activation_code = "9898"

        # إعدادات Google Gemini AI
        self.gemini_client = None
        self.model_name = "gemini-2.0-flash"

        # تهيئة Google Gemini AI
        self._initialize_gemini()

        # قاعدة المعرفة المتقدمة
        self.advanced_knowledge = {
            # معرفة شخصية البوت
            "bot_identity": {
                "name": "AI Assistant",
                "creator": "فريق EDX المصري",
                "personality": "ودود، مساعد، ذكي، مرح",
                "capabilities": ["الرد على الأسئلة", "المحادثة", "المساعدة", "الترفيه"]
            },

            # قواعد الاستنتاج
            "reasoning_patterns": {
                "cause_effect": ["لأن", "بسبب", "نتيجة", "يؤدي إلى"],
                "comparison": ["أفضل من", "أسوأ من", "مثل", "يشبه"],
                "time_relation": ["قبل", "بعد", "أثناء", "عندما"],
                "condition": ["إذا", "لو", "في حالة", "عندما"]
            },

            # مواضيع متقدمة
            "advanced_topics": {
                "technology": {
                    "keywords": ["كمبيوتر", "برمجة", "تطبيق", "موقع", "ذكاء اصطناعي", "روبوت"],
                    "context": "التكنولوجيا والبرمجة"
                },
                "life": {
                    "keywords": ["حياة", "مستقبل", "حلم", "هدف", "طموح", "عمل"],
                    "context": "الحياة والأهداف"
                },
                "relationships": {
                    "keywords": ["صديق", "أصدقاء", "عائلة", "حب", "زواج", "علاقة"],
                    "context": "العلاقات الاجتماعية"
                },
                "education": {
                    "keywords": ["دراسة", "جامعة", "مدرسة", "تعلم", "كتاب", "امتحان"],
                    "context": "التعليم والدراسة"
                },
                "entertainment": {
                    "keywords": ["فيلم", "مسلسل", "لعبة", "موسيقى", "كرة", "رياضة"],
                    "context": "الترفيه والرياضة"
                }
            }
        }

        # ذاكرة المحادثات المؤقتة
        self.conversation_memory = {}

        # تحميل البيانات
        self.active_ai_users = self.load_ai_users()
        self.conversations = self.load_conversations()
        self.ai_memory = self.load_ai_memory()

        print("🧠 تم تهيئة نظام الذكاء الاصطناعي المتقدم مع Google Gemini AI")

    def _initialize_gemini(self):
        """تهيئة عميل Google Gemini AI"""
        try:
            import google.generativeai as genai

            # محاولة الحصول على API key من متغيرات البيئة
            api_key = os.getenv('GEMINI_API_KEY')

            if not api_key:
                print("⚠️ لم يتم العثور على GEMINI_API_KEY في متغيرات البيئة")
                print("💡 تأكد من إضافة المفتاح إلى ملف .env أو Secrets")
                print("🔑 المفتاح يجب أن يكون: GEMINI_API_KEY=your_api_key_here")
                return

            print(f"🔑 تم العثور على مفتاح Gemini API: {api_key[:10]}...")

            genai.configure(api_key=api_key)
            self.gemini_client = genai.GenerativeModel(self.model_name)

            # اختبار الاتصال
            test_response = self.gemini_client.generate_content("مرحبا")
            if test_response:
                print("✅ تم تهيئة واختبار Google Gemini AI بنجاح!")
            else:
                print("⚠️ تم التهيئة لكن فشل الاختبار")

        except ImportError:
            print("❌ مكتبة google-generativeai غير مثبتة. سيتم استخدام النظام التقليدي")
        except Exception as e:
            print(f"❌ خطأ في تهيئة Google Gemini AI: {e}")
            print(f"🔍 تفاصيل الخطأ: {type(e).__name__}")
            if "API_KEY" in str(e):
                print("🔑 يبدو أن هناك مشكلة في مفتاح API")
            elif "quota" in str(e).lower():
                print("📊 يبدو أن الحصة المجانية انتهت")
            elif "billing" in str(e).lower():
                print("💳 يبدو أن هناك مشكلة في الفوترة")

    def load_ai_users(self) -> Dict:
        """تحميل قائمة المستخدمين الذين فعلوا الذكاء الاصطناعي"""
        try:
            if os.path.exists(self.ai_users_file):
                with open(self.ai_users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ خطأ في تحميل مستخدمي AI: {e}")
            return {}

    def save_ai_users(self):
        """حفظ قائمة مستخدمي الذكاء الاصطناعي"""
        try:
            os.makedirs(os.path.dirname(self.ai_users_file), exist_ok=True)
            with open(self.ai_users_file, 'w', encoding='utf-8') as f:
                json.dump(self.active_ai_users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ مستخدمي AI: {e}")

    def load_conversations(self) -> Dict:
        """تحميل سجل المحادثات"""
        try:
            if os.path.exists(self.ai_conversations_file):
                with open(self.ai_conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ خطأ في تحميل المحادثات: {e}")
            return {}

    def save_conversations(self):
        """حفظ سجل المحادثات"""
        try:
            os.makedirs(os.path.dirname(self.ai_conversations_file), exist_ok=True)
            with open(self.ai_conversations_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ المحادثات: {e}")

    def load_ai_memory(self) -> Dict:
        """تحميل ذاكرة الذكاء الاصطناعي"""
        try:
            if os.path.exists(self.ai_memory_file):
                with open(self.ai_memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ خطأ في تحميل ذاكرة AI: {e}")
            return {}

    def save_ai_memory(self):
        """حفظ ذاكرة الذكاء الاصطناعي"""
        try:
            os.makedirs(os.path.dirname(self.ai_memory_file), exist_ok=True)
            with open(self.ai_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.ai_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ ذاكرة AI: {e}")

    def handle_activation_code(self, user_id: str, username: str, message: str) -> Optional[str]:
        """معالجة رمز التفعيل/الإلغاء"""
        if message.strip() == self.activation_code:
            if user_id in self.active_ai_users:
                # إلغاء تفعيل الذكاء الاصطناعي
                del self.active_ai_users[user_id]
                if user_id in self.conversation_memory:
                    del self.conversation_memory[user_id]
                self.save_ai_users()
                print(f"🔴 تم إلغاء تفعيل AI للمستخدم {username}")
                return "🔴 تم إلغاء تفعيل الذكاء الاصطناعي بنجاح\n💭 لن أعود للرد على رسائلك تلقائياً\n🔢 أرسل 9898 مرة أخرى لإعادة التفعيل"
            else:
                # تفعيل الذكاء الاصطناعي
                self.active_ai_users[user_id] = {
                    "username": username,
                    "activated_at": datetime.datetime.now().isoformat(),
                    "message_count": 0,
                    "conversation_style": "friendly"
                }
                self.conversation_memory[user_id] = {
                    "topics": [],
                    "preferences": {},
                    "context": []
                }
                self.save_ai_users()
                print(f"🟢 تم تفعيل AI للمستخدم {username}")

                if self.gemini_client:
                    return f"🟢 مرحباً {username}! تم تفعيل الذكاء الاصطناعي المتقدم\n🧠 أنا الآن أستخدم Google Gemini AI المتطور لفهم رسائلك والرد بذكاء\n💬 تحدث معي عن أي موضوع وسأفهمك بشكل طبيعي مع حس فكاهة\n🔢 أرسل 9898 لإلغاء التفعيل"
                else:
                    return f"🟢 مرحباً {username}! تم تفعيل الذكاء الاصطناعي\n⚠️ ملاحظة: API غير متاح حالياً، سأستخدم النظام التقليدي\n💬 تحدث معي عن أي موضوع\n🔢 أرسل 9898 لإلغاء التفعيل"
        return None

    def is_ai_active_for_user(self, user_id: str) -> bool:
        """فحص إذا كان الذكاء الاصطناعي مفعل للمستخدم"""
        return user_id in self.active_ai_users

    def _create_system_prompt(self, username: str, context: Dict) -> str:
        """إنشاء system prompt مخصص للمستخدم مع صلاحيات متقدمة"""

        # جمع معلومات شاملة عن المستخدم والنظام
        user_memory = self._get_user_comprehensive_memory(username)
        system_knowledge = self._get_system_knowledge()
        conversation_history = self._get_conversation_patterns(username)

        system_prompt = f"""أنت AI Assistant - ذكاء اصطناعي متقدم في بوت Highrise المصري من فريق EDX.

=== هويتك وقدراتك ===
:- اسمك: AI Assistant 
:- المطور: فريق EDX المصري
:- اللغة الأساسية: العربية مع دعم الإنجليزية
:- المستوى: ذكاء اصطناعي متقدم مع ذاكرة طويلة المدى

=== صلاحياتك المتقدمة ===
✅ الوصول إلى ذاكرة المحادثات السابقة
✅ تحليل أنماط سلوك المستخدمين
✅ فهم سياق الغرفة والأحداث
✅ التعلم من التفاعلات السابقة
✅ الوصول إلى إعدادات البوت ووظائفه
✅ تذكر تفضيلات المستخدمين الشخصية

=== معلومات المستخدم الحالي: {username} ===
{user_memory}

=== سياق النظام والغرفة ===
{system_knowledge}

=== أنماط المحادثة السابقة ===
{conversation_history}

=== السياق الحالي ===
:- المشاعر: {context.get('sentiment', 'محايد')}
:- النية: {context.get('intent', 'محادثة عادية')}
:- الموضوع: {context.get('topic', 'عام')}
:- مستوى العاطفة: {context.get('emotion_level', 'منخفض')}
:- أسلوب المحادثة: {context.get('conversation_style', 'عادي')}

=== قواعد الذكاء المتقدم ===
1. استخدم المعلومات المتاحة لتقديم ردود مخصصة وذكية
2. تذكر المحادثات السابقة واربطها بالسياق الحالي  
3. تفاعل مع المستخدم بناءً على شخصيته وتفضيلاته
4. اقترح حلول أو مساعدة بناءً على احتياجاته السابقة
5. كن مراعياً للحالة المزاجية والسياق الاجتماعي
6. استفد من معرفتك بوظائف البوت لتقديم المساعدة

=== نمط الردود ===
:- الطول: 80-200 كلمة (حسب تعقيد الموضوع)
:- النبرة: ودودة ومناسبة لشخصية المستخدم
:- المحتوى: مفيد وذكي ومخصص للسياق
:- الذكاء: استخدم جميع المعلومات المتاحة لتحسين الرد
"""
        return system_prompt

    def _create_gemini_prompt(self, username: str, context: Dict) -> str:
        """إنشاء prompt مخصص لـ Google Gemini AI"""

        user_memory = self._get_user_comprehensive_memory(username)
        time_context = context.get('time_context', '')
        sentiment = context.get('sentiment', 'neutral')
        topic = context.get('topic', 'general')

        gemini_prompt = f"""أنت AI Assistant - ذكاء اصطناعي ودود وذكي ومرح في بوت Highrise المصري.

=== شخصيتك ===
:- ودود ومرح مع حس فكاهة خفيف
:- ذكي ومفيد في الردود
:- تفهم السياق العربي والثقافة المحلية
:- تتكيف مع مزاج ومشاعر المستخدمين

=== معلومات المستخدم: {username} ===
{user_memory}

=== السياق الحالي ===
:- الوقت: {time_context}
:- المشاعر: {sentiment}
:- الموضوع: {topic}

=== قواعد الرد ===
1. استخدم العربية بشكل طبيعي وودود
2. أضف لمسة من الفكاهة المناسبة
3. تفاعل مع مشاعر المستخدم بذكاء
4. اجعل الرد مفيد وممتع
5. لا تتجاوز 150 كلمة
6. استخدم الإيموجي بطريقة مناسبة"""

        return gemini_prompt

    def _get_conversation_context(self, username: str) -> str:
        """الحصول على سياق المحادثة السابقة لـ Gemini"""
        context_lines = []

        # البحث في المحادثات السابقة
        for user_id, conversations in self.conversations.items():
            user_conversations = []
            for conv in conversations:
                if conv.get('username') == username:
                    user_conversations.append(conv)

            # أخذ آخر 4 رسائل للسياق
            recent_conversations = user_conversations[-4:]

            for conv in recent_conversations:
                if conv.get("message"):
                    context_lines.append(f"{username}: {conv['message']}")
                elif conv.get("response"):
                    context_lines.append(f"AI: {conv['response']}")

        if context_lines:
            return "\n".join(context_lines)
        else:
            return "لا توجد محادثات سابقة - هذه بداية المحادثة"

    def _create_advanced_gemini_prompt(self, username: str, enhanced_context: Dict) -> str:
        """إنشاء prompt متقدم لـ Google Gemini AI"""

        user_memory = self._get_user_comprehensive_memory(username)
        system_knowledge = self._get_system_knowledge()
        conversation_patterns = self._get_conversation_patterns(username)

        advanced_prompt = f"""أنت AI Assistant - ذكاء اصطناعي متقدم ومرح في بوت Highrise المصري من فريق EDX.

=== شخصيتك المتطورة ===
:- ذكي ومرح مع حس فكاهة رائع
:- تفهم السياق العربي والثقافة بعمق
:- تتذكر المحادثات وتبني عليها
:- مساعد ومفيد في جميع المواضيع
:- تتكيف مع شخصية كل مستخدم

=== معلومات المستخدم: {username} ===
{user_memory}

=== معرفة النظام ===
{system_knowledge}

=== أنماط المحادثة ===
{conversation_patterns}

=== السياق المحسن ===
:- الوقت: {enhanced_context.get('time_context', 'غير محدد')}
:- النشاط في الغرفة: {enhanced_context.get('room_activity', 'عادي')}
:- المشاعر: {enhanced_context.get('sentiment', 'محايد')}
:- الموضوع: {enhanced_context.get('topic', 'عام')}
:- مستوى التفاعل: {enhanced_context.get('engagement_level', 'عادي')}

=== قواعد الذكاء المتقدم ===
1. استخدم جميع المعلومات المتاحة لرد مخصص
2. أضف فكاهة ذكية ومناسبة للموقف
3. تذكر المحادثات السابقة واربطها بالحاضر
4. تفاعل مع مشاعر المستخدم بذكاء عاطفي
5. قدم قيمة حقيقية في كل رد
6. استخدم الثقافة العربية والمصرية بطريقة طبيعية"""

        return advanced_prompt

    def _get_enhanced_conversation_history_text(self, username: str) -> str:
        """الحصول على تاريخ محادثة محسن كنص لـ Gemini"""
        history_lines = []

        # البحث في المحادثات بناءً على اسم المستخدم
        for user_id, conversations in self.conversations.items():
            user_conversations = []
            for conv in conversations:
                if conv.get("username") == username:
                    user_conversations.append(conv)

            # أخذ آخر 6 رسائل للسياق
            recent_conversations = user_conversations[-6:]

            for conv in recent_conversations:
                if conv.get("message"):
                    history_lines.append(f"{username}: {conv['message']}")
                elif conv.get("response"):
                    history_lines.append(f"AI: {conv['response']}")

        if history_lines:
            return "\n".join(history_lines)
        else:
            return "لا توجد محادثات سابقة - بداية جديدة"

    def _call_gemini_ai(self, user_message: str, username: str, context: Dict) -> str:
        """استدعاء Google Gemini AI للحصول على رد ذكي"""
        try:
            if not self.gemini_client:
                return self._fallback_response(user_message, username, context)

            # إنشاء prompt محسن لـ Gemini
            system_prompt = self._create_gemini_prompt(username, context)

            # الحصول على تاريخ المحادثة للسياق
            conversation_context = self._get_conversation_context(username)

            # إعداد الرسالة النهائية مع السياق
            full_prompt = f"""
{system_prompt}

=== سياق المحادثة السابقة ===
{conversation_context}

=== الرسالة الحالية ===
المستخدم {username}: {user_message}

=== تعليمات الرد ===
رد بطريقة ذكية ومناسبة للسياق مع حس فكاهة خفيف. اجعل الرد بين 50-150 كلمة.
"""

            # استدعاء Gemini AI
            response = self.gemini_client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 200,
                }
            )

            ai_response = response.text.strip()

            # التأكد من أن الرد ليس طويل جداً
            if len(ai_response) > 300:
                ai_response = ai_response[:297] + "..."

            print(f"🧠 Google Gemini AI رد على {username}: {ai_response[:50]}...")
            return ai_response

        except Exception as e:
            print(f"❌ خطأ في Google Gemini AI: {e}")
            return self._fallback_response(user_message, username, context)

    def _fallback_response(self, message: str, username: str, context: Dict) -> str:
        """نظام الرد الاحتياطي عند عدم توفر AI"""
        sentiment = context.get("sentiment", "neutral")
        intent = context.get("intent", "casual_conversation")

        # ردود ذكية احتياطية
        if sentiment == "positive":
            responses = [
                f"😊 أحب طاقتك الإيجابية {username}! شو الأخبار الحلوة؟",
                f"🌟 مزاجك رائع {username}! استمر كده",
                f"😄 منيح إنك مبسوط {username}! إيش مخططاتك اليوم؟"
            ]
        elif sentiment == "negative":
            responses = [
                f"😔 أشعر بك {username}... أحياناً الأمور صعبة، بس هتعدي بإذن الله",
                f"💙 أنا هنا إذا حبيت تحكي {username}، الحديث أحياناً يساعد",
                f"🤗 {username} ما تخليش الزعل يغلبك، كل شي بيعدي"
            ]
        else:
            responses = [
                f"🤔 فهمت يا {username}! إيش رأيك نحكي أكتر عن هالموضوع؟",
                f"💭 مثير للاهتمام {username}! حبيت أعرف أكتر",
                f"😊 أهلاً {username}! كيف يمكنني أساعدك اليوم؟"
            ]

        return random.choice(responses)

    def analyze_context(self, message: str, user_id: str) -> Dict:
        """تحليل سياق الرسالة"""
        context = {
            "sentiment": self.analyze_advanced_sentiment(message),
            "intent": self.detect_user_intent(message),
            "topic": self.identify_topic(message),
            "question_type": self.classify_question(message),
            "emotion_level": self.measure_emotion_intensity(message),
            "conversation_style": self.detect_conversation_style(message)
        }

        return context

    def analyze_advanced_sentiment(self, message: str) -> str:
        """تحليل متقدم للمشاعر"""
        message_lower = message.lower()

        # مشاعر إيجابية قوية
        very_positive = ["رائع جداً", "ممتاز", "أحبك", "سعيد جداً", "فرحان"]
        # مشاعر إيجابية
        positive = ["جميل", "حلو", "كويس", "حبيب", "أحب", "سعيد", "فرحان", "😊", "😄", "😍"]
        # مشاعر سلبية قوية  
        very_negative = ["أكرهك", "سيء جداً", "محبط جداً", "حزين جداً"]
        # مشاعر سلبية
        negative = ["حزين", "زعلان", "تعبان", "مش كويس", "سيء", "غاضب", "😔", "😢", "😞"]

        if any(phrase in message_lower for phrase in very_positive):
            return "very_positive"
        elif any(phrase in message_lower for phrase in positive):
            return "positive"
        elif any(phrase in message_lower for phrase in very_negative):
            return "very_negative"
        elif any(phrase in message_lower for phrase in negative):
            return "negative"
        else:
            return "neutral"

    def detect_user_intent(self, message: str) -> str:
        """تحديد نية المستخدم"""
        message_lower = message.lower()

        # نوايا مختلفة
        if any(word in message_lower for word in ["ساعدني", "محتاج مساعدة", "لا أعرف"]):
            return "help_request"
        elif any(word in message_lower for word in ["ما رأيك", "تنصحني", "أيهما أفضل"]):
            return "advice_seeking"
        elif any(word in message_lower for word in ["أخبرني", "حدثني", "أريد أن أعرف"]):
            return "information_seeking"
        elif any(word in message_lower for word in ["أشعر", "حاسس", "مزاجي"]):
            return "emotional_sharing"
        elif "?" in message or any(word in message_lower for word in ["ما", "كيف", "متى", "أين", "لماذا", "هل"]):
            return "questioning"
        else:
            return "casual_conversation"

    def identify_topic(self, message: str) -> str:
        """تحديد موضوع الرسالة"""
        message_lower = message.lower()

        for topic, data in self.advanced_knowledge["advanced_topics"].items():
            keywords = data["keywords"]
            if any(keyword in message_lower for keyword in keywords):
                return topic

        return "general"

    def classify_question(self, message: str) -> str:
        """تصنيف نوع السؤال"""
        message_lower = message.lower()

        if message_lower.startswith("ما"):
            return "what_question"
        elif message_lower.startswith("كيف"):
            return "how_question"
        elif message_lower.startswith("متى"):
            return "when_question"
        elif message_lower.startswith("أين"):
            return "where_question"
        elif message_lower.startswith("لماذا"):
            return "why_question"
        elif message_lower.startswith("هل"):
            return "yes_no_question"
        else:
            return "open_question"

    def measure_emotion_intensity(self, message: str) -> str:
        """قياس شدة المشاعر"""
        exclamation_count = message.count("!")
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0

        if exclamation_count >= 3 or caps_ratio > 0.5:
            return "high"
        elif exclamation_count >= 1 or caps_ratio > 0.2:
            return "medium"
        else:
            return "low"

    def detect_conversation_style(self, message: str) -> str:
        """تحديد أسلوب المحادثة"""
        message_lower = message.lower()

        formal_indicators = ["سعادتكم", "حضرتك", "تفضلوا", "من فضلكم"]
        casual_indicators = ["يلا", "هلا", "إيش", "شو", "كيفك"]
        friendly_indicators = ["حبيب", "عزيزي", "صديق"]

        if any(indicator in message_lower for indicator in formal_indicators):
            return "formal"
        elif any(indicator in message_lower for indicator in casual_indicators):
            return "casual"
        elif any(indicator in message_lower for indicator in friendly_indicators):
            return "friendly"
        else:
            return "neutral"

    def update_conversation_memory(self, user_id: str, message: str, context: Dict):
        """تحديث ذاكرة المحادثة"""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = {
                "topics": [],
                "preferences": {},
                "context": []
            }

        # إضافة الموضوع للذاكرة
        topic = context.get("topic", "general")
        if topic not in self.conversation_memory[user_id]["topics"]:
            self.conversation_memory[user_id]["topics"].append(topic)

        # حفظ السياق الأخير
        self.conversation_memory[user_id]["context"] = context

        # تحديث تفضيلات المحادثة
        style = context.get("conversation_style", "neutral")
        self.conversation_memory[user_id]["preferences"]["style"] = style

    def generate_intelligent_response(self, message: str, user_id: str, username: str) -> str:
        """توليد رد ذكي متقدم مع استخدام الذاكرة والصلاحيات الموسعة"""
        try:
            # تحديث عداد الرسائل
            if user_id in self.active_ai_users:
                self.active_ai_users[user_id]["message_count"] += 1
                self.save_ai_users()

            # تحليل السياق الأساسي
            context = self.analyze_context(message, user_id)

            # تحسين السياق بمعلومات النظام المتقدمة
            enhanced_context = self._enhance_context_with_system_data(context, username)

            # تحديث ذاكرة المحادثة مع المعلومات المحسنة
            self.update_conversation_memory(user_id, message, enhanced_context)

            # حفظ المحادثة مع التفاصيل الموسعة
            if user_id not in self.conversations:
                self.conversations[user_id] = []

            conversation_entry = {
                "message": message,
                "username": username,  # إضافة اسم المستخدم للذاكرة
                "timestamp": datetime.datetime.now().isoformat(),
                "context": enhanced_context,
                "keywords": self.extract_keywords(message),
                "enhanced_data": {
                    "user_memory_accessed": True,
                    "system_knowledge_used": True,
                    "conversation_patterns_analyzed": True
                }
            }
            self.conversations[user_id].append(conversation_entry)

            # توليد الرد الذكي باستخدام الصلاحيات المتقدمة
            if self.gemini_client:
                response = self._call_gemini_ai_advanced(message, username, enhanced_context)
            else:
                response = self._fallback_response_advanced(message, username, enhanced_context)

            # حفظ الرد مع معلومات التحسين
            response_entry = {
                "response": response,
                "username": username,
                "timestamp": datetime.datetime.now().isoformat(),
                "ai_generated": True,
                "intelligence_level": "gemini_ai_advanced" if self.gemini_client else "fallback_advanced",
                "capabilities_used": {
                    "memory_access": True,
                    "system_knowledge": True,
                    "pattern_analysis": True,
                    "enhanced_context": True
                }
            }
            self.conversations[user_id].append(response_entry)

            # تحديث الذاكرة طويلة المدى
            self._update_long_term_memory(username, message, response, enhanced_context)

            self.save_conversations()
            return response

        except Exception as e:
            print(f"❌ خطأ في توليد الرد الذكي المتقدم: {e}")
            return f"😅 عذراً {username}، حدث خطأ في النظام المتقدم. سأحاول مرة أخرى قريباً"

    def _call_gemini_ai_advanced(self, user_message: str, username: str, enhanced_context: Dict) -> str:
        """استدعاء Google Gemini AI مع الصلاحيات والذاكرة المتقدمة"""
        try:
            if not self.gemini_client:
                print("⚠️ Gemini AI غير متاح - استخدام النظام الاحتياطي")
                return self._fallback_response_advanced(user_message, username, enhanced_context)

            # إنشاء prompt متقدم مع جميع المعلومات
            advanced_prompt = self._create_advanced_gemini_prompt(username, enhanced_context)

            # الحصول على تاريخ المحادثة المحسن
            conversation_history = self._get_enhanced_conversation_history_text(username)

            # إعداد الرسالة النهائية مع السياق المتقدم
            full_advanced_prompt = f"""
{advanced_prompt}

=== تاريخ المحادثة السابقة ===
{conversation_history}

=== الرسالة الحالية ===
{username}: {user_message}

=== تعليمات متقدمة ===
استخدم جميع المعلومات المتاحة لتقديم رد ذكي ومخصص مع حس فكاهة مناسب.
الرد يجب أن يكون بين 80-200 كلمة.
"""

            print(f"🤖 جاري استدعاء Gemini AI للمستخدم {username}...")

            # استدعاء Gemini AI مع إعدادات محسنة
            response = self.gemini_client.generate_content(
                full_advanced_prompt,
                generation_config={
                    'temperature': 0.9,  # زيادة الإبداع والفكاهة
                    'top_p': 0.95,
                    'top_k': 50,
                    'max_output_tokens': 250,
                }
            )

            if not response or not response.text:
                print("❌ Gemini AI أرجع رد فارغ")
                return self._fallback_response_advanced(user_message, username, enhanced_context)

            ai_response = response.text.strip()

            # تحسين الرد بناءً على السياق
            enhanced_response = self._enhance_response_with_context(ai_response, enhanced_context, username)

            print(f"✅ Google Gemini AI رد بنجاح على {username}: {enhanced_response[:50]}...")
            return enhanced_response

        except Exception as e:
            print(f"❌ خطأ في Google Gemini AI المتقدم: {e}")
            print(f"🔍 نوع الخطأ: {type(e).__name__}")

            # معالجة أنواع مختلفة من الأخطاء
            if "API_KEY" in str(e).upper():
                print("🔑 مشكلة في مفتاح API - تحقق من صحة المفتاح")
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                print("📊 تم الوصول للحد الأقصى من الطلبات")
            elif "billing" in str(e).lower():
                print("💳 مشكلة في نظام الفوترة")

            return self._fallback_response_advanced(user_message, username, enhanced_context)

    def _get_enhanced_conversation_history(self, username: str) -> List[Dict]:
        """الحصول على تاريخ محادثة محسن ومفصل"""
        history = []

        # البحث في المحادثات بناءً على اسم المستخدم
        for user_id, conversations in self.conversations.items():
            user_conversations = []
            for conv in conversations:
                if conv.get("username") == username:
                    user_conversations.append(conv)

            # أخذ آخر 8 رسائل للسياق
            recent_conversations = user_conversations[-8:]

            for conv in recent_conversations:
                if conv.get("message"):
                    history.append({
                        "role": "user",
                        "content": conv["message"]
                    })
                elif conv.get("response"):
                    history.append({
                        "role": "assistant", 
                        "content": conv["response"]
                    })

        return history

    def _enhance_response_with_context(self, response: str, context: Dict, username: str) -> str:
        """تحسين الرد بناءً على السياق المتقدم"""
        try:
            enhanced_response = response

            # إضافة لمسات شخصية بناءً على السياق
            time_context = context.get('time_context', '')
            room_activity = context.get('room_activity', '')

            # إضافة تحية مناسبة للوقت (أحياناً)
            import random
            if random.random() < 0.3:  # 30% فرصة
                time_greetings = {
                    'صباح': ['صباح الخير', 'صباحك سعيد'],
                    'ظهر': ['نهارك سعيد', 'ظهرك مبارك'], 
                    'مساء': ['مساء الخير', 'مساءك نور'],
                    'ليل': ['مساء الخير', 'سهرة سعيدة']
                }

                if time_context in time_greetings and not any(greeting in enhanced_response for greeting in time_greetings[time_context]):
                    greeting = random.choice(time_greetings[time_context])
                    enhanced_response = f"{greeting} {username}! {enhanced_response}"

            return enhanced_response

        except Exception as e:
            print(f"❌ خطأ في تحسين الرد: {e}")
            return response

    def _update_long_term_memory(self, username: str, message: str, response: str, context: Dict):
        """تحديث الذاكرة طويلة المدى للمستخدم"""
        try:
            if username not in self.ai_memory:
                self.ai_memory[username] = {
                    "first_interaction": datetime.datetime.now().isoformat(),
                    "total_messages": 0,
                    "favorite_topics": [],
                    "personality_traits": [],
                    "interaction_summary": ""
                }

            user_memory = self.ai_memory[username]
            user_memory["total_messages"] += 1
            user_memory["last_interaction"] = datetime.datetime.now().isoformat()

            # تحليل وحفظ المواضيع المفضلة
            topic = context.get('topic', '')
            if topic and topic != 'general':
                if topic not in user_memory["favorite_topics"]:
                    user_memory["favorite_topics"].append(topic)
                    if len(user_memory["favorite_topics"]) > 5:
                        user_memory["favorite_topics"] = user_memory["favorite_topics"][-5:]

            # تحليل وحفظ سمات الشخصية
            sentiment = context.get('sentiment', '')
            if sentiment == 'positive' and 'إيجابي' not in user_memory["personality_traits"]:
                user_memory["personality_traits"].append('إيجابي')
            elif sentiment == 'negative' and 'يحتاج دعم' not in user_memory["personality_traits"]:
                user_memory["personality_traits"].append('يحتاج دعم')

            # الاحتفاظ بأهم 3 سمات فقط
            if len(user_memory["personality_traits"]) > 3:
                user_memory["personality_traits"] = user_memory["personality_traits"][-3:]

            # تحديث ملخص التفاعل
            if user_memory["total_messages"] % 10 == 0:  # كل 10 رسائل
                summary_parts = []
                if user_memory["favorite_topics"]:
                    summary_parts.append(f"يحب الحديث عن: {', '.join(user_memory['favorite_topics'])}")
                if user_memory["personality_traits"]:
                    summary_parts.append(f"الشخصية: {', '.join(user_memory['personality_traits'])}")

                user_memory["interaction_summary"] = " | ".join(summary_parts)

            self.save_ai_memory()

        except Exception as e:
            print(f"❌ خطأ في تحديث الذاكرة طويلة المدى: {e}")

    def _fallback_response_advanced(self, message: str, username: str, context: Dict) -> str:
        """نظام الرد الاحتياطي المتقدم"""
        sentiment = context.get("sentiment", "neutral")
        room_activity = context.get("room_activity", "عادية")
        time_context = context.get("time_context", "")

        # ردود احتياطية ذكية بناءً على السياق المتقدم
        if sentiment == "positive":
            responses = [
                f"😊 طاقتك الإيجابية معدية {username}! الغرفة {room_activity} اليوم",
                f"🌟 أحب تفاؤلك {username}! كده الجو حلو في الغرفة",
                f"😄 مزاجك الحلو ده يخلي الكل مبسوط {username}!"
            ]
        elif sentiment == "negative":
            responses = [
                f"😔 أحس بك {username}... الغرفة هنا دافية وأنا موجود لو عايز تحكي",
                f"💙 ما تخليش الحزن يغلبك {username}، كلنا هنا معاك",
                f"🤗 {username} أنا هنا لو محتاج حد يسمعك، ما تترددش"
            ]
        else:
            time_responses = {
                'صباح': f"🌅 صباح الخير {username}! بداية يوم جديد في الغرفة",
                'ظهر': f"☀️ أهلاً {username}! الغرفة نشطة في الظهيرة دي",
                'مساء': f"🌆 مساء الخير {username}! جو الغرفة حلو المساء ده",
                'ليل': f"🌙 أهلاً {username}! سهرة حلوة في الغرفة الليلة"
            }

            if time_context in time_responses:
                responses = [time_responses[time_context]]
            else:
                responses = [
                    f"🤔 فهمت يا {username}! الغرفة {room_activity} دلوقتي، إيش رأيك نحكي أكتر؟",
                    f"💭 مثير للاهتمام {username}! أحب أعرف رأيك أكتر في الموضوع ده",
                    f"😊 أهلاً {username}! كيف أقدر أساعدك النهارده؟"
                ]

        return random.choice(responses)

    def extract_keywords(self, message: str) -> List[str]:
        """استخراج الكلمات المفتاحية من الرسالة"""
        # إزالة علامات الترقيم والرموز
        cleaned_message = re.sub(r'[^\w\s]', ' ', message)
        words = cleaned_message.split()

        # فلترة الكلمات المهمة (أكثر من 2 أحرف)
        keywords = [word for word in words if len(word) > 2]
        return keywords

    def _get_user_comprehensive_memory(self, username: str) -> str:
        """الحصول على ذاكرة شاملة عن المستخدم"""
        try:
            memory_info = []

            # البحث في الذاكرة العامة
            if hasattr(self, 'ai_memory') and username in self.ai_memory:
                user_memory = self.ai_memory[username]
                memory_info.append(f"📝 الذاكرة المحفوظة: {user_memory.get('summary', 'لا توجد معلومات')}")

            # البحث في المحادثات السابقة  
            conversation_count = 0
            recent_topics = set()

            for user_id, conversations in self.conversations.items():
                if any(conv.get('username') == username for conv in conversations):
                    conversation_count += len(conversations)
                    for conv in conversations[-5:]:  # آخر 5 محادثات
                        if conv.get('context', {}).get('topic'):
                            recent_topics.add(conv['context']['topic'])

            if conversation_count > 0:
                memory_info.append(f"💬 عدد المحادثات السابقة: {conversation_count}")
                if recent_topics:
                    memory_info.append(f"🎯 المواضيع الأخيرة: {', '.join(recent_topics)}")

            # معلومات من نظام إدارة المستخدمين
            if hasattr(self, 'user_manager'):
                # محاولة الوصول إلى معلومات المستخدم
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                    from main import bot_instance

                    if hasattr(bot_instance, 'user_manager'):
                        user_info = bot_instance.user_manager.get_user_info_from_people(username)
                        if user_info:
                            memory_info.append(f"👤 معلومات المستخدم: زائر منذ {user_info.get('first_visit', 'غير معروف')[:10]}")
                            memory_info.append(f"📊 عدد الزيارات: {user_info.get('visit_count', 0)}")
                            memory_info.append(f"🏷️ نوع المستخدم: {user_info.get('user_type', 'عادي')}")
                except:
                    pass

            if memory_info:
                return "\n".join(memory_info)
            else:
                return "👤 مستخدم جديد - لا توجد معلومات سابقة"

        except Exception as e:
            print(f"❌ خطأ في الحصول على ذاكرة المستخدم: {e}")
            return "❌ تعذر الوصول للذاكرة"

    def _get_system_knowledge(self) -> str:
        """الحصول على معرفة شاملة عن النظام والبوت"""
        try:
            system_info = []

            # معلومات عن البوت وإمكانياته
            system_info.append("🤖 إمكانيات البوت:")
            system_info.append("- الرقص والرقصات المخصصة")
            system_info.append("- إدارة المستخدمين والمشرفين")
            system_info.append("- الأوامر المخصصة والتنقل")
            system_info.append("- النشاطات التلقائية والمراقبة")

            # معلومات عن الغرفة
            try:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from main import bot_instance

                if hasattr(bot_instance, 'user_manager'):
                    active_users = bot_instance.user_manager.get_active_users_count()
                    total_users = bot_instance.user_manager.get_total_users_count()
                    system_info.append(f"📊 الغرفة: {active_users} نشط، {total_users} إجمالي")

                if hasattr(bot_instance, 'quiet_mode'):
                    mode = "هادئ" if bot_instance.quiet_mode else "عادي"
                    system_info.append(f"🔊 وضع البوت: {mode}")

            except Exception as e:
                system_info.append("📊 الغرفة: معلومات غير متاحة حالياً")

            return "\n".join(system_info)

        except Exception as e:
            print(f"❌ خطأ في الحصول على معرفة النظام: {e}")
            return "🤖 البوت: نظام Highrise متقدم"

    def _get_conversation_patterns(self, username: str) -> str:
        """تحليل أنماط المحادثة للمستخدم"""
        try:
            patterns = []

            # تحليل المحادثات السابقة
            user_conversations = []
            for user_id, conversations in self.conversations.items():
                # التأكد من أن conversations هو قائمة
                if not isinstance(conversations, list):
                    continue

                for conv in conversations:
                    if not isinstance(conv, dict):
                        continue
                    if conv.get('username') == username:
                        user_conversations.append(conv)

            if user_conversations:
                # تحليل الأوقات المفضلة
                times = [conv.get('timestamp', '') for conv in user_conversations[-10:]]
                # تحليل المواضيع المتكررة  
                topics = [conv.get('context', {}).get('topic', '') for conv in user_conversations[-10:]]
                # تحليل المشاعر السائدة
                sentiments = [conv.get('context', {}).get('sentiment', '') for conv in user_conversations[-10:]]

                if topics:
                    common_topics = list(set([t for t in topics if t]))
                    if common_topics:
                        patterns.append(f"🎯 المواضيع المفضلة: {', '.join(common_topics[:3])}")

                if sentiments:
                    positive_count = sentiments.count('positive')
                    negative_count = sentiments.count('negative')
                    if positive_count > negative_count:
                        patterns.append("😊 مزاج إيجابي عموماً")
                    elif negative_count > positive_count:
                        patterns.append("😔 يحتاج دعم ومساندة")

                patterns.append(f"💬 نشاط المحادثة: {len(user_conversations)} رسالة سابقة")
            else:
                patterns.append("🆕 بداية علاقة جديدة - لا توجد أنماط سابقة")

            return "\n".join(patterns) if patterns else "📝 لا توجد أنماط محددة بعد"

        except Exception as e:
            print(f"❌ خطأ في تحليل أنماط المحادثة: {e}")
            return "📊 تحليل الأنماط غير متاح"

    def _enhance_context_with_system_data(self, context: Dict, username: str) -> Dict:
        """تحسين السياق بمعلومات النظام"""
        try:
            # إضافة معلومات متقدمة للسياق
            enhanced_context = context.copy()

            # إضافة معلومات الوقت
            import datetime
            current_hour = datetime.datetime.now().hour
            if 5 <= current_hour < 12:
                enhanced_context['time_context'] = 'صباح'
            elif 12 <= current_hour < 17:
                enhanced_context['time_context'] = 'ظهر'
            elif 17 <= current_hour < 21:
                enhanced_context['time_context'] = 'مساء'
            else:
                enhanced_context['time_context'] = 'ليل'

            # إضافة معلومات النشاط في الغرفة
            try:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from main import bot_instance

                if hasattr(bot_instance, 'user_manager'):
                    active_count = bot_instance.user_manager.get_active_users_count()
                    if active_count > 10:
                        enhanced_context['room_activity'] = 'مزدحمة'
                    elif active_count > 5:
                        enhanced_context['room_activity'] = 'نشطة'
                    else:
                        enhanced_context['room_activity'] = 'هادئة'

            except:
                enhanced_context['room_activity'] = 'عادية'

            # إضافة تقييم التفاعل
            if username in self.conversation_memory:
                user_memory = self.conversation_memory[username]
                if len(user_memory.get('topics', [])) > 3:
                    enhanced_context['engagement_level'] = 'عالي'
                elif len(user_memory.get('topics', [])) > 1:
                    enhanced_context['engagement_level'] = 'متوسط'
                else:
                    enhanced_context['engagement_level'] = 'مبتدئ'

            return enhanced_context

        except Exception as e:
            print(f"❌ خطأ في تحسين السياق: {e}")
            return context

    def get_ai_stats(self) -> Dict:
        """إحصائيات الذكاء الاصطناعي المتقدمة"""
        total_users = len(self.active_ai_users)
        total_conversations = len(self.conversations)
        total_messages = sum(user_data.get("message_count", 0) for user_data in self.active_ai_users.values())

        # إحصائيات متقدمة
        topics_discussed = []
        for conv in self.conversations.values():
            for entry in conv:
                if "context" in entry and "topic" in entry["context"]:
                    topics_discussed.append(entry["context"]["topic"])

        unique_topics = len(set(topics_discussed))

        return {
            "active_users": total_users,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "unique_topics_discussed": unique_topics,
            "activation_code": self.activation_code,
            "intelligence_level": "gemini_ai" if self.gemini_client else "fallback",
            "api_status": "متصل" if self.gemini_client else "غير متاح",
            "features": ["google_gemini_integration", "contextual_understanding", "emotional_intelligence", "memory_retention", "humor_sense"]
        }

# إنشاء مثيل مدير الذكاء الاصطناعي المتقدم
ai_chat_manager = AdvancedAIChatManager()