
# ===================================================================
# ملف إعدادات البوت والمطور والغرفة
# تم إنشاؤه لفصل البيانات الحساسة عن الكود الرئيسي
# ===================================================================

# معلومات المطور
DEVELOPER_INFO = {
    "name": "HR_LY",  # اسم المطور
    "id": "65402b9fffc87c0146e3dcb3",  # معرف المطور في Highrise
    "username": "HR_LY",  # اسم المستخدم للمطور
    "team": "EDX Team",  # فريق التطوير
    "contact": "jin__2007@edx.com"  # معلومات التواصل (اختياري)
}

# معلومات البوت
BOT_CONFIG = {
    "bot_token": "7a5159bda86d3aef9306b94c6812a7b2fe0d78e722db877b4ba50367be73c82e",  # توكن البوت
    "bot_id": "6a3bcee2d33297264d0b776b",  # معرف البوت
    "bot_name": "EDX Bot",  # اسم البوت
    "bot_version": "3.0",  # إصدار البوت
    "created_date": "2025-01-01",  # تاريخ الإنشاء
    "description": "مرحبا انا بوت ليبي من تطوير وانشاء @HR_LY"  # وصف البوت
}

# معلومات الغرفة
ROOM_CONFIG = {
    "room_id": "6a3bcbc516d6ea320bb39984",  # معرف الغرفة
    "room_name": "EDX Room",  # اسم الغرفة (اختياري)
    "room_type": "public",  # نوع الغرفة
    "max_users": 50,  # أقصى عدد مستخدمين (اختياري)
    "language": "ar",  # لغة الغرفة
    "region": "Middle East"  # المنطقة الجغرافية
}

# إعدادات الأمان والصلاحيات
SECURITY_CONFIG = {
    "owner_id": DEVELOPER_INFO["id"],  # معرف المالك
    "owner_username": DEVELOPER_INFO["username"],  # اسم المالك
    "admin_commands_enabled": True,  # تفعيل أوامر الإدارة
    "HR_LY": False  # وضع التطوير
    # ملاحظة: أسماء فريق EDX محفوظة في ملف محمي منفصل
}

# إعدادات الخادم والشبكة
SERVER_CONFIG = {
    "web_port": 8080,  # منفذ الخادم
    "backup_port": 5000,  # منفذ احتياطي
    "host": "0.0.0.0",  # عنوان الخادم
    "debug": False,  # وضع التطوير للخادم
    "threaded": True  # دعم العمليات المتوازية
}

# إعدادات قاعدة البيانات والملفات
DATA_CONFIG = {
    "data_folder": "data",  # مجلد البيانات
    "backup_folder": "backups",  # مجلد النسخ الاحتياطية
    "logs_folder": "chat_logs",  # مجلد السجلات
    "auto_backup": True,  # النسخ الاحتياطي التلقائي
    "backup_interval": 3600  # فترة النسخ الاحتياطي بالثواني (ساعة واحدة)
}

# دالة للحصول على التوكن
def get_bot_token():
    """إرجاع توكن البوت"""
    return BOT_CONFIG["bot_token"]

# دالة للحصول على معرف الغرفة
def get_room_id():
    """إرجاع معرف الغرفة"""
    return ROOM_CONFIG["room_id"]

# دالة للحصول على معرف المطور
def get_developer_id():
    """إرجاع معرف المطور"""
    return DEVELOPER_INFO["id"]

# دالة للحصول على معرف البوت
def get_bot_id():
    """إرجاع معرف البوت"""
    return BOT_CONFIG["bot_id"]

# دالة للتحقق من صحة الإعدادات
def validate_config():
    """التحقق من صحة جميع الإعدادات"""
    errors = []

    # فحص توكن البوت
    if not BOT_CONFIG["bot_token"] or len(BOT_CONFIG["bot_token"]) < 30:
        errors.append("❌ توكن البوت غير صحيح")

    # فحص معرف الغرفة
    if not ROOM_CONFIG["room_id"] or len(ROOM_CONFIG["room_id"]) < 20:
        errors.append("❌ معرف الغرفة غير صحيح")

    # فحص معرف المطور
    if not DEVELOPER_INFO["id"] or len(DEVELOPER_INFO["id"]) < 20:
        errors.append("❌ معرف المطور غير صحيح")

    # فحص معرف البوت
    if not BOT_CONFIG["bot_id"] or len(BOT_CONFIG["bot_id"]) < 20:
        errors.append("❌ معرف البوت غير صحيح")

    if errors:
        return False, errors
    else:
        return True, ["✅ جميع الإعدادات صحيحة"]

# دالة لطباعة ملخص الإعدادات
def print_config_summary():
    """طباعة ملخص الإعدادات"""
    print("🔧 ملخص إعدادات البوت:")
    print(f"   👤 المطور: {DEVELOPER_INFO['name']} ({DEVELOPER_INFO['id'][:10]}...)")
    print(f"   🤖 البوت: {BOT_CONFIG['bot_name']} ({BOT_CONFIG['bot_id'][:10]}...)")
    print(f"   🏠 الغرفة: {ROOM_CONFIG['room_id'][:10]}...")
    print(f"   🔑 التوكن: {BOT_CONFIG['bot_token'][:10]}...")
    print(f"   🌐 الخادم: {SERVER_CONFIG['host']}:{SERVER_CONFIG['web_port']}")

    # التحقق من صحة الإعدادات
    is_valid, messages = validate_config()
    for message in messages:
        print(f"   {message}")

# تشغيل الفحص عند استيراد الملف
if __name__ == "__main__":
    print("📋 فحص ملف الإعدادات...")
    print_config_summary()
