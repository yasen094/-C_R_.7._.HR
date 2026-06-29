
"""
نظام تتبع المواقع - مراقبة وحفظ مواقع المستخدمين
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from highrise import Position, AnchorPosition, User

class LocationTracker:
    def __init__(self):
        self.data_file = "data/user_locations.json"
        self.user_locations = {}  # user_id -> {position, last_update, username}
        self.load_locations_data()
        print("📍 نظام تتبع المواقع جاهز")

    def load_locations_data(self):
        """تحميل بيانات المواقع المحفوظة"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.user_locations = json.load(f)
                print(f"📂 تم تحميل مواقع {len(self.user_locations)} مستخدم")
            else:
                os.makedirs("data", exist_ok=True)
                self.user_locations = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات المواقع: {e}")
            self.user_locations = {}

    def save_locations_data(self):
        """حفظ بيانات المواقع"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_locations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات المواقع: {e}")

    def position_to_dict(self, position):
        """تحويل Position إلى dictionary"""
        if isinstance(position, Position):
            facing_name = "FrontRight"
            if hasattr(position, 'facing') and position.facing:
                if hasattr(position.facing, 'name'):
                    facing_name = position.facing.name
                elif isinstance(position.facing, str):
                    facing_name = position.facing
            
            return {
                "type": "Position",
                "x": position.x,
                "y": position.y,
                "z": position.z,
                "facing": facing_name
            }
        elif isinstance(position, AnchorPosition):
            return {
                "type": "AnchorPosition",
                "entity_id": position.entity_id,
                "anchor_ix": position.anchor_ix
            }
        return None

    def dict_to_position(self, pos_dict):
        """تحويل dictionary إلى Position"""
        from highrise.models import Position, AnchorPosition, Facing
        
        if pos_dict["type"] == "Position":
            facing = getattr(Facing, pos_dict.get("facing", "FrontRight"))
            return Position(
                x=pos_dict["x"],
                y=pos_dict["y"], 
                z=pos_dict["z"],
                facing=facing
            )
        elif pos_dict["type"] == "AnchorPosition":
            return AnchorPosition(
                entity_id=pos_dict["entity_id"],
                anchor_ix=pos_dict["anchor_ix"]
            )
        return None

    def update_user_location(self, user: User, position):
        """تحديث موقع المستخدم"""
        try:
            pos_dict = self.position_to_dict(position)
            if pos_dict:
                self.user_locations[user.id] = {
                    "position": pos_dict,
                    "username": user.username,
                    "last_update": datetime.now().isoformat(),
                    "x": pos_dict.get("x", 0),
                    "y": pos_dict.get("y", 0),
                    "z": pos_dict.get("z", 0)
                }
                # حفظ كل 10 تحديثات لتجنب الكثرة
                if len(self.user_locations) % 10 == 0:
                    self.save_locations_data()
        except Exception as e:
            print(f"خطأ في تحديث موقع {user.username}: {e}")

    def get_user_location(self, user_id: str) -> Optional[Dict]:
        """الحصول على آخر موقع للمستخدم"""
        return self.user_locations.get(user_id)

    def get_user_location_by_username(self, username: str) -> Optional[Dict]:
        """الحصول على آخر موقع للمستخدم بالاسم"""
        for user_id, data in self.user_locations.items():
            if data["username"].lower() == username.lower():
                return data
        return None

    def find_nearest_users(self, target_user_id: str, max_distance: float = 10.0) -> list:
        """العثور على المستخدمين الأقرب للمستخدم المحدد"""
        target_data = self.get_user_location(target_user_id)
        if not target_data:
            return []

        target_x = target_data.get("x", 0)
        target_z = target_data.get("z", 0)
        
        nearby_users = []
        
        for user_id, data in self.user_locations.items():
            if user_id == target_user_id:
                continue
                
            user_x = data.get("x", 0)
            user_z = data.get("z", 0)
            
            # حساب المسافة (نتجاهل Y للبساطة)
            distance = ((target_x - user_x) ** 2 + (target_z - user_z) ** 2) ** 0.5
            
            if distance <= max_distance:
                nearby_users.append({
                    "username": data["username"],
                    "user_id": user_id,
                    "distance": round(distance, 2),
                    "position": data["position"]
                })
        
        # ترتيب حسب المسافة
        nearby_users.sort(key=lambda x: x["distance"])
        return nearby_users

    def get_location_stats(self) -> str:
        """الحصول على إحصائيات المواقع"""
        total_users = len(self.user_locations)
        if total_users == 0:
            return "📍 لا توجد مواقع محفوظة"
        
        # حساب متوسط المواقع
        avg_x = sum(data.get("x", 0) for data in self.user_locations.values()) / total_users
        avg_z = sum(data.get("z", 0) for data in self.user_locations.values()) / total_users
        
        return f"""📍 إحصائيات المواقع:
👥 عدد المستخدمين المتتبعين: {total_users}
📊 متوسط الموقع: ({avg_x:.1f}, {avg_z:.1f})
📅 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"""

    def clear_old_locations(self, hours: int = 24):
        """مسح المواقع القديمة"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            old_locations = []
            for user_id, data in list(self.user_locations.items()):
                last_update = datetime.fromisoformat(data["last_update"])
                if last_update < cutoff_time:
                    old_locations.append(user_id)
                    del self.user_locations[user_id]
            
            if old_locations:
                self.save_locations_data()
                print(f"🧹 تم مسح {len(old_locations)} موقع قديم")
            
            return len(old_locations)
        except Exception as e:
            print(f"خطأ في مسح المواقع القديمة: {e}")
            return 0

    def remove_user_location(self, user_id: str):
        """إزالة موقع مستخدم معين"""
        if user_id in self.user_locations:
            del self.user_locations[user_id]
            self.save_locations_data()
