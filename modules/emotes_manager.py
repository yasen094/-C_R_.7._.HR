"""
مدير الرقصات - نظام إدارة الرقصات والحركات مع الأرقام
"""
import json
import os

class EmotesManager:
    def __init__(self):
        self.emotes_data_file = "data/emotes_data.json"
        # ترتيب الرقصات: emote أولاً، ثم dance، ثم idle، ثم الباقي
        self.emotes_list = [
            # رقصات تبدأ بـ emote (81 رقصة)
            "emote-superpose", "emote-frog", "emote-swordfight", "emote-energyball", 
            "emote-cute", "emote-float", "emote-teleporting", "emote-telekinesis", 
            "emote-maniac", "emote-embarrassed", "emote-frustrated", "emote-slap", 
            "emote-snake", "emote-confused", "emote-roll", "emote-rofl", 
            "emote-superpunch", "emote-superrun", "emote-kicking", "emote-monster_fail", 
            "emote-peekaboo", "emote-sumo", "emote-charging", "emote-ninjarun", 
            "emote-proposing", "emote-ropepull", "emote-secrethandshake", "emote-elbowbump", 
            "emote-baseball", "emote-hug", "emote-hugyourself", "emote-snowball", 
            "emote-hot", "emote-levelup", "emote-snowangel", "emote-apart", 
            "emote-hero", "emote-curtsy", "emote-bow", "emote-headball", 
            "emote-fail2", "emote-fail1", "emote-boo", "emote-wings", 
            "emote-model", "emote-theatrical", "emote-laughing2", "emote-jetpack", 
            "emote-bunnyhop", "emote-death2", "emote-death", "emote-disco", 
            "emote-faint", "emote-cold", "emote-handstand", "emote-ghost-idle", 
            "emote-splitsdrop", "emote-deathdrop", "emote-heartfingers", "emote-heartshape", 
            "emote-think", "emote-disappear", "emote-frollicking", "emote-graceful", 
            "emote-greedy", "emote-lust", "emote-mindblown", "emote-thumbsup", 
            "emote-clap", "emote-mad", "emote-sleepy", "emote-thewave", 
            "emote-suckthumb", "emote-peace", "emote-panic", "emote-jumpb", 
            "emote-hearteyes", "emote-exasperated", "emote-exasperatedb", "emote-dab", 
            "emote-gangnam", "emote-harlemshake", "emote-tapdance", "emote-yes", 
            "emote-sad", "emote-robot", "emote-rainbow", "emote-no", 
            "emote-nightfever", "emote-laughing", "emote-kiss", "emote-judochop", 
            "emote-hello", "emote-happy", "emote-gordonshuffle", "emote-zombierun", 
            "emote-pose8", "emote-pose7", "emote-pose5", "emote-pose3", 
            "emote-pose1", "emote-cutey", "emote-astronaut", "emote-punkguitar", 
            "emote-gravity", "emote-fashionista", "emote-wave", "emote-bow2", 
            "emote-curtsy2", "emote-point", "emote-shrug", "emote-nod", 
            "emote-shake", "emote-salute", "emote-flex2", "emote-dance1", 
            "emote-dance2", "emote-dance3", "emote-sing", "idle-floating",
            "emote-shy", "emote-tired", "dance-pinguin", "idle-guitar",
            "emote-stargazer", "emote-boxer", "dance-creepypuppet", "dance-anime",
            "emote-creepycute", "emote-headblowup", "emote-shy2", "emote-pose10",
            "emote-iceskating", "idle-wild", "idle-nervous", "emote-timejump",
            "idle-toilet", "dance-jinglebell", "emote-hyped", "emote-sleigh",
            "emote-pose6", "dance-kawai", "dance-touch", "sit-relaxed",
            "emote-celebrationstep", "dance-employee", "emote-launch", "emote-cutesalute",
            "dance-tiktok11", "emote-gift", "emote-pose9", "emote-kissing-bound",
            "dance-wild", "idle_zombie", "idle_layingdown2", "idle-loop-tired",
            "idle-loop-tapdance", "idle-loop-shy", "idle-loop-sad", "idle-loop-happy",
            "idle-loop-annoyed", "idle-loop-aerobics", "idle-lookup", "idle-hero",
            "idle-dance-swinging", "idle-dance-headbobbing", "emote-attention",
            "emoji-ghost", "emote-lagughing", "emoji-eyeroll", "dance-sexy",
            "emote-puppet", "sit-open", "emote-stargaze", "emote-kawaiigogo",
            "idle-dance-tiktok7", "emote-shrink", "emote-trampoline", "emote-howl",
            "idle-howl", "emote-guitar", 
            "emote-drums", "emote-violin", "emote-piano", "emote-microphone",
            
            # الرقصات الجديدة المضافة
            "emoji-angry", "emoji-celebrate", "emoji-cursing",

            # رقصات تبدأ بـ dance (75 رقصة)
            "dance-tiktok10", "dance-weird", "dance-tiktok9", "dance-shoppingcart", 
            "dance-zombie", "dance-pennywise", "dance-floss", "dance-blackpink", 
            "dance-russian", "dance-spiritual", "dance-smoothwalk", "dance-singleladies", 
            "dance-sexy", "dance-robotic", "dance-duckwalk", "dance-voguehands", 
            "dance-orangejustice", "dance-tiktok8", "dance-tiktok2", "dance-metal", 
            "dance-aerobics", "dance-martial-artist", "dance-macarena", "dance-handsup", 
            "dance-breakdance", "dance-icecream", "dance-wrong", "dance-tiktok3", 
            "dance-tiktok4", "dance-tiktok5", "dance-tiktok6", "dance-tiktok7", 
            "dance-ballet", "dance-waltz", "dance-tango", "dance-salsa", 
            "dance-hip-hop", "dance-breakdance2", "dance-moonwalk", "dance-robot2", 
            "dance-shuffle", "dance-twist", "dance-charleston", "dance-can-can", 
            "dance-belly", "dance-folk", "dance-modern", "dance-jazz", 
            "dance-tap", "dance-latin", "dance-ballroom", "dance-street", 
            "dance-freestyle", "dance-contemporary", "dance-swing", "dance-foxtrot", 
            "dance-quickstep", "dance-viennese", "dance-rumba", "dance-cha-cha", 
            "dance-samba", "dance-jive", "dance-paso", "dance-argentine", 
            "dance-cuban", "dance-merengue",

            # رقصات تبدأ بـ idle (20 رقصة)
            "idle-fighter", "idle-dance-tiktok7", "idle_singing", "idle-enthusiastic", 
            "idle-floorsleeping2", "idle-floorsleeping", "idle-posh", "idle-sad", 
            "idle-angry", "idle-hero", "idle-lookup", "idle_relaxed", 
            "idle_layingdown", "idle-sleep", "idle-loop-annoyed", "idle-loop-tapdance", 
            "idle-loop-sad", "idle-loop-happy", "idle-loop-aerobics", "idle-dance-swinging", 
            "idle-loop-tired", "idle-loop-shy", "idle-loop-sitfloor", "idle-dance-casual", 
            "idle-dance-tiktok4", "idle-uwu",

            # رقصات أخرى تبدأ بـ emoji و sit و Idle (13 رقصة)
            "emoji-ghost", "emoji-sick", "emoji-naughty", "emoji-pray", 
            "emoji-halo", "emoji-sneeze", "emoji-hadoken", "emoji-arrogance", 
            "emoji-smirking", "emoji-lying", "emoji-give-up", "emoji-punch", 
            "emoji-poop", "emoji-there", "emoji-scared", "emoji-eyeroll", 
            "emoji-crying", "emoji-gagging", "emoji-flex", "emoji-celebrate", 
            "emoji-cursing", "emoji-dizzy", "sit-idle-cute", "Idle_zombie",
            
            # الرقصات الجديدة المضافة
            "idle-space", "dance-popularvibe"
        ]
        
        # رقصات ذات أرقام مخصصة (خارج نطاق القائمة)
        self.special_emotes = {
            500: "sit-idle-cute",
            501: "sit-idle-laidBack",
        }

        self.load_emotes_data()
        actual_count = len(self.emotes_list)
        print(f"💃 مدير الرقصات جاهز مع {actual_count} رقصة")

    def load_emotes_data(self):
        """تحميل بيانات الرقصات من الملف"""
        try:
            if os.path.exists(self.emotes_data_file):
                with open(self.emotes_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "emotes_list" in data:
                        self.emotes_list = data["emotes_list"]
            else:
                os.makedirs("data", exist_ok=True)
                self.save_emotes_data()
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات الرقصات: {e}")

    def save_emotes_data(self):
        """حفظ بيانات الرقصات إلى الملف"""
        try:
            data = {
                "emotes_list": self.emotes_list,
                "total_emotes": len(self.emotes_list)
            }
            with open(self.emotes_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات الرقصات: {e}")

    def get_emote_by_number(self, number: int) -> str:
        """الحصول على الرقصة بالرقم مع التحقق"""
        try:
            # فحص الأرقام المخصصة أولاً
            if number in self.special_emotes:
                emote_name = self.special_emotes[number]
                print(f"🎯 طلب رقصة مخصصة رقم {number}: {emote_name}")
                return emote_name
            if 1 <= number <= len(self.emotes_list):
                emote_name = self.emotes_list[number - 1]
                print(f"🎯 طلب رقصة رقم {number}: {emote_name}")
                return emote_name
            print(f"❌ رقم رقصة غير صحيح: {number} (المتاح: 1-{len(self.emotes_list)} أو أرقام مخصصة: {list(self.special_emotes.keys())})")
            return None
        except Exception as e:
            print(f"خطأ في الحصول على الرقصة: {e}")
            return None

    def get_emote_number(self, emote_name: str) -> int:
        """الحصول على رقم الرقصة"""
        try:
            # فحص الأرقام المخصصة أولاً
            for num, name in self.special_emotes.items():
                if name == emote_name:
                    return num
            if emote_name in self.emotes_list:
                return self.emotes_list.index(emote_name) + 1
            return None
        except Exception as e:
            print(f"خطأ في الحصول على رقم الرقصة: {e}")
            return None

    def get_emotes_list_formatted(self, page: int = 1, items_per_page: int = 20) -> str:
        """عرض قائمة الرقصات مع الأرقام مقسمة لصفحات"""
        try:
            total_emotes = len(self.emotes_list)
            total_pages = (total_emotes + items_per_page - 1) // items_per_page
            
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages
            
            start_index = (page - 1) * items_per_page
            end_index = min(start_index + items_per_page, total_emotes)
            
            result = f"💃 قائمة الرقصات (صفحة {page} من {total_pages}):\n\n"
            
            for i in range(start_index, end_index):
                emote_number = i + 1
                emote_name = self.emotes_list[i]
                result += f"🔹 {emote_number}: {emote_name}\n"
            
            result += f"\n📊 المجموع: {total_emotes} رقصة"
            result += f"\n💡 استخدم: رقص [رقم] أو ارقص [رقم]"
            
            if total_pages > 1:
                result += f"\n📖 للصفحة التالية: الرقصات {page + 1 if page < total_pages else 1}"
            
            return result
            
        except Exception as e:
            return f"❌ خطأ في عرض قائمة الرقصات: {e}"

    def search_emote(self, search_term: str) -> str:
        """البحث عن رقصة"""
        try:
            search_term = search_term.lower().strip()
            found_emotes = []
            
            for i, emote in enumerate(self.emotes_list):
                if search_term in emote.lower():
                    found_emotes.append((i + 1, emote))
            
            if not found_emotes:
                return f"❌ لم يتم العثور على أي رقصة تحتوي على '{search_term}'"
            
            result = f"🔍 نتائج البحث عن '{search_term}':\n\n"
            for number, emote in found_emotes[:10]:  # عرض أول 10 نتائج
                result += f"🔹 {number}: {emote}\n"
            
            if len(found_emotes) > 10:
                result += f"\n... وأكثر من {len(found_emotes) - 10} نتيجة أخرى"
            
            return result
            
        except Exception as e:
            return f"❌ خطأ في البحث: {e}"

    def get_random_emote(self) -> tuple:
        """الحصول على رقصة عشوائية"""
        try:
            import random
            random_index = random.randint(0, len(self.emotes_list) - 1)
            emote_name = self.emotes_list[random_index]
            emote_number = random_index + 1
            return emote_number, emote_name
        except Exception as e:
            print(f"خطأ في الحصول على رقصة عشوائية: {e}")
            return None, None

    def get_emotes_count(self) -> int:
        """الحصول على عدد الرقصات"""
        return len(self.emotes_list)
