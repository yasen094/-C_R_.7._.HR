"""
أوامر المشرفين المبسطة
"""
import asyncio
from highrise import Position, User

class ModeratorCommands:
    def __init__(self, bot):
        self.bot = bot
        print("👮‍♂️ أوامر المشرفين المبسطة جاهزة")

    async def handle_command(self, user: User, message: str) -> str:
        """معالجة أوامر المشرفين"""
        try:
            # التحقق من الصلاحيات أولاً
            is_moderator = self.bot.user_manager.is_moderator(user.username)
            is_owner = self.bot.user_manager.is_owner(user.username)

            # قائمة الأوامر التي تتطلب صلاحيات مشرف
            moderator_commands = [
                "حفظ", "اذهب", "الاماكن", "احذف مكان", "عدد الاماكن",
                "اسحبهم", "جيب @", "بدل ", "bot_dance", "رقص البوت",
                "تغيير", "ريأكشن ", "المشرفين", "فحص @", "فحصني",
                "احصائيات_الغرفة", "قائمة_المشرفين", "ثبت @", "الغ ثبت @",
                "إلغاء_التثبيت @", "سجن @", "المثبتين", "ايقاف @", "طرد @"
            ]

            # فحص إذا كان الأمر يتطلب صلاحيات
            command_requires_mod = any(message.startswith(cmd) or message == cmd.strip() for cmd in moderator_commands)

            # أوامر المالك والمطورين
            owner_developer_commands = ["promote ", "demote "]
            owner_only_commands = ["اضافة_مشرف @", "ازالة_مشرف @"]

            command_requires_owner = any(message.startswith(cmd) for cmd in owner_only_commands)
            command_requires_owner_or_developer = any(message.startswith(cmd) for cmd in owner_developer_commands)

            # رد على غير المشرفين
            if command_requires_owner and not is_owner:
                return f"❌ المعذرة يا {user.username}، الأمر ده للريس بس! إنت مش صاحب البوت"

            is_developer = self.bot.user_manager.is_developer(user.username)
            if command_requires_owner_or_developer and not is_owner and not is_developer:
                return f"❌ المعذرة يا {user.username}، الأمر ده للمالك والمطورين فقط!"

            if command_requires_mod and not is_moderator and not is_owner:
                user_type = self.bot.user_manager.get_user_type(user.username, user.id)
                return f"❌ آسف يا {user.username}، الأمر ده للمشرفين بس!\n👤 إنت: {user_type}\n💡 كلم المشرفين علشان يدوك الصلاحيات"
            # أوامر الأماكن (للمشرفين والمالك)
            if message == "حفظ":
                try:
                    return await self.bot.position_manager.save_current_position(
                        self.bot.highrise, user.username
                    )
                except Exception as e:
                    print(f"خطأ في أمر حفظ: {e}")
                    return f"❌ في مشكلة في حفظ المكان: {str(e)}"

            elif message.startswith("حفظ "):
                try:
                    position_name = message[4:].strip()
                    if position_name:
                        return await self.bot.position_manager.save_current_position(
                            self.bot.highrise, user.username, position_name
                        )
                    else:
                        return "❌ لازم تكتب اسم المكان بعد كلمة 'حفظ'"
                except Exception as e:
                    print(f"خطأ في أمر حفظ: {e}")
                    return f"❌ في مشكلة في حفظ المكان: {str(e)}"

            elif message == "اذهب":
                return await self.bot.position_manager.teleport_to_saved_position(self.bot.highrise)

            elif message.startswith("اذهب "):
                try:
                    position_identifier = message[5:].strip()
                    if position_identifier:
                        # فحص إذا كان رقم أو اسم
                        if position_identifier.isdigit():
                            position_number = int(position_identifier)
                            # تحويل الرقم إلى اسم المكان
                            positions_list = list(self.bot.position_manager.positions.keys())
                            if 1 <= position_number <= len(positions_list):
                                position_name = positions_list[position_number - 1]
                                return await self.bot.position_manager.teleport_to_saved_position(
                                    self.bot.highrise, position_name
                                )
                            else:
                                return f"❌ رقم المكان غير صحيح. الأرقام المتاحة: 1-{len(positions_list)}"
                        else:
                            # اسم المكان مباشرة
                            return await self.bot.position_manager.teleport_to_saved_position(
                                self.bot.highrise, position_identifier
                            )
                    else:
                        return "❌ يرجى كتابة اسم أو رقم المكان بعد 'اذهب'"
                except Exception as e:
                    print(f"خطأ في أمر اذهب: {e}")
                    return f"❌ خطأ في الانتقال: {str(e)}"

            elif message == "الاماكن":
                return self.bot.position_manager.get_saved_positions_list()

            elif message.startswith("احذف مكان "):
                position_name = message[11:].strip()
                if position_name:
                    return self.bot.position_manager.delete_saved_position(position_name)
                else:
                    return "❌ لازم تكتب اسم المكان بعد 'احذف مكان'"

            elif message == "عدد الاماكن":
                count = self.bot.position_manager.get_positions_count()
                return f"📍 عدد الأماكن المحفوظة: {count} مكان"

            elif message == "اصلح الاماكن":
                return self.bot.position_manager.fix_corrupted_positions()

            # أوامر السحب والنقل
            elif message == "اسحبهم":
                result = await self.pull_users_around_moderator(user)
                if result.startswith("✅"):
                    is_owner = self.bot.user_manager.is_owner(user.username)
                    if is_owner:
                        result += f"\n👑 تم تنفيذ الأمر بنجاح يا صاحب البوت!"
                    else:
                        result += f"\n👮‍♂️ أحسنت يا مشرف! تم التنفيذ بنجاح"
                return result

            elif message.startswith("جيب @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    # للمشرفين: جلب المستخدم إلى مكان المشرف
                    if is_moderator or is_owner:
                        result = await self.bring_user_to_moderator(user, target_username)
                        if result.startswith("✅"):
                            await self.bot.highrise.chat(f"💀 تم اختراق المستخدم @{target_username} - تم سحبه بالقوة!")
                        return result
                    else:
                        # للمستخدمين العاديين: نقلهم إلى المستخدم المحدد
                        return await self.bring_user_to_user(user, target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'جيب @'"

            elif message.startswith("بدل "):
                parts = message[4:].strip().split()
                users_to_swap = []
                for part in parts:
                    username = part.replace("@", "").strip()
                    if username:
                        users_to_swap.append(username)

                if len(users_to_swap) == 2:
                    return await self.swap_users_positions(users_to_swap[0], users_to_swap[1])
                else:
                    return "❌ يرجى كتابة اسمين مستخدمين بعد 'بدل @ @'"

            elif message == "bot_dance" or message == "رقص البوت":
                try:
                    if not self.bot.bot_auto_emote["active"]:
                        self.bot.bot_auto_emote["active"] = True
                        task = asyncio.create_task(self.bot.repeat_emote_for_bot())
                        self.bot.bot_auto_emote["task"] = task
                        return "🤖 بدأ البوت الرقص العشوائي المتكرر"
                    else:
                        self.bot.bot_auto_emote["active"] = False
                        if self.bot.bot_auto_emote.get("task"):
                            self.bot.bot_auto_emote["task"].cancel()
                        return "⏹️ تم إيقاف رقص البوت"
                except Exception as e:
                    return f"❌ خطأ في رقص البوت: {str(e)}"

            # أمر تغيير الملابس
            elif message == "تغيير":
                return await self.change_bot_outfit()

            # أوامر الريأكشنز
            elif message.startswith("ريأكشن "):
                try:
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        return "❌ استخدام خاطئ! المثال: ريأكشن قلب @اسم_المستخدم"

                    reaction_type = parts[1]
                    username = parts[2].replace("@", "")

                    result = await self.bot.send_reaction_to_user(username, reaction_type)
                    return result
                except Exception as e:
                    return f"❌ خطأ في إرسال الريأكشن: {str(e)}"

            # أوامر إدارة المشرفين للمالك فقط
            elif message.startswith("اضافة_مشرف @"):
                if not self.bot.user_manager.is_owner(user.username):
                    return f"❌ المعذرة يا {user.username}، هذا الأمر للمالك فقط!"

                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    username_to_add = parts[1][1:]  # إزالة @ من اسم المستخدم
                    result = self.bot.user_manager.add_moderator(username_to_add)
                    print(f"🔧 تم تنفيذ أمر إضافة مشرف: {username_to_add} بواسطة {user.username}")

                    # إضافة رسالة إضافية للتأكيد
                    if result.startswith("✅"):
                        confirmation_msg = f"🎉 تهانينا! {username_to_add} أصبح الآن مشرفاً في البوت"
                        try:
                            await self.bot.highrise.chat(confirmation_msg)
                        except:
                            pass

                    return result
                else:
                    return "❌ الصيغة الصحيحة: اضافة_مشرف @اسم_المستخدم"

            elif message.startswith("ازالة_مشرف @"):
                if not self.bot.user_manager.is_owner(user.username):
                    return f"❌ المعذرة يا {user.username}، هذا الأمر للمالك فقط!"

                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    username_to_remove = parts[1][1:]  # إزالة @ من اسم المستخدم
                    result = self.bot.user_manager.remove_moderator(username_to_remove)
                    print(f"🔧 تم تنفيذ أمر إزالة مشرف: {username_to_remove} بواسطة {user.username}")

                    # إضافة رسالة إضافية للتأكيد
                    if result.startswith("✅"):
                        confirmation_msg = f"📝 تم إزالة {username_to_remove} من قائمة المشرفين"
                        try:
                            await self.bot.highrise.chat(confirmation_msg)
                        except:
                            pass

                    return result
                else:
                    return "❌ الصيغة الصحيحة: ازالة_مشرف @اسم_المستخدم"

            # أوامر إدارة صلاحيات الغرفة (Room Privileges)
            elif message.startswith("promote "):
                is_developer = self.bot.user_manager.is_developer(user.username)
                if not is_owner and not is_developer:
                    return f"❌ المعذرة يا {user.username}، أمر promote للمالك والمطورين فقط!"

                try:
                    parts = message.split()
                    if len(parts) != 3:
                        return "❌ صيغة خاطئة! الاستخدام: promote @اسم_المستخدم moderator/designer"

                    command, username_part, role = parts

                    # تنظيف اسم المستخدم
                    if username_part.startswith("@"):
                        target_username = username_part[1:]
                    else:
                        target_username = username_part

                    # فحص الدور المطلوب
                    if role.lower() not in ["moderator", "designer"]:
                        return "❌ دور غير صحيح! يجب أن يكون: moderator أو designer"

                    # البحث عن المستخدم في الغرفة
                    room_users = (await self.bot.highrise.get_room_users()).content
                    target_user_id = None

                    for room_user, pos in room_users:
                        if room_user.username.lower() == target_username.lower():
                            target_user_id = room_user.id
                            break

                    if not target_user_id:
                        return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

                    # الحصول على الصلاحيات الحالية وترقيتها
                    permissions = await self.bot.highrise.get_room_privilege(target_user_id)
                    setattr(permissions, role.lower(), True)

                    # تطبيق الصلاحيات الجديدة
                    await self.bot.highrise.change_room_privilege(target_user_id, permissions)

                    # تسجيل التغيير في نظام البوت
                    if role.lower() == "moderator":
                        self.bot.user_manager.add_moderator(target_username)

                    role_arabic = "مشرف غرفة" if role.lower() == "moderator" else "مصمم"
                    return f"✅ تم ترقية {target_username} إلى {role_arabic} بنجاح!"

                except Exception as e:
                    print(f"خطأ في أمر promote: {e}")
                    if "can't edit this room" in str(e).lower():
                        return f"❌ البوت لا يملك صلاحيات المالك في هذه الغرفة!\n💡 حل بديل: استخدم 'اضافة_مشرف @{target_username}' لإضافته في نظام البوت"
                    return f"❌ خطأ في الترقية: {str(e)}"

            elif message.startswith("demote "):
                is_developer = self.bot.user_manager.is_developer(user.username)
                if not is_owner and not is_developer:
                    return f"❌ المعذرة يا {user.username}، أمر demote للمالك والمطورين فقط!"

                try:
                    parts = message.split()
                    if len(parts) != 3:
                        return "❌ صيغة خاطئة! الاستخدام: demote @اسم_المستخدم moderator/designer"

                    command, username_part, role = parts

                    # تنظيف اسم المستخدم
                    if username_part.startswith("@"):
                        target_username = username_part[1:]
                    else:
                        target_username = username_part

                    # فحص الدور المطلوب
                    if role.lower() not in ["moderator", "designer"]:
                        return "❌ دور غير صحيح! يجب أن يكون: moderator أو designer"

                    # البحث عن المستخدم في الغرفة
                    room_users = (await self.bot.highrise.get_room_users()).content
                    target_user_id = None

                    for room_user, pos in room_users:
                        if room_user.username.lower() == target_username.lower():
                            target_user_id = room_user.id
                            break

                    if not target_user_id:
                        return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

                    # الحصول على الصلاحيات الحالية وإزالة الدور
                    permissions = await self.bot.highrise.get_room_privilege(target_user_id)
                    setattr(permissions, role.lower(), False)

                    # تطبيق الصلاحيات الجديدة
                    await self.bot.highrise.change_room_privilege(target_user_id, permissions)

                    # إزالة من نظام البوت إذا كان مشرف
                    if role.lower() == "moderator":
                        self.bot.user_manager.remove_moderator(target_username)

                    role_arabic = "مشرف غرفة" if role.lower() == "moderator" else "مصمم"
                    return f"✅ تم تنزيل {target_username} من منصب {role_arabic} بنجاح!"

                except Exception as e:
                    print(f"خطأ في أمر demote: {e}")
                    if "can't edit this room" in str(e).lower():
                        return f"❌ البوت لا يملك صلاحيات المالك في هذه الغرفة!\n💡 حل بديل: استخدم 'ازالة_مشرف @{target_username}' لإزالته من نظام البوت"
                    return f"❌ خطأ في التنزيل: {str(e)}"

            # أوامر المعلومات
            elif message == "غرفة":
                result = await self.bot.room_moderator_detector.sync_moderators_with_room_settings()
                return result

            elif message == "المشرفين":
                moderators = self.bot.user_manager.get_moderators_list()
                is_owner = self.bot.user_manager.is_owner(user.username)

                if moderators:
                    mods_text = " | ".join(moderators[:10])
                    if is_owner:
                        return f"👑 قائمة المشرفين لصاحب البوت ({len(moderators)}): {mods_text}\n💡 يمكنك إضافة أو إزالة المشرفين"
                    else:
                        return f"👮‍♂️ المشرفين ({len(moderators)}): {mods_text}"
                else:
                    return "❌ لا يوجد مشرفين"

            elif message.startswith("فحص @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    result = self.bot.user_manager.get_user_permissions_info(target_username)
                    return result
                else:
                    return "❌ الصيغة الصحيحة: فحص @اسم_المستخدم"

            elif message == "فحصني":
                result = self.bot.user_manager.get_user_permissions_info(user.username)
                return result

            elif message.startswith("فحص_صلاحيات @"):
                if not is_moderator and not is_owner:
                    return f"❌ آسف يا {user.username}، هذا الأمر للمشرفين فقط!"

                try:
                    parts = message.split()
                    if len(parts) >= 2 and parts[1].startswith("@"):
                        target_username = parts[1][1:]

                        # البحث عن المستخدم في الغرفة
                        room_users = (await self.bot.highrise.get_room_users()).content
                        target_user_id = None

                        for room_user, pos in room_users:
                            if room_user.username.lower() == target_username.lower():
                                target_user_id = room_user.id
                                break

                        if not target_user_id:
                            return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

                        # الحصول على صلاحيات الغرفة
                        permissions = await self.bot.highrise.get_room_privilege(target_user_id)

                        result = f"🔍 صلاحيات الغرفة لـ {target_username}:\n"
                        result += f"👮‍♂️ مشرف غرفة: {'✅ نعم' if permissions.moderator else '❌ لا'}\n"
                        result += f"🎨 مصمم: {'✅ نعم' if permissions.designer else '❌ لا'}\n"

                        # إضافة معلومات من نظام البوت
                        bot_info = self.bot.user_manager.get_user_permissions_info(target_username)
                        result += f"\n📋 معلومات البوت:\n{bot_info}"

                        return result

                    else:
                        return "❌ الصيغة الصحيحة: فحص_صلاحيات @اسم_المستخدم"

                except Exception as e:
                    return f"❌ خطأ في فحص الصلاحيات: {str(e)}"

            elif message == "احصائيات_الغرفة":
                return self.bot.user_manager.get_room_statistics()

            elif message == "قائمة_المشرفين":
                mods_list = self.bot.user_manager.get_moderators_list()
                if mods_list:
                    owners = [m for m in mods_list if self.bot.user_manager.is_owner(m)]
                    others = [m for m in mods_list if not self.bot.user_manager.is_owner(m)]

                    result = f"👮‍♂️ قائمة المشرفين ({len(mods_list)}):\n"

                    if owners:
                        result += f"👑 المالكين: {' | '.join(owners)}\n"

                    if others:
                        result += f"🛡️ المشرفين: {' | '.join(others[:15])}"
                        if len(others) > 15:
                            result += f" + {len(others) - 15} آخرين"

                    return result
                else:
                    return "❌ لا يوجد مشرفين مسجلين"

            elif message == "مزامنة_الصلاحيات":
                if not is_owner:
                    return f"❌ المعذرة يا {user.username}، هذا الأمر للمالك فقط!"

                try:
                    room_users = (await self.bot.highrise.get_room_users()).content
                    synced_count = 0

                    for room_user, pos in room_users:
                        try:
                            permissions = await self.bot.highrise.get_room_privilege(room_user.id)

                            # إذا كان مشرف غرفة، أضفه لنظام البوت
                            if permissions.moderator:
                                if not self.bot.user_manager.is_moderator(room_user.username):
                                    self.bot.user_manager.add_moderator(room_user.username)
                                    synced_count += 1

                        except Exception as e:
                            print(f"خطأ في مزامنة {room_user.username}: {e}")
                            continue

                    return f"✅ تم مزامنة {synced_count} مشرف من صلاحيات الغرفة إلى نظام البوت"

                except Exception as e:
                    return f"❌ خطأ في المزامنة: {str(e)}"

            # أوامر التثبيت والسجن
            elif message.startswith("ثبت @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    result = await self.freeze_user(target_username)
                    if result.startswith("✅"):
                        await self.bot.highrise.chat(f"💀 تم اختراق المستخدم @{target_username} - نظام الحركة معطل!")
                    return result
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'ثبت @'"

            elif message.startswith("الغ ثبت @") or message.startswith("إلغاء_التثبيت @"):
                parts = message.split()
                if message.startswith("الغ ثبت @"):
                    # التعامل مع "الغ ثبت @اسم_المستخدم"
                    if len(parts) >= 3 and parts[2].startswith("@"):
                        target_username = parts[2][1:]  # إزالة @ من اسم المستخدم
                        return await self.unfreeze_user(target_username)
                    else:
                        return "❌ الصيغة الصحيحة: الغ ثبت @اسم_المستخدم"
                elif message.startswith("إلغاء_التثبيت @"):
                    # التعامل مع "إلغاء_التثبيت @اسم_المستخدم"
                    if len(parts) >= 2 and parts[1].startswith("@"):
                        target_username = parts[1][1:]  # إزالة @ من اسم المستخدم
                        return await self.unfreeze_user(target_username)
                    else:
                        return "❌ الصيغة الصحيحة: إلغاء_التثبيت @اسم_المستخدم"

            elif message.startswith("سجن @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.jail_user(target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'سجن @'"

            # أوامر الريأكشن للجميع
            elif message == "قلوب":
                return await self.send_reaction_to_all("heart")

            elif message == "تحية":
                return await self.send_reaction_to_all("wave")

            elif message == "تصفيق":
                return await self.send_reaction_to_all("clap")

            elif message == "اعجاب":
                return await self.send_reaction_to_all("thumbs")

            elif message == "غمزة":
                return await self.send_reaction_to_all("wink")

            elif message == "قبلة":
                return await self.send_reaction_to_all("kiss")

            elif message == "ضحك":
                return await self.send_reaction_to_all("laugh")

            elif message == "محتار":
                return await self.send_reaction_to_all("confused")

            elif message == "قائمة_الريأكشنز" or message == "الريأكشنز":
                return self.get_available_reactions()

            elif message.startswith("ريأكشن "):
                parts = message.split(" ", 1)
                if len(parts) >= 2:
                    reaction_type = parts[1].strip()
                    return await self.send_reaction_to_all(reaction_type)
                else:
                    return "❌ استخدام خاطئ! المثال: ريأكشن heart"

            elif message == "المثبتين":
                return self.get_frozen_users_list()

            # أوامر النقل للمستخدمين العاديين
            elif message.startswith("وديني @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.teleport_user_to_target(user, target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'وديني @'"

            elif message.startswith("جيب @") and not self.bot.user_manager.is_moderator(user.username):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.bring_user_to_user(user, target_username)
                else:
                    return "❌ يرجى كتابة اسم المستخدم بعد 'جيب @'"

            elif message.startswith("اعكس @"):
                parts = message.split()
                if len(parts) >= 3 and parts[1].startswith("@") and parts[2].startswith("@"):
                    # عكس بين مستخدمين محددين
                    username1 = parts[1][1:]  # إزالة @
                    username2 = parts[2][1:]  # إزالة @
                    return await self.swap_users_positions(username1, username2)
                elif len(parts) >= 2 and parts[1].startswith("@"):
                    # عكس بين الطالب والمستخدم المحدد (الطريقة القديمة)
                    target_username = parts[1][1:]
                    return await self.swap_with_user(user, target_username)
                else:
                    return "❌ الصيغة الصحيحة: اعكس @اسم1 @اسم2 (لعكس مستخدمين) أو اعكس @اسم (لعكس معك)"

            elif message.startswith("ايقاف @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.stop_user_emote(target_username)
                else:
                    return "❌ الصيغة الصحيحة: ايقاف @اسم_المستخدم"

            elif message.startswith("طرد @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.kick_user(target_username)
                else:
                    return "❌ الصيغة الصحيحة: طرد @اسم_المستخدم"

            

            elif message == "ايقاف_الملاحقة":
                if is_moderator or is_owner:
                    return await self.stop_following_all()
                else:
                    return f"❌ آسف يا {user.username}، الأمر ده للمشرفين بس!"

            elif message == "الملاحقين":
                return self.get_following_list()

            

            elif message.lower() in ["فحص_الجولد", "فحص_المحفظة", "check_wallet"]:
                return await self.check_bot_wallet_detailed()

            # أوامر إدارة VIP
            elif message.lower() in ["قائمة_vip", "vip_list", "الـvip"]:
                return self.bot.user_manager.get_vip_list()

            elif message.startswith("اضافة_vip @"):
                if not self.bot.user_manager.is_owner(user.username):
                    return f"❌ المعذرة يا {user.username}، هذا الأمر للمالك فقط!"

                # تحديد نوع الأمر واستخراج اسم المستخدم
                if message.startswith("اضافة_vip @"):
                    username_to_add = message[11:].strip()  # إزالة "اضافة_vip @"
                elif message.startswith("إضافة vip @"):
                    username_to_add = message[11:].strip()  # إزالة "إضافة vip @"
                elif message.startswith("إضافة_vip @"):
                    username_to_add = message[12:].strip()  # إزالة "إضافة_vip @"
                elif message.startswith("اضافة vip @"):
                    username_to_add = message[10:].strip()  # إزالة "اضافة vip @"
                else:
                    parts = message.split()
                    if len(parts) >= 2 and parts[1].startswith("@"):
                        username_to_add = parts[1][1:]  # إزالة @ من اسم المستخدم
                    else:
                        return "❌ الصيغة الصحيحة: اضافة_vip @اسم_المستخدم"

                result = self.bot.user_manager.add_vip(username_to_add)
                print(f"🔧 تم تنفيذ أمر إضافة VIP: {username_to_add} بواسطة {user.username}")

                # إضافة رسالة إضافية للتأكيد
                if result.startswith("✅"):
                    confirmation_msg = f"🎉 تهانينا! {username_to_add} أصبح الآن VIP في البوت"
                    try:
                        await self.bot.highrise.chat(confirmation_msg)
                    except:
                        pass

                return result

            elif message.startswith("ازالة_vip @"):
                if not self.bot.user_manager.is_owner(user.username):
                    return f"❌ المعذرة يا {user.username}، هذا الأمر للمالك فقط!"

                # تحديد نوع الأمر واستخراج اسم المستخدم
                if message.startswith("ازالة_vip @"):
                    username_to_remove = message[11:].strip()  # إزالة "ازالة_vip @"
                elif message.startswith("إزالة vip @"):
                    username_to_remove = message[11:].strip()  # إزالة "إزالة vip @"
                elif message.startswith("إزالة_vip @"):
                    username_to_remove = message[12:].strip()  # إزالة "إزالة_vip @"
                elif message.startswith("ازالة vip @"):
                    username_to_remove = message[10:].strip()  # إزالة "ازالة vip @"
                else:
                    parts = message.split()
                    if len(parts) >= 2 and parts[1].startswith("@"):
                        username_to_remove = parts[1][1:]  # إزالة @ من اسم المستخدم
                    else:
                        return "❌ الصيغة الصحيحة: ازالة_vip @اسم_المستخدم"

                result = self.bot.user_manager.remove_vip(username_to_remove)
                print(f"🔧 تم تنفيذ أمر إزالة VIP: {username_to_remove} بواسطة {user.username}")

                # إضافة رسالة إضافية للتأكيد
                if result.startswith("✅"):
                    confirmation_msg = f"📝 تم إزالة {username_to_remove} من قائمة VIP"
                    try:
                        await self.bot.highrise.chat(confirmation_msg)
                    except:
                        pass

                return result

            elif message == "ريأكشن":
                return await self.send_reaction_menu()

            elif message == "غمزة" or message == "wink":
                return await self.send_wink_reaction()

            return None

        except Exception as e:
            print(f"خطأ في أوامر المشرفين: {e}")
            return f"❌ خطأ في تنفيذ الأمر: {str(e)}"

    # باقي الدوال تبقى كما هي...
    async def stop_user_emote(self, username: str):
        """إيقاف رقصة مستخدم معين"""
        try:
            target_user = None
            room_users = await self.bot.highrise.get_room_users()

            for user, _ in room_users:
                if user.username.lower() == username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{username}' غير موجود في الغرفة"

            if target_user.id in self.bot.auto_emotes:
                self.bot.auto_emotes[target_user.id]["task"].cancel()
                del self.bot.auto_emotes[target_user.id]
                return f"⏹️ تم إيقاف الرقص التلقائي للمستخدم {username}"
            else:
                await self.bot.highrise.send_emote("idle-loop-sitfloor", target_user.id)
                return f"⏹️ تم إيقاف رقصة المستخدم {username}"

        except Exception as e:
            return f"❌ فشل في إيقاف رقصة {username}: {str(e)}"

    async def kick_user(self, target_username: str) -> str:
        """طرد مستخدم من الغرفة"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user_id = None

            for room_user, _ in room_users:
                if room_user.username.lower() == target_username.lower():
                    target_user_id = room_user.id
                    break

            if not target_user_id:
                return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

            if target_user_id == self.bot.user_manager.bot_id:
                return "❌ لا يمكن طرد البوت نفسه!"

            if self.bot.user_manager.is_owner(target_username):
                return f"❌ لا يمكن طرد صاحب البوت!"

            await self.bot.highrise.moderate_room(target_user_id, "kick")
            await self.bot.highrise.chat(f"👟 تم طرد {target_username} من الغرفة!")
            print(f"✅ تم طرد {target_username} من الغرفة")
            return f"✅ تم طرد {target_username} بنجاح"

        except Exception as e:
            print(f"❌ خطأ في طرد {target_username}: {e}")
            return f"❌ فشل في طرد {target_username}: {str(e)}"

    async def pull_users_around_moderator(self, moderator_user: User) -> str:
        """سحب المستخدمين حول المشرف في شكل مربع"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content

            moderator_position = None
            for user, position in room_users:
                if user.id == moderator_user.id:
                    moderator_position = position
                    break

            if not moderator_position or not isinstance(moderator_position, Position):
                return "❌ لم أتمكن من العثور على مكانك"

            positions_around = [
                Position(moderator_position.x - 3, moderator_position.y, moderator_position.z - 3),
                Position(moderator_position.x, moderator_position.y, moderator_position.z - 3),
                Position(moderator_position.x + 3, moderator_position.y, moderator_position.z - 3),
                Position(moderator_position.x - 3, moderator_position.y, moderator_position.y, moderator_position.z),
                Position(moderator_position.x + 3, moderator_position.y, moderator_position.z),
                Position(moderator_position.x - 3, moderator_position.y, moderator_position.z + 3),
                Position(moderator_position.x, moderator_position.y, moderator_position.z + 3),
                Position(moderator_position.x + 3, moderator_position.y, moderator_position.z + 3),
            ]

            moved_count = 0
            position_index = 0

            for user, _ in room_users:
                if (user.id != moderator_user.id and 
                    user.username != self.bot.highrise.my_user.username and 
                    position_index < len(positions_around)):

                    try:
                        await self.bot.highrise.teleport(user.id, positions_around[position_index])
                        moved_count += 1
                        position_index += 1
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"خطأ في نقل {user.username}: {e}")
                        continue

            return f"✅ تم سحب {moved_count} مستخدم حولك في شكل مربع"

        except Exception as e:
            print(f"خطأ في أمر اسحبهم: {e}")
            return f"❌ خطأ في تنفيذ الأمر: {str(e)}"

    async def bring_user_to_moderator(self, moderator_user: User, target_username: str) -> str:
        """إحضار مستخدم محدد إلى نفس مكان المشرف بالضبط"""
        try:
            # أولاً نجرب الحصول على المواقع من نظام التتبع
            moderator_location = self.bot.location_tracker.get_user_location(moderator_user.id)
            target_location = self.bot.location_tracker.get_user_location_by_username(target_username)

            # إذا لم نجد في نظام التتبع، نحصل من الغرفة مباشرة
            room_users = (await self.bot.highrise.get_room_users()).content
            moderator_position = None
            target_user = None

            for user, position in room_users:
                if user.id == moderator_user.id:
                    moderator_position = position
                    # تحديث نظام التتبع
                    self.bot.location_tracker.update_user_location(user, position)
                elif user.username.lower() == target_username.lower():
                    target_user = user
                    # تحديث نظام التتبع
                    self.bot.location_tracker.update_user_location(user, position)

            if not moderator_position:
                return "❌ لم أتمكن من العثور على مكانك"

            if not target_user:
                # تحقق من وجود المستخدم في نظام التتبع
                if target_location:
                    return f"❌ المستخدم '{target_username}' ليس في الغرفة حالياً (آخر موقع معروف: {target_location['last_update'][:16]})"
                return f"❌ المستخدم '{target_username}' غير موجود في الروم"

            if not isinstance(moderator_position, Position):
                return "❌ مكانك غير صالح للنقل"

            # إحضار المستخدم إلى نفس إحداثيات المشرف تماماً
            exact_position = Position(
                moderator_position.x,
                moderator_position.y,
                moderator_position.z
            )

            await self.bot.highrise.teleport(target_user.id, exact_position)

            # تحديث موقع المستخدم في نظام التتبع
            self.bot.location_tracker.update_user_location(target_user, exact_position)

            return f"✅ تم إحضار {target_username} إلى نفس إحداثياتك تماماً"

        except Exception as e:
            print(f"خطأ في أمر جيب: {e}")
            return f"❌ خطأ في إحضار المستخدم: {str(e)}"

    async def swap_users_positions(self, username1: str, username2: str) -> str:
        """تبديل أماكن مستخدمين"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content

            user1_data = None
            user2_data = None

            for user, position in room_users:
                if user.username.lower() == username1.lower():
                    user1_data = (user, position)
                elif user.username.lower() == username2.lower():
                    user2_data = (user, position)

            if not user1_data:
                return f"❌ المستخدم '{username1}' غير موجود في الروم"

            if not user2_data:
                return f"❌ المستخدم '{username2}' غير موجود في الروم"

            user1, position1 = user1_data
            user2, position2 = user2_data

            if not isinstance(position1, Position) or not isinstance(position2, Position):
                return "❌ أحد المواقع غير صالح للتبديل"

            await self.bot.highrise.teleport(user1.id, position2)
            await asyncio.sleep(0.3)
            await self.bot.highrise.teleport(user2.id, position1)

            return f"✅ تم تبديل أماكن {username1} و {username2}"

        except Exception as e:
            print(f"خطأ في أمر بدل: {e}")
            return f"❌ خطأ في تبديل الأماكن: {str(e)}"

    async def change_bot_outfit(self) -> str:
        """تغيير ملابس البوت عشوائياً"""
        try:
            import random
            from highrise.models import Item

            shirt = ["shirt-n_starteritems2019tankwhite", "shirt-n_starteritems2019tankblack", "shirt-n_starteritems2019raglanwhite"]
            pant = ["pants-n_starteritems2019mensshortswhite", "pants-n_starteritems2019mensshortsblue", "pants-n_starteritems2019mensshortsblack"]

            item_top = random.choice(shirt)
            item_bottom = random.choice(pant)

            result = await self.bot.highrise.set_outfit(outfit=[
                Item(type='clothing', amount=1, id='body-flesh', account_bound=False, active_palette=65),
                Item(type='clothing', amount=1, id=item_top, account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=item_bottom, account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id='nose-n_01', account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id='shoes-n_room12019sneakersblack', account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id='mouth-basic2018downturnedthinround', account_bound=False, active_palette=0),
                Item(type='clothing', amount=1, id='hair_front-n_malenew07', account_bound=False, active_palette=1),
                Item(type='clothing', amount=1, id='hair_back-n_malenew07', account_bound=False, active_palette=1),
                Item(type='clothing', amount=1, id='eye-n_basic2018zanyeyes', account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id='eyebrow-n_basic2018newbrows09', account_bound=False, active_palette=-1)
            ])

            return f"👕 تم تغيير ملابس البوت عشوائياً!"

        except Exception as e:
            return f"❌ خطأ في تغيير الملابس: {str(e)}"

    async def freeze_user(self, target_username: str) -> str:
        """تثبيت مستخدم في مكانه"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            target_position = None

            for user, position in room_users:
                if user.username.lower() == target_username.lower():
                    target_user = user
                    target_position = position
                    break

            if not target_user:
                return f"❌ المستخدم '{target_username}' غير موجود في الروم"

            if not isinstance(target_position, Position):
                return f"❌ موقع المستخدم '{target_username}' غير صالح للتثبيت"

            self.bot.frozen_users[target_user.id] = {
                "position": target_position,
                "username": target_user.username
            }

            await self.bot.highrise.chat(f"🔒 تم تثبيت {target_username} في مكانه!")
            return f"✅ تم تثبيت {target_username} بنجاح"

        except Exception as e:
            print(f"خطأ في تثبيت المستخدم: {e}")
            return f"❌ خطأ في تثبيت المستخدم: {str(e)}"

    async def unfreeze_user(self, target_username: str) -> str:
        """إلغاء تثبيت مستخدم"""
        try:
            clean_username = target_username.replace("@", "").strip()

            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None

            for user, _ in room_users:
                if user.username.lower() == clean_username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{clean_username}' غير موجود في الروم"

            if target_user.id not in self.bot.frozen_users:
                return f"❌ المستخدم '{clean_username}' غير مثبت أصلاً"

            del self.bot.frozen_users[target_user.id]
            await self.bot.highrise.chat(f"🔓 تم إلغاء تثبيت {clean_username}!")
            return f"✅ تم إلغاء تثبيت {clean_username} بنجاح"

        except Exception as e:
            print(f"خطأ في إلغاء تثبيت المستخدم: {e}")
            return f"❌ خطأ في إلغاء تثبيت المستخدم: {str(e)}"

    async def jail_user(self, target_username: str) -> str:
        """سجن مستخدم في إحداثيات سالبة"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None

            for user, _ in room_users:
                if user.username.lower() == target_username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{target_username}' غير موجود في الروم"

            jail_position = Position(x=-50.0, y=0.0, z=-50.0)

            await self.bot.highrise.teleport(target_user.id, jail_position)
            await self.bot.highrise.chat(f"⛓️ تم سجن {target_username} في المنطقة المحظورة!")

            return f"✅ تم سجن {target_username} بنجاح"

        except Exception as e:
            print(f"خطأ في سجن المستخدم: {e}")
            return f"❌ خطأ في سجن المستخدم: {str(e)}"

    # إضافة أوامر الريأكشن للجميع

    async def send_reaction_to_all(self, reaction_type: str) -> str:
        """إرسال ريأكشن لجميع المستخدمين في الغرفة"""
        try:
            room_users = await self.bot.highrise.get_room_users()
            users_list = room_users.content

            # قائمة الريأكشنز المدعومة
            supported_reactions = ["heart", "wave", "clap", "thumbs", "wink", "kiss", "confused", "laugh"]

            if reaction_type not in supported_reactions:
                return f"❌ ريأكشن غير مدعوم! الريأكشنز المتاحة: {', '.join(supported_reactions)}"

            reaction_names = {
                "heart": "قلوب",
                "wave": "تحية", 
                "clap": "تصفيق",
                "thumbs": "إعجاب",
                "wink": "غمزة",
                "kiss": "قبلة",
                "confused": "محتار",
                "laugh": "ضحك"
            }

            reaction_name = reaction_names.get(reaction_type, reaction_type)
            sent_count = 0
            failed_count = 0

            # معرف البوت المحدد
            BOT_ID = "657a06ae5f8a5ec3ff16ec1b"

            for user, _ in users_list:
                # تجنب إرسال ريأكشن للبوت نفسه
                if user.id != BOT_ID:
                    try:
                        # إرسال 5 ريأكشنز لكل مستخدم مع انتظار أطول
                        for _ in range(5):
                            await self.bot.highrise.react(reaction_type, user.id)
                            await asyncio.sleep(0.2)  # انتظار أطول بين كل ريأكشن
                        sent_count += 1
                        await asyncio.sleep(0.5)  # انتظار بين المستخدمين
                    except Exception as e:
                        print(f"فشل إرسال ريأكشن لـ {user.username}: {e}")
                        failed_count += 1
                        continue

            result = f"✅ تم إرسال {reaction_name} لـ {sent_count} مستخدم"
            if failed_count > 0:
                result += f" (فشل مع {failed_count} مستخدم)"

            return result

        except Exception as e:
            return f"❌ خطأ في إرسال الريأكشن للجميع: {str(e)}"

    def get_available_reactions(self) -> str:
        """عرض قائمة الريأكشنز المتاحة"""
        reactions_info = {
            "heart": "❤️ قلوب",
            "wave": "👋 تحية",
            "clap": "👏 تصفيق", 
            "thumbs": "👍 إعجاب",
            "wink": "😉 غمزة",
            "kiss": "😘 قبلة",
            "confused": "😕 محتار",
            "laugh": "😂 ضحك"
        }

        result = "🎭 قائمة الريأكشنز المتاحة:\n\n"
        result += "**الأوامر السريعة:**\n"
        for reaction, desc in reactions_info.items():
            result += f"• {desc} - `{list(reactions_info.keys())[list(reactions_info.values()).index(desc)].split()[1] if ' ' in desc else reaction}`\n"

        result += "\n**أو استخدم:**\n"
        result += "• `ريأكشن [نوع]` - مثل: ريأكشن heart\n"
        result += "• `قائمة_الريأكشنز` - لعرض هذه القائمة\n"

        return result

    def get_frozen_users_list(self) -> str:
        """الحصول على قائمة المستخدمين المثبتين"""
        if not self.bot.frozen_users:
            return "🔒 لا يوجد مستخدمين مثبتين حالياً"

        frozen_list = []
        for user_id, data in self.bot.frozen_users.items():
            username = data["username"]
            frozen_list.append(username)

        users_text = " | ".join(frozen_list[:10])
        count = len(self.bot.frozen_users)

        return f"🔒 المستخدمين المثبتين ({count}): {users_text}"

    async def teleport_user_to_target(self, requesting_user, target_username: str) -> str:
        """نقل المستخدم الذي طلب الأمر إلى مكان الشخص المحدد"""
        try:
            clean_username = target_username.replace("@", "").strip()

            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            target_position = None

            for user, position in room_users:
                if user.username.lower() == clean_username.lower():
                    target_user = user
                    target_position = position
                    break

            if not target_user:
                return f"❌ المستخدم '{clean_username}' غير موجود في الروم"

            if not target_position:
                return f"❌ لا يمكن تحديد موقع '{clean_username}'"

            if not isinstance(target_position, Position):
                return f"❌ موقع '{clean_username}' غير صالح للنقل"

            new_position = Position(
                target_position.x + 1,
                target_position.y,
                target_position.z
            )

            await self.bot.highrise.teleport(requesting_user.id, new_position)
            return f"🚶‍♂️ تم نقلك إلى {clean_username} بنجاح"

        except Exception as e:
            print(f"خطأ في أمر وديني: {e}")
            return f"❌ خطأ في النقل: {str(e)}"

    async def bring_user_to_user(self, requesting_user, target_username: str) -> str:
        """جلب المستخدم المحدد إلى نفس مكان الطالب تماماً"""
        try:
            clean_username = target_username.replace("@", "").strip()

            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            requesting_user_position = None

            for user, position in room_users:
                if user.id == requesting_user.id:
                    requesting_user_position = position
                elif user.username.lower() == clean_username.lower():
                    target_user = user

            if not target_user:
                return f"❌ المستخدم '{clean_username}' غير موجود في الروم"

            if not requesting_user_position:
                return "❌ لا يمكن تحديد موقعك الحالي"

            if not isinstance(requesting_user_position, Position):
                return "❌ موقعك غير صالح للنقل"

            # نقل المستخدم المحدد إلى نفس الإحداثيات تماماً
            exact_position = Position(
                requesting_user_position.x,
                requesting_user_position.y,
                requesting_user_position.z
            )

            await self.bot.highrise.teleport(target_user.id, exact_position)
            return f"✅ تم جلب {clean_username} إلى نفس إحداثياتك تماماً"

        except Exception as e:
            print(f"خطأ في أمر جيب: {e}")
            return f"❌ خطأ في جلب المستخدم: {str(e)}"

    async def swap_with_user(self, requesting_user, target_username: str) -> str:
        """تبديل مكان الطالب مع المستخدم المحدد"""
        try:
            clean_username = target_username.replace("@", "").strip()

            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            requesting_user_position = None
            target_position = None

            for user, position in room_users:
                if user.id == requesting_user.id:
                    requesting_user_position = position
                elif user.username.lower() == clean_username.lower():
                    target_user = user
                    target_position = position

            if not target_user:
                return f"❌ المستخدم '{clean_username}' غير موجود في الروم"

            if not requesting_user_position or not target_position:
                return "❌ لا يمكن تحديد المواقع"

            if not isinstance(requesting_user_position, Position) or not isinstance(target_position, Position):
                return "❌ أحد المواقع غير صالح للتبديل"

            await self.bot.highrise.teleport(requesting_user.id, target_position)
            await asyncio.sleep(0.3)
            await self.bot.highrise.teleport(target_user.id, requesting_user_position)

            return f"🔄 تم تبديل مكانك مع {clean_username}"

        except Exception as e:
            print(f"خطأ في أمر اعكس: {e}")
            return f"❌ خطأ في تبديل المكان: {str(e)}"

    async def bring_user_to_requester(self, requester, target_username: str):
        """إحضار مستخدم إلى نفس موقع الشخص الذي طلب الأمر"""
        try:
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            requester_position = None

            # البحث عن المستخدم المطلوب والشخص الطالب
            for user, position in room_users:
                if user.username.lower() == target_username.lower():
                    target_user = user
                elif user.id == requester.id:
                    requester_position = position

            if not target_user:
                return f"❌ المستخدم '{target_username}' مش موجود في الروم"

            if not requester_position:
                return f"❌ ما قدرتش أحدد مكانك يا {requester.username}"

            # نقل المستخدم المطلوب لنفس موقع الطالب بالضبط
            await self.bot.highrise.teleport(target_user.id, requester_position)
            return f"✅ تم جلب {target_username} لموقعك بالضبط يا {requester.username}!"

        except Exception as e:
            print(f"خطأ في جلب المستخدم: {e}")
            return f"❌ خطأ في جلب المستخدم: {str(e)}"

    async def stop_user_emote(self, target_username: str) -> str:
        """إيقاف رقصة مستخدم معين"""
        try:
            clean_username = target_username.replace("@", "").strip()

            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None

            for user, _ in room_users:
                if user.username.lower() == clean_username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{clean_username}' غير موجود في الروم"

            if target_user.id not in self.bot.auto_emotes:
                await self.bot.highrise.send_emote("idle-loop-sitfloor", target_user.id)
                return f"⏹️ تم إيقاف رقصة المستخدم {clean_username}"
            else:
                self.bot.auto_emotes[target_user.id]["task"].cancel()
                del self.bot.auto_emotes[target_user.id]
                return f"⏹️ تم إيقاف الرقص التلقائي للمستخدم {clean_username}"

        except Exception as e:
            return f"❌ فشل في إيقاف رقصة {target_username}: {str(e)}"

    async def stop_user_emote(self, username: str):
        """إيقاف رقصة مستخدم معين"""
        try:
            target_user = None
            room_users = await self.bot.highrise.get_room_users()

            for user, _ in room_users:
                if user.username.lower() == username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{username}' غير موجود في الغرفة"

            if target_user.id in self.bot.auto_emotes:
                self.bot.auto_emotes[target_user.id]["task"].cancel()
                del self.bot.auto_emotes[target_user.id]
                return f"⏹️ تم إيقاف الرقص التلقائي للمستخدم {username}"
            else:
                await self.bot.highrise.send_emote("idle-loop-sitfloor", target_user.id)
                return f"⏹️ تم إيقاف رقصة المستخدم {username}"

        except Exception as e:
            return f"❌ فشل في إيقاف رقصة {username}: {str(e)}"

    async def start_following_user(self, target_username: str) -> str:
        """بدء ملاحقة مستخدم معين"""
        try:
            # البحث عن المستخدم في الغرفة
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None

            for user, _ in room_users:
                if user.username.lower() == target_username.lower():
                    target_user = user
                    break

            if not target_user:
                return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

            # إيقاف أي ملاحقة سابقة
            if hasattr(self.bot, 'following_tasks'):
                for task in self.bot.following_tasks.values():
                    task.cancel()
                self.bot.following_tasks.clear()
            else:
                self.bot.following_tasks = {}

            # بدء ملاحقة المستخدم الجديد
            follow_task = asyncio.create_task(self.follow_user_continuously(target_user))
            self.bot.following_tasks[target_user.id] = {
                "task": follow_task,
                "username": target_username,
                "target_id": target_user.id
            }

            await self.bot.highrise.chat(f"👁️ البوت بدأ ملاحقة @{target_username} - لن يفلت منه!")
            return f"✅ تم بدء ملاحقة {target_username} بنجاح! البوت سيتابعه أينما ذهب"

        except Exception as e:
            return f"❌ فشل في بدء الملاحقة: {str(e)}"

    async def follow_user_continuously(self, target_user):
        """ملاحقة المستخدم بالمشي التدريجي فقط - بدون انتقال نهائياً"""
        try:
            last_position = None
            follow_delay = 1.0  # تأخير للمشي الطبيعي
            close_distance = 2.0  # المسافة القريبة (لا نتحرك)
            max_walk_distance = 50.0  # أقصى مسافة للمشي
            consecutive_walk_failures = 0

            print(f"🚶‍♂️ بدء متابعة {target_user.username} بالمشي الطبيعي فقط - بدون انتقال")

            while target_user.id in getattr(self.bot, 'following_tasks', {}):
                try:
                    # الحصول على موقع المستخدم والبوت
                    room_users = (await self.bot.highrise.get_room_users()).content
                    target_position = None
                    bot_position = None

                    BOT_ID = "657a06ae5f8a5ec3ff16ec1b"

                    for user, position in room_users:
                        if user.id == target_user.id:
                            target_position = position
                        elif user.id == BOT_ID:
                            bot_position = position

                    if target_position and bot_position and target_position != last_position:
                        from highrise import Position
                        import math

                        # حساب المسافة بين البوت والمستخدم
                        distance = math.sqrt(
                            (target_position.x - bot_position.x) ** 2 + 
                            (target_position.z - bot_position.z) ** 2
                        )

                        print(f"🔍 المسافة إلى {target_user.username}: {distance:.2f} وحدة")

                        # إذا كان المستخدم قريب جداً، لا نتحرك
                        if distance <= close_distance:
                            print(f"📍 البوت قريب بما فيه الكفاية من {target_user.username}")
                            last_position = target_position
                            consecutive_walk_failures = 0
                            await asyncio.sleep(follow_delay)
                            continue

                        # إذا كان المستخدم بعيد جداً، نمشي بأقصى خطوة ممكنة
                        if distance > max_walk_distance:
                            print(f"🚶‍♂️ المستخدم بعيد جداً ({distance:.2f} وحدة)، سأمشي بأقصى خطوة")
                            # نمشي بأقصى خطوة في اتجاه المستخدم
                            dx = target_position.x - bot_position.x
                            dz = target_position.z - bot_position.z

                            # تطبيع المتجه
                            if distance > 0:
                                dx = dx / distance
                                dz = dz / distance

                            # أقصى خطوة ممكنة
                            max_step = 8.0
                            walk_position = Position(
                                x=bot_position.x + (dx * max_step),
                                y=target_position.y,
                                z=bot_position.z + (dz * max_step)
                            )

                            try:
                                await self.bot.highrise.walk_to(walk_position)
                                print(f"🚶‍♂️ مشيت خطوة كبيرة ({max_step} وحدة) نحو {target_user.username}")
                                consecutive_walk_failures = 0
                            except Exception as walk_error:
                                consecutive_walk_failures += 1
                                print(f"⚠️ فشل المشي الكبير: {walk_error}")
                                if consecutive_walk_failures >= 5:
                                    print(f"😴 توقف لمدة 10 ثوان بسبب فشل المشي المتكرر")
                                    await asyncio.sleep(10)
                                    consecutive_walk_failures = 0
                                else:
                                    await asyncio.sleep(2)
                        else:
                            # المشي العادي - حساب خطوة مناسبة
                            print(f"🚶‍♂️ المشي العادي نحو {target_user.username}")

                            # حساب حجم الخطوة حسب المسافة
                            if distance > 15:
                                step_size = min(4.0, distance * 0.3)
                            elif distance > 8:
                                step_size = min(3.0, distance * 0.4)
                            elif distance > 4:
                                step_size = min(2.0, distance * 0.5)
                            else:
                                step_size = min(1.5, distance * 0.7)

                            # حساب الاتجاه
                            dx = target_position.x - bot_position.x
                            dz = target_position.z - bot_position.z

                            # تطبيع المتجه
                            if distance > 0:
                                dx = dx / distance
                                dz = dz / distance

                            # حساب موقع الخطوة التالية
                            walk_position = Position(
                                x=bot_position.x + (dx * step_size),
                                y=target_position.y,
                                z=bot_position.z + (dz * step_size)
                            )

                            try:
                                # المشي فقط - لا انتقال أبداً
                                await self.bot.highrise.walk_to(walk_position)
                                print(f"🚶‍♂️ مشيت ({step_size:.1f} وحدة) من ({bot_position.x:.1f}, {bot_position.z:.1f}) إلى ({walk_position.x:.1f}, {walk_position.z:.1f})")
                                consecutive_walk_failures = 0

                            except Exception as walk_error:
                                consecutive_walk_failures += 1
                                print(f"⚠️ فشل المشي (فشل متتالي رقم {consecutive_walk_failures}): {walk_error}")

                                # إذا فشل المشي عدة مرات، نتوقف مؤقتاً
                                if consecutive_walk_failures >= 3:
                                    print(f"😴 توقف مؤقت لمدة 5 ثوان بسبب فشل المشي المتكرر")
                                    await asyncio.sleep(5)
                                    consecutive_walk_failures = 0
                                else:
                                    await asyncio.sleep(1)

                        last_position = target_position

                    # انتظار قبل الفحص التالي
                    await asyncio.sleep(follow_delay)

                except Exception as e:
                    print(f"خطأ في ملاحقة {target_user.username}: {e}")
                    await asyncio.sleep(2)

        except asyncio.CancelledError:
            print(f"تم إيقاف ملاحقة {target_user.username}")
        except Exception as e:
            print(f"خطأ في مهمة الملاحقة: {e}")

    async def stop_following_all(self) -> str:
        """إيقاف جميع عمليات الملاحقة"""
        try:
            if not hasattr(self.bot, 'following_tasks') or not self.bot.following_tasks:
                return "❌ لا توجد عمليات ملاحقة نشطة"

            stopped_count = 0
            stopped_users = []

            for user_id, follow_data in self.bot.following_tasks.items():
                follow_data["task"].cancel()
                stopped_users.append(follow_data["username"])
                stopped_count += 1

            self.bot.following_tasks.clear()

            users_text = " | ".join(stopped_users)
            await self.bot.highrise.chat(f"🛑 تم إيقاف جميع عمليات الملاحقة!")

            return f"✅ تم إيقاف ملاحقة {stopped_count} مستخدم: {users_text}"

        except Exception as e:
            return f"❌ فشل في إيقاف الملاحقة: {str(e)}"

    def get_following_list(self) -> str:
        """عرض قائمة المستخدمين المتابعين حالياً"""
        try:
            if not hasattr(self.bot, 'following_tasks') or not self.bot.following_tasks:
                return "👁️ لا يوجد مستخدمين يتم تتبعهم حالياً"

            following_users = []
            for user_id, follow_data in self.bot.following_tasks.items():
                following_users.append(follow_data["username"])

            users_text = " | ".join(following_users)
            count = len(self.bot.following_tasks)

            return f"👁️ المستخدمين المتابعين حالياً ({count}): {users_text}\n💡 استخدم 'ايقاف_الملاحقة' لإيقاف جميع عمليات التتبع"

        except Exception as e:
            return f"❌ خطأ في عرض قائمة المتابعين: {str(e)}"

    async def start_punishment(self, target_username: str) -> str:
        """بدء العقاب العشوائي للمستخدم"""
        try:
            # البحث عن المستخدم في الغرفة
            room_users = (await self.bot.highrise.get_room_users()).content
            target_user = None
            original_position = None

            for user, position in room_users:
                if user.username.lower() == target_username.lower():
                    target_user = user
                    original_position = position
                    break

            if not target_user:
                return f"❌ المستخدم '{target_username}' غير موجود في الغرفة"

            # تهيئة قاموس العقاب إذا لم يكن موجود
            if not hasattr(self.bot, 'punishment_tasks'):
                self.bot.punishment_tasks = {}

            # إيقاف أي عقاب سابق لنفس المستخدم
            if target_user.id in self.bot.punishment_tasks:
                self.bot.punishment_tasks[target_user.id]["task"].cancel()

            # بدء العقاب مع حفظ الموقع الأصلي
            punishment_task = asyncio.create_task(self.punish_user_continuously(target_user, original_position))
            self.bot.punishment_tasks[target_user.id] = {
                "task": punishment_task,
                "username": target_username,
                "target_id": target_user.id,
                "original_position": original_position
            }

            await self.bot.highrise.chat(f"⚡ بدء العقاب العشوائي لـ @{target_username} - سيتم نقله بسرعة وعشوائية!")
            return f"✅ تم بدء عقاب {target_username} بنجاح! سيتم نقله عشوائياً بسرعة عالية وإرجاعه لمكانه الأصلي بعد الانتهاء"

        except Exception as e:
            return f"❌ فشل في بدء العقاب: {str(e)}"

    async def punish_user_continuously(self, target_user, original_position=None):
        """تطبيق العقاب المستمر على المستخدم"""
        try:
            import random
            from highrise import Position

            print(f"⚡ بدء العقاب العشوائي لـ {target_user.username}")

            punishment_count = 0
            max_punishments = 50  # عدد مرات النقل العشوائي

            while (target_user.id in getattr(self.bot, 'punishment_tasks', {}) and 
                   punishment_count < max_punishments):
                try:
                    # إنشاء إحداثيات عشوائية في نطاقات مختلفة
                    x_ranges = [
                        (-20, -10), (10, 20), (-30, -20), (20, 30),
                        (-40, -30), (30, 40), (-15, 15), (-50, 50)
                    ]
                    z_ranges = [
                        (-20, -10), (10, 20), (-30, -20), (20, 30),
                        (-40, -30), (30, 40), (-15, 15), (-50, 50)
                    ]
                    y_values = [0, 0.5, 1.0, 1.5, 2.0]

                    # اختيار نطاق عشوائي
                    x_range = random.choice(x_ranges)
                    z_range = random.choice(z_ranges)

                    # إنشاء موقع عشوائي
                    random_position = Position(
                        x=random.uniform(x_range[0], x_range[1]),
                        y=random.choice(y_values),
                        z=random.uniform(z_range[0], z_range[1])
                    )

                    # نقل المستخدم
                    await self.bot.highrise.teleport(target_user.id, random_position)

                    punishment_count += 1
                    print(f"⚡ العقاب {punishment_count}: نقل {target_user.username} إلى ({random_position.x:.1f}, {random_position.y:.1f}, {random_position.z:.1f})")

                    # انتظار قصير جداً للسرعة العالية
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                    # في منتصف العقاب، أرسل رسالة تحذيرية
                    if punishment_count == 25:
                        await self.bot.highrise.chat(f"⚡ {target_user.username} يتم تأديبه! العقاب في منتصفه...")

                except Exception as teleport_error:
                    print(f"⚠️ خطأ في نقل المستخدم أثناء العقاب: {teleport_error}")
                    await asyncio.sleep(0.5)
                    continue

            # انتهاء العقاب - إرجاع المستخدم لمكانه الأصلي
            try:
                if original_position:
                    await self.bot.highrise.teleport(target_user.id, original_position)
                    await self.bot.highrise.chat(f"🏠 تم إرجاع @{target_username} إلى مكانه الأصلي!")
                    print(f"🏠 تم إرجاع {target_user.username} إلى مكانه الأصلي")
                else:
                    print(f"⚠️ لا يوجد موقع أصلي محفوظ لـ {target_user.username}")
            except Exception as return_error:
                print(f"❌ خطأ في إرجاع المستخدم لمكانه الأصلي: {return_error}")

            # إزالة من قائمة العقاب
            if target_user.id in getattr(self.bot, 'punishment_tasks', {}):
                del self.bot.punishment_tasks[target_user.id]

            await self.bot.highrise.chat(f"✅ انتهى العقاب لـ @{target_username} - تم نقله {punishment_count} مرة!")
            print(f"✅ انتهى العقاب لـ {target_user.username} بعد {punishment_count} عملية نقل")

        except asyncio.CancelledError:
            print(f"⏹️ تم إلغاء العقاب لـ {target_user.username}")
            # محاولة إرجاع المستخدم لمكانه الأصلي حتى لو تم إلغاء العقاب
            try:
                if original_position:
                    await self.bot.highrise.teleport(target_user.id, original_position)
                    await self.bot.highrise.chat(f"🏠 تم إرجاع @{target_username} إلى مكانه الأصلي بعد إلغاء العقاب!")
            except:
                pass
            await self.bot.highrise.chat(f"⏹️ تم إلغاء العقاب لـ @{target_username}")
        except Exception as e:
            print(f"❌ خطأ في مهمة العقاب: {e}")

    async def stop_punishment(self, target_username: str) -> str:
        """إيقاف العقاب عن المستخدم وإرجاعه لمكانه الأصلي"""
        try:
            if not hasattr(self.bot, 'punishment_tasks') or not self.bot.punishment_tasks:
                return "❌ لا توجد عقوبات نشطة حالياً"

            # البحث عن المستخدم في العقوبات النشطة
            target_user_id = None
            punishment_data = None
            for user_id, data in self.bot.punishment_tasks.items():
                if data["username"].lower() == target_username.lower():
                    target_user_id = user_id
                    punishment_data = data
                    break

            if not target_user_id:
                return f"❌ المستخدم '{target_username}' ليس تحت العقاب حالياً"

            # إلغاء العقاب
            punishment_data["task"].cancel()

            # محاولة إرجاع المستخدم لمكانه الأصلي
            original_position = punishment_data.get("original_position")
            if original_position:
                try:
                    await self.bot.highrise.teleport(target_user_id, original_position)
                    await self.bot.highrise.chat(f"🏠 تم إرجاع @{target_username} إلى مكانه الأصلي!")
                except Exception as e:
                    print(f"❌ خطأ في إرجاع المستخدم لمكانه الأصلي: {e}")

            del self.bot.punishment_tasks[target_user_id]

            await self.bot.highrise.chat(f"🛑 تم إلغاء العقاب عن @{target_username}")
            return f"✅ تم إلغاء العقاب عن {target_username} بنجاح وإرجاعه لمكانه الأصلي"

        except Exception as e:
            return f"❌ فشل في إلغاء العقاب: {str(e)}"

    def get_punished_users_list(self) -> str:
        """عرض قائمة المستخدمين المعاقبين حالياً"""
        try:
            if not hasattr(self.bot, 'punishment_tasks') or not self.bot.punishment_tasks:
                return "⚡ لا يوجد مستخدمين تحت العقاب حالياً"

            punished_users = []
            for user_id, punishment_data in self.bot.punishment_tasks.items():
                punished_users.append(punishment_data["username"])

            users_text = " | ".join(punished_users)
            count = len(self.bot.punishment_tasks)

            return f"⚡ المستخدمين تحت العقاب حالياً ({count}): {users_text}\n💡 استخدم 'الغ_عقاب @اسم_المستخدم' لإلغاء العقاب"

        except Exception as e:
            return f"❌ خطأ في عرض قائمة المعاقبين: {str(e)}"

    async def check_user_permissions(self, username: str):
        """فحص صلاحيات مستخدم"""
        try:
            return self.bot.user_manager.get_user_permissions_info(username)
        except Exception as e:
            return f"❌ خطأ في فحص صلاحيات {username}: {str(e)}"

    async def check_bot_wallet_detailed(self):
        """فحص مفصل لمحفظة البوت للمشرفين"""
        try:
            # الحصول على محفظة البوت
            wallet = await self.bot.highrise.get_wallet()

            if wallet and hasattr(wallet, 'content'):
                wallet_info = "💰 محفظة البوت المفصلة:\n"
                wallet_info += "=" * 30 + "\n"

                total_items = len(wallet.content)
                gold_amount = 0
                other_items = []

                # فحص جميع العناصر في المحفظة
                for i, item in enumerate(wallet.content, 1):
                    if hasattr(item, 'type') and item.type == "gold":
                        gold_amount = item.amount
                        wallet_info += f"💰 الجولد: {item.amount:,} قطعة\n"
                    elif hasattr(item, 'id') and 'gold' in item.id.lower():
                        gold_amount = item.amount
                        wallet_info += f"💰 الجولد: {item.amount:,} قطعة\n"
                    else:
                        # عناصر أخرى في المحفظة
                        item_name = getattr(item, 'id', f'عنصر_{i}')
                        item_amount = getattr(item, 'amount', 1)
                        other_items.append(f"📦 {item_name}: {item_amount}")

                if other_items:
                    wallet_info += "\n🎁 عناصر أخرى:\n"
                    for item in other_items[:10]:  # عرض أول 10 عناصر
                        wallet_info += f"  • {item}\n"
                    if len(other_items) > 10:
                        wallet_info += f"  ... و {len(other_items) - 10} عنصر آخر\n"

                wallet_info += f"\n📊 إجمالي العناصر: {total_items}"
                wallet_info += f"\n💎 الجولد الرئيسي: {gold_amount:,}"

                return wallet_info
            else:
                return "❌ لا يمكن الوصول لمحفظة البوت أو المحفظة فارغة"

        except Exception as e:
            print(f"خطأ في فحص محفظة البوت المفصل: {e}")
            return f"❌ فشل في فحص المحفظة: {str(e)}"

    def get_vip_list(self) -> str:
        """الحصول على قائمة VIP"""
        try:
            vips = self.bot.user_manager.get_vip_list()
            if not vips:
                return "⭐ لا يوجد VIP مسجلين حالياً"

            vip_list = []
            for vip in vips:
                vip_list.append(vip)

            users_text = " | ".join(vip_list[:10])
            count = len(self.bot.user_manager.vips)

            return f"⭐ قائمة VIP ({count}): {users_text}\n💡 استخدم 'اضافة_vip @اسم_المستخدم' لإضافة VIP"

        except Exception as e:
            return f"❌ خطأ في عرض قائمة VIP: {str(e)}"

    async def add_vip(self, username: str) -> str:
        """إضافة VIP"""
        try:
            result = self.bot.user_manager.add_vip(username)
            if result.startswith("✅"):
                await self.bot.highrise.chat(f"🎉 {username} أصبح الآن VIP!")
            return result
        except Exception as e:
            return f"❌ فشل في إضافة VIP: {str(e)}"

    async def remove_vip(self, username: str) -> str:
        """إزالة VIP"""
        try:
            result = self.bot.user_manager.remove_vip(username)
            if result.startswith("✅"):
                await self.bot.highrise.chat(f"📝 {username} لم يعد VIP")
            return result
        except Exception as e:
            return f"❌ فشل في إزالة VIP: {str(e)}"

    def get_moderators_list(self) -> str:
        """الحصول على قائمة المشرفين"""
        mods_list = self.bot.user_manager.get_moderators_list()
        if mods_list:
            owners = [m for m in mods_list if self.bot.user_manager.is_owner(m)]
            others = [m for m in mods_list if not self.bot.user_manager.is_owner(m)]

            result = f"👮‍♂️ قائمة المشرفين ({len(mods_list)}):\n"

            if owners:
                result += f"👑 المالكين: {' | '.join(owners)}\n"

            if others:
                result += f"🛡️ المشرفين: {' | '.join(others[:15])}"
                if len(others) > 15:
                    result += f" + {len(others) - 15} آخرين"

            return result
        else:
            return "❌ لا يوجد مشرفين مسجلين"

    async def move_bot_to_room(self, room_id: str) -> str:
        """نقل البوت إلى غرفة أخرى مع التحقق من الصلاحيات"""
        try:
            print(f"🔄 بدء عملية النقل إلى الغرفة: {room_id}")

            # محاولة الانتقال إلى الغرفة الجديدة
            result = await self.bot.highrise.move_to_room(room_id)

            if result:
                print(f"✅ تم نقل البوت بنجاح إلى الغرفة: {room_id}")

                # انتظار قصير للتأكد من الاتصال
                await asyncio.sleep(2)

                # فحص الصلاحيات في الغرفة الجديدة
                try:
                    bot_privileges = await self.bot.highrise.get_room_privilege(self.bot.user_manager.bot_id)

                    if hasattr(bot_privileges, 'moderator') and hasattr(bot_privileges, 'designer'):
                        is_moderator = bot_privileges.moderator
                        is_designer = bot_privileges.designer

                        status_msg = f"✅ تم النقل بنجاح إلى الغرفة {room_id}\n"
                        status_msg += f"👮‍♂️ صلاحيات المشرف: {'✅ نعم' if is_moderator else '❌ لا'}\n"
                        status_msg += f"🎨 صلاحيات المصمم: {'✅ نعم' if is_designer else '❌ لا'}"

                        if is_moderator and is_designer:
                            status_msg += "\n🎉 البوت جاهز للعمل بكامل الصلاحيات!"
                        elif is_moderator:
                            status_msg += "\n⚠️ البوت يحتاج صلاحيات المصمم للعمل الكامل"
                        else:
                            status_msg += "\n❌ البوت يحتاج صلاحيات المشرف والمصمم"

                        # إرسال رسالة في الغرفة الجديدة
                        try:
                            await self.bot.highrise.chat(f"🤖 تم نقل البوت بنجاح! مرحباً بكم في خدمات البوت المتقدمة")
                        except:
                            pass

                        return status_msg
                    else:
                        return f"✅ تم النقل للغرفة {room_id} لكن لا يمكن فحص الصلاحيات"

                except Exception as e:
                    print(f"⚠️ خطأ في فحص الصلاحيات: {e}")
                    return f"✅ تم النقل للغرفة {room_id} لكن فشل فحص الصلاحيات: {str(e)}"
            else:
                return f"❌ فشل في النقل إلى الغرفة {room_id}"

        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ خطأ في النقل: {e}")

            if "room not found" in error_msg or "invalid room" in error_msg:
                return f"❌ الغرفة {room_id} غير موجودة أو غير صحيحة"
            elif "permission" in error_msg or "access" in error_msg:
                return f"❌ البوت لا يملك صلاحيات الدخول للغرفة {room_id}"
            elif "banned" in error_msg:
                return f"❌ البوت محظور من الغرفة {room_id}"
            else:
                return f"❌ خطأ في النقل: {str(e)}"

    async def send_reaction_menu(self):
        """إرسال قائمة الرياكشنات المتاحة"""
        try:
            menu = "🎭 الرياكشنات المتاحة:\n"
            menu += "═" * 25 + "\n"
            menu += "😂 laugh - ضحك\n"
            menu += "😍 heart_eyes - عيون قلوب\n" 
            menu += "👏 clap - تصفيق\n"
            menu += "❤️ heart - قلب\n"
            menu += "😮 surprised - مفاجأة\n"
            menu += "😢 sad - حزن\n"
            menu += "😡 angry - غضب\n"
            menu += "🤔 thinking - تفكير\n"
            menu += "👍 thumbs_up - إعجاب\n"
            menu += "👎 thumbs_down - عدم إعجاب\n"
            menu += "🔥 fire - نار\n"
            menu += "⭐ star - نجمة\n"
            menu += "💯 hundred - مئة\n"
            menu += "🎉 party - حفلة\n"
            menu += "😴 sleepy - نعسان\n"
            menu += "😉 wink - غمزة\n"
            menu += "\n💡 اكتب الرمز أو الاسم الإنجليزي"

            return menu

        except Exception as e:
            return f"❌ خطأ في عرض قائمة الرياكشنات: {str(e)}"

    async def send_wink_reaction(self):
        """إرسال ريأكشن غمزة مباشر"""
        try:
            await self.bot.highrise.react("wink")
            return "😉 تم إرسال غمزة!"
        except Exception as e:
            return f"❌ فشل في إرسال الغمزة: {str(e)}"