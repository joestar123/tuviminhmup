import streamlit as st
import pandas as pd
from lunar_python import Lunar, Solar
import itertools
import math

# ==========================================
# PHẦN 1: CẤU HÌNH & TỪ ĐIỂN DỮ LIỆU
# ==========================================

TRANSLATE = {"甲": "Giáp", "乙": "Ất", "丙": "Bính", "丁": "Đinh", "戊": "Mậu", "己": "Kỷ", "庚": "Canh", "辛": "Tân", "壬": "Nhâm", "癸": "Quý",
             "子": "Tý", "丑": "Sửu", "寅": "Dần", "卯": "Mão", "辰": "Thìn", "巳": "Tỵ", "午": "Ngọ", "未": "Mùi", "申": "Thân", "酉": "Dậu", "戌": "Tuất", "亥": "Hợi"}
ZHI_LIST = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
GAN_LIST = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

ELEMENTS = {"Giáp": "Mộc", "Ất": "Mộc", "Bính": "Hỏa", "Đinh": "Hỏa", "Mậu": "Thổ", "Kỷ": "Thổ", "Canh": "Kim", "Tân": "Kim", "Nhâm": "Thủy", "Quý": "Thủy"}
ZHI_ELEMENTS = {"Tý": "Thủy", "Sửu": "Thổ", "Dần": "Mộc", "Mão": "Mộc", "Thìn": "Thổ", "Tỵ": "Hỏa", "Ngọ": "Hỏa", "Mùi": "Thổ", "Thân": "Kim", "Dậu": "Kim", "Tuất": "Thổ", "Hợi": "Thủy"}
YIN_YANG = {"Giáp": True, "Bính": True, "Mậu": True, "Canh": True, "Nhâm": True, "Ất": False, "Đinh": False, "Kỷ": False, "Tân": False, "Quý": False}

HIDDEN_STEMS = {"Tý": ["Quý"], "Sửu": ["Kỷ", "Quý", "Tân"], "Dần": ["Giáp", "Bính", "Mậu"], "Mão": ["Ất"], "Thìn": ["Mậu", "Ất", "Quý"], "Tỵ": ["Bính", "Mậu", "Canh"],
                "Ngọ": ["Đinh", "Kỷ"], "Mùi": ["Kỷ", "Đinh", "Ất"], "Thân": ["Canh", "Nhâm", "Mậu"], "Dậu": ["Tân"], "Tuất": ["Mậu", "Tân", "Đinh"], "Hợi": ["Nhâm", "Giáp"]}

RELATIONS = {
    "Mộc": {"Mộc": "Tỷ/Kiếp", "Hỏa": "Thực/Thương", "Thổ": "Tài", "Kim": "Quan/Sát", "Thủy": "Ấn"},
    "Hỏa": {"Hỏa": "Tỷ/Kiếp", "Thổ": "Thực/Thương", "Kim": "Tài", "Thủy": "Quan/Sát", "Mộc": "Ấn"},
    "Thổ": {"Thổ": "Tỷ/Kiếp", "Kim": "Thực/Thương", "Thủy": "Tài", "Mộc": "Quan/Sát", "Hỏa": "Ấn"},
    "Kim": {"Kim": "Tỷ/Kiếp", "Thủy": "Thực/Thương", "Mộc": "Tài", "Hỏa": "Quan/Sát", "Thổ": "Ấn"},
    "Thủy": {"Thủy": "Tỷ/Kiếp", "Mộc": "Thực/Thương", "Hỏa": "Tài", "Thổ": "Quan/Sát", "Kim": "Ấn"}
}

STAR_STATE = { 
    "Tử Vi": ["B", "Đ", "M", "V", "B", "V", "M", "Đ", "V", "B", "B", "V"],
    "Thiên Cơ": ["M", "H", "Đ", "V", "B", "B", "M", "H", "Đ", "V", "B", "B"],
    "Thái Dương": ["H", "H", "V", "M", "V", "V", "M", "Đ", "B", "B", "H", "H"],
    "Vũ Khúc": ["V", "M", "B", "V", "M", "B", "V", "M", "B", "V", "M", "B"],
    "Thiên Đồng": ["V", "H", "B", "Đ", "B", "M", "H", "H", "V", "B", "B", "M"],
    "Liêm Trinh": ["B", "Đ", "M", "B", "V", "H", "B", "Đ", "M", "B", "V", "H"],
    "Thiên Phủ": ["M", "M", "M", "B", "M", "B", "M", "M", "M", "B", "M", "B"],
    "Thái Âm": ["V", "M", "B", "H", "H", "H", "H", "B", "Đ", "V", "V", "M"],
    "Tham Lang": ["V", "M", "B", "H", "M", "H", "V", "M", "B", "H", "M", "H"],
    "Cự Môn": ["V", "H", "M", "M", "H", "B", "V", "H", "M", "M", "H", "B"],
    "Thiên Tướng": ["V", "M", "M", "H", "V", "Đ", "V", "M", "M", "H", "V", "Đ"],
    "Thiên Lương": ["M", "V", "M", "V", "M", "H", "M", "V", "M", "V", "M", "H"],
    "Thất Sát": ["M", "M", "M", "V", "B", "B", "M", "M", "M", "V", "B", "B"],
    "Phá Quân": ["M", "V", "H", "H", "V", "B", "M", "V", "H", "H", "V", "B"]
}

CUNG_NAMES = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc", "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]
TRANG_SINH_12 = ["Tràng Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"]

TU_HOA_MAP = {
    "Giáp": {"Liêm Trinh": "Lộc", "Phá Quân": "Quyền", "Vũ Khúc": "Khoa", "Thái Dương": "Kỵ"},
    "Ất": {"Thiên Cơ": "Lộc", "Thiên Lương": "Quyền", "Tử Vi": "Khoa", "Thái Âm": "Kỵ"},
    "Bính": {"Thiên Đồng": "Lộc", "Thiên Cơ": "Quyền", "Văn Xương": "Khoa", "Liêm Trinh": "Kỵ"},
    "Đinh": {"Thái Âm": "Lộc", "Thiên Đồng": "Quyền", "Thiên Cơ": "Khoa", "Cự Môn": "Kỵ"},
    "Mậu": {"Tham Lang": "Lộc", "Thái Âm": "Quyền", "Hữu Bật": "Khoa", "Thiên Cơ": "Kỵ"},
    "Kỷ": {"Vũ Khúc": "Lộc", "Tham Lang": "Quyền", "Thiên Lương": "Khoa", "Văn Khúc": "Kỵ"},
    "Canh": {"Thái Dương": "Lộc", "Vũ Khúc": "Quyền", "Thái Âm": "Khoa", "Thiên Đồng": "Kỵ"},
    "Tân": {"Cự Môn": "Lộc", "Thái Dương": "Quyền", "Văn Khúc": "Khoa", "Văn Xương": "Kỵ"},
    "Nhâm": {"Thiên Lương": "Lộc", "Tử Vi": "Quyền", "Thiên Phủ": "Khoa", "Vũ Khúc": "Kỵ"},
    "Quý": {"Phá Quân": "Lộc", "Cự Môn": "Quyền", "Thái Âm": "Khoa", "Tham Lang": "Kỵ"}
}

TU_HOA_LUAN_GIAI = {
    "Lộc": {"Mệnh": "Có duyên với tiền bạc, vui vẻ, hay gặp may mắn.", "Huynh Đệ": "Anh em hòa thuận, thường giúp đỡ nhau về tài chính.", "Phu Thê": "Hôn phối mang lại tài lộc.", "Tử Tức": "Con cái ngoan ngoãn, mang lại niềm vui.", "Tài Bạch": "Rất thuận lợi kiếm tiền.", "Tật Ách": "Giải hung cứu khốn.", "Thiên Di": "Ra ngoài hay gặp quý nhân.", "Nô Bộc": "Bạn bè, đối tác đắc lực.", "Quan Lộc": "Công danh suôn sẻ.", "Điền Trạch": "Nhà cửa êm ấm.", "Phúc Đức": "Hưởng phúc dòng họ.", "Phụ Mẫu": "Cha mẹ yêu thương hỗ trợ."},
    "Quyền": {"Mệnh": "Có uy quyền, năng lực lãnh đạo.", "Huynh Đệ": "Anh em dễ lấn lướt mình.", "Phu Thê": "Vợ/chồng giỏi giang nhưng hay lấn lướt.", "Tử Tức": "Con cái bướng bỉnh, có cá tính mạnh.", "Tài Bạch": "Thích cầm trịch tài chính.", "Tật Ách": "Sức khỏe tốt.", "Thiên Di": "Ra ngoài có uy thế.", "Nô Bộc": "Bạn bè giỏi, cần biết thu phục.", "Quan Lộc": "Sự nghiệp thăng tiến.", "Điền Trạch": "Có tài quản lý tài sản.", "Phúc Đức": "Thích chi phối người khác.", "Phụ Mẫu": "Cha mẹ nghiêm khắc."},
    "Khoa": {"Mệnh": "Thanh nhã, hiếu học, giải thần.", "Huynh Đệ": "Anh em hiền lành.", "Phu Thê": "Vợ/chồng cư xử nho nhã.", "Tử Tức": "Con cái thông minh, học giỏi.", "Tài Bạch": "Kiếm tiền minh bạch.", "Tật Ách": "Gặp hung hóa cát.", "Thiên Di": "Ra ngoài giữ tiếng thơm.", "Nô Bộc": "Bạn bè tử tế.", "Quan Lộc": "Công việc thiên về học thuật.", "Điền Trạch": "Môi trường sống trí thức.", "Phúc Đức": "Tâm hồn thanh cao.", "Phụ Mẫu": "Cha mẹ hiểu biết."},
    "Kỵ": {"Mệnh": "Nhiều thăng trầm, hay lo nghĩ.", "Huynh Đệ": "Anh em dễ bất hòa.", "Phu Thê": "Tình duyên trắc trở.", "Tử Tức": "Muộn con hoặc phiền lòng vì con.", "Tài Bạch": "Dòng tiền hay tắc nghẽn.", "Tật Ách": "Dễ mắc bệnh.", "Thiên Di": "Ra ngoài dễ gặp thị phi.", "Nô Bộc": "Dễ bị phản trắc.", "Quan Lộc": "Công việc lận đận.", "Điền Trạch": "Rắc rối giấy tờ nhà đất.", "Phúc Đức": "Hay bồn chồn.", "Phụ Mẫu": "Khắc khẩu với cha mẹ."}
}

TINH_CACH_MAP = {
    "Mộc": "Nhân ái, hiền hòa, thẳng thắn. Có chí tiến thủ nhưng đôi khi cố chấp nếu Mộc quá vượng.",
    "Hỏa": "Nhiệt tình, sáng tạo, năng động, trọng lễ. Tính tình có phần nóng vội, cả thèm chóng chán.",
    "Thổ": "Trầm ổn, đáng tin cậy, bao dung, trọng tín nghĩa. Làm việc chắc chắn nhưng đôi khi bảo thủ.",
    "Kim": "Sắc sảo, quyết đoán, trọng nghĩa khí, kiên cường. Rất dứt khoát nhưng đôi khi lạnh lùng.",
    "Thủy": "Linh hoạt, thông minh, khéo léo ứng xử, nhiều tâm sự. Giỏi thích nghi nhưng khí chất dễ thay đổi."
}

NGHE_NGHIEP_MAP = {
    "Chính Quan": "Phù hợp nhà nước, hành chính, quản lý, kỷ luật cao.", "Thất Sát": "Quân đội, công an, lãnh đạo, khai phá, mạo hiểm.",
    "Chính Ấn": "Giáo dục, giảng dạy, nghiên cứu, y tế, văn phòng.", "Thiên Ấn": "Nghệ thuật, y học cổ truyền, tôn giáo, IT, thiết kế.",
    "Chính Tài": "Tài chính, ngân hàng, kế toán, kinh doanh ổn định.", "Thiên Tài": "Đầu tư, kinh doanh tự do, bán hàng, lợi nhuận đột phá.",
    "Thực Thần": "Sư phạm, tư vấn, ẩm thực, phúc lợi xã hội.", "Thương Quan": "Nghệ thuật, diễn thuyết, truyền thông, marketing, luật sư.",
    "Tỷ Kiên": "Tự lập kinh doanh, làm việc nhóm, độc lập.", "Kiếp Tài": "Thể thao, cạnh tranh thương mại, môi giới."
}

# ==========================================
# PHẦN 2: ĐỘNG CƠ PHÂN TÍCH (ENGINES)
# ==========================================

class BaziScorer:
    def __init__(self, gans, zhis):
        self.gans = gans
        self.zhis = zhis
        self.nhat_chu = gans[2]
        self.nc_el = ELEMENTS.get(self.nhat_chu, "Mộc")
        self.scores = {"Mộc": 0, "Hỏa": 0, "Thổ": 0, "Kim": 0, "Thủy": 0}
        self._calculate_scores()
        
    def _calculate_scores(self):
        weights = [10, 35, 12, 10] 
        zhi_weights = [15, 40, 15, 12]
        for i in range(4):
            can_el = ELEMENTS.get(self.gans[i])
            chi_el = ZHI_ELEMENTS.get(self.zhis[i])
            if can_el: self.scores[can_el] += weights[i]
            if chi_el: self.scores[chi_el] += zhi_weights[i]
            for stem in HIDDEN_STEMS.get(self.zhis[i], []):
                h_el = ELEMENTS.get(stem)
                if h_el: self.scores[h_el] += (5 if i == 1 else 3)
                
    def get_analysis(self):
        total = sum(self.scores.values()) or 1
        percentages = {k: round((v/total)*100, 1) for k, v in self.scores.items()}
        sinh_el = [k for k, v in RELATIONS.get(self.nc_el, {}).items() if v == "Ấn"][0]
        friendly_score = percentages.get(self.nc_el, 0) + percentages.get(sinh_el, 0)
        
        month_zhi = self.zhis[1]
        month_zhi_el = ZHI_ELEMENTS.get(month_zhi)
        dac_lenh = month_zhi_el in [self.nc_el, sinh_el]
        
        is_strong = friendly_score >= 40 if dac_lenh else friendly_score > 50
        
        dung_than, hy_than, ky_than = [], [], []
        dieu_hau_msg = "" 
        status = f"Thân {'Vượng' if is_strong else 'Nhược'} ({friendly_score}% Phù trợ)"
        
        khac_sinh_el = [k for k, v in RELATIONS.get(sinh_el, {}).items() if v == "Quan/Sát"][0] 
        tiet_nc_el = [k for k, v in RELATIONS.get(self.nc_el, {}).items() if v == "Thực/Thương"][0]
        khac_nc_el = [k for k, v in RELATIONS.get(self.nc_el, {}).items() if v == "Quan/Sát"][0]
        
        if is_strong and percentages.get(sinh_el, 0) >= 35 and percentages.get(self.nc_el, 0) < 20:
            dung_than = [khac_sinh_el]; hy_than = [tiet_nc_el]; ky_than = [sinh_el, khac_nc_el]
            if self.nc_el == "Kim" and sinh_el == "Thổ": status += " - CÁCH CỤC: THỔ ĐA KIM MAI"
            elif self.nc_el == "Hỏa" and sinh_el == "Mộc": status += " - CÁCH CỤC: MỘC ĐA HỎA TẮC"
            elif self.nc_el == "Thủy" and sinh_el == "Kim": status += " - CÁCH CỤC: KIM ĐA THỦY TRƯỢC"
            elif self.nc_el == "Mộc" and sinh_el == "Thủy": status += " - CÁCH CỤC: THỦY ĐA MỘC PHIÊU"
            elif self.nc_el == "Thổ" and sinh_el == "Hỏa": status += " - CÁCH CỤC: HỎA ĐA THỔ TIÊU"
                
        if not dung_than: 
            hoa_perc = percentages.get("Hỏa", 0)
            thuy_perc = percentages.get("Thủy", 0)
            is_dieu_hau = False
            
            if month_zhi in ["Hợi", "Tý", "Sửu", "Tuất"]:
                if hoa_perc < 15 and thuy_perc >= 20:
                    dung_than = ["Hỏa"]; hy_than = ["Mộc"]; ky_than = ["Thủy", "Kim"]
                    dieu_hau_msg = "Sinh mùa Đông hàn khí cực thịnh. Cấp thiết cần Bính Hỏa sưởi ấm cục diện."
                    is_dieu_hau = True
                elif hoa_perc >= 30:
                    dieu_hau_msg = "Sinh mùa Đông nhưng mệnh Hỏa khí dồi dào, bố cục tự ấm."
            
            elif month_zhi in ["Tỵ", "Ngọ", "Mùi", "Thìn"]:
                if thuy_perc < 15 and hoa_perc >= 20:
                    dung_than = ["Thủy"]; hy_than = ["Kim"]; ky_than = ["Hỏa", "Mộc", "Thổ"]
                    dieu_hau_msg = "Sinh mùa Hạ hỏa viêm thổ táo. Cấp thiết cần Nhâm Thủy nhuận trạch."
                    is_dieu_hau = True
                elif thuy_perc >= 30:
                    dieu_hau_msg = "Sinh mùa Hạ nhưng Thủy khí sung mãn, mệnh cục tự mát mẻ."

            if not is_dieu_hau:
                if is_strong: dung_than = [tiet_nc_el, khac_sinh_el]; hy_than = [khac_nc_el]; ky_than = [self.nc_el, sinh_el]
                else: dung_than = [sinh_el]; hy_than = [self.nc_el]; ky_than = [khac_nc_el, khac_sinh_el]
                
        dominant_el = max(self.scores, key=self.scores.get)
        return {
            "status": status, "percentages": percentages, "is_strong": is_strong,
            "dung_than": dung_than, "hy_than": hy_than, "ky_than": ky_than,
            "dominant_el": dominant_el, "dieu_hau_msg": dieu_hau_msg
        }

class TuviRuleEngine:
    def __init__(self, palaces, menh_idx, tuan_idx, triet_idx):
        self.palaces = palaces
        self.menh_idx = menh_idx
        self.tuan_idx = tuan_idx
        self.triet_idx = triet_idx
        self.sat_tinh_luc = ["Kình Dương", "Đà La", "Địa Không", "Địa Kiếp", "Hỏa Tinh", "Linh Tinh"]
        
    def _get_stars_in_palaces(self, indices):
        stars = {"main": [], "bad": [], "minor": []}
        for idx in indices:
            for s in self.palaces[idx]["main"]: stars["main"].append(s.split(" (")[0])
            stars["bad"].extend([s for s in self.palaces[idx]["bad"]])
            stars["minor"].extend([s for s in self.palaces[idx]["minor"]])
        return set(stars["main"]), set(stars["bad"]), set(stars["minor"])

    def evaluate_menh(self):
        tp_indices = [self.menh_idx, (self.menh_idx + 4) % 12, (self.menh_idx + 8) % 12, (self.menh_idx + 6) % 12]
        main_set, bad_set, minor_set = self._get_stars_in_palaces(tp_indices)
        
        bi_tuan_triet = (self.menh_idx in self.tuan_idx) or (self.menh_idx in self.triet_idx)
        sat_tinh_count = len(bad_set.intersection(self.sat_tinh_luc))
        
        base_cach = "Tạp Cách (Cần mượn vận Đại hạn)"
        level = "Thành Cách"
        
        if any(s in [m.split(" (")[0] for m in self.palaces[self.menh_idx]["main"]] for s in ["Thất Sát", "Phá Quân", "Tham Lang"]):
            base_cach = "SÁT PHÁ THAM (Hành động, bứt phá, mạo hiểm)"
            if bi_tuan_triet or sat_tinh_count >= 3: level = "Bán Cách / Phá Cách (Gặp cản trở, thăng trầm)"
        elif len({"Thiên Cơ", "Thái Âm", "Thái Dương", "Thiên Lương"}.intersection(main_set)) >= 3 and "Thiên Lương" in main_set:
            base_cach = "CƠ ÂM DƯƠNG LƯƠNG (Thông tuệ, học thuật, tham mưu, quyền biến)"
            if sat_tinh_count >= 2: level = "Phá Cách"
            elif bi_tuan_triet: level = "Bán Cách"
        elif len({"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"}.intersection(main_set)) >= 3:
            base_cach = "CƠ NGUYỆT ĐỒNG LƯƠNG (Tham mưu, trí thức, ổn định)"
            if sat_tinh_count >= 2: level = "Phá Cách"
            elif bi_tuan_triet: level = "Bán Cách"
        elif len({"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"}.intersection(main_set)) >= 3:
            base_cach = "TỬ PHỦ VŨ TƯỚNG (Lãnh đạo, quản lý, cẩn trọng)"
            if "Địa Không" in bad_set or "Địa Kiếp" in bad_set or bi_tuan_triet: level = "Phá Cách (Hư danh, trắc trở)"
        elif not self.palaces[self.menh_idx]["main"]:
            base_cach = "VÔ CHÍNH DIỆU (Uyển chuyển, linh hoạt)"
            if bi_tuan_triet: level = "Thành Cách (Đắc Tuần/Triệt)"
            elif "Tuần" not in self.tuan_idx and "Triệt" not in self.triet_idx: level = "Bán Cách (Dễ trôi dạt)"

        return f"{base_cach} - Độ thuần: {level} (Có {sat_tinh_count} Sát tinh hội hợp)"

def get_thap_than(nhat_chu, target):
    if not nhat_chu or not target: return ""
    nc_el, tgt_el = ELEMENTS.get(nhat_chu), ELEMENTS.get(target)
    if not nc_el or not tgt_el or target not in YIN_YANG: return ""
    same_pol = YIN_YANG.get(nhat_chu) == YIN_YANG.get(target)
    base = RELATIONS[nc_el][tgt_el]
    return {"Tỷ/Kiếp": "Tỷ Kiên" if same_pol else "Kiếp Tài", "Thực/Thương": "Thực Thần" if same_pol else "Thương Quan",
            "Tài": "Thiên Tài" if same_pol else "Chính Tài", "Quan/Sát": "Thất Sát" if same_pol else "Chính Quan",
            "Ấn": "Thiên Ấn" if same_pol else "Chính Ấn"}[base]

def check_cach_cuc_thau_can(gans, zhis, nhat_chu):
    month_zhi = zhis[1]
    hidden_of_month = HIDDEN_STEMS.get(month_zhi, [])
    revealed_gans = [gans[0], gans[1], gans[3]]
    
    def get_matching_revealed_gan(hidden_can):
        hidden_el = ELEMENTS.get(hidden_can)
        for g in revealed_gans:
            if ELEMENTS.get(g) == hidden_el: return g
        return None

    if hidden_of_month:
        match_main = get_matching_revealed_gan(hidden_of_month[0])
        if match_main: return f"{get_thap_than(nhat_chu, match_main)} Cách (Bản khí thấu)"
    for h_can in hidden_of_month[1:]:
        match_minor = get_matching_revealed_gan(h_can)
        if match_minor: return f"{get_thap_than(nhat_chu, match_minor)} Cách (Tạp khí thấu)"
    return f"Giả {get_thap_than(nhat_chu, hidden_of_month[0] if hidden_of_month else nhat_chu)} Cách"

def get_tuan_triet(year_gan, year_zhi):
    can_idx = GAN_LIST.index(year_gan) if year_gan in GAN_LIST else 0
    zhi_idx = ZHI_LIST.index(year_zhi) if year_zhi in ZHI_LIST else 0
    diff = (zhi_idx - can_idx) % 12
    tuan_1, tuan_2 = (diff - 2) % 12, (diff - 1) % 12
    triet_map = {"Giáp": (8, 9), "Kỷ": (8, 9), "Ất": (6, 7), "Canh": (6, 7), "Bính": (4, 5), "Tân": (4, 5), "Đinh": (2, 3), "Nhâm": (2, 3), "Mậu": (0, 1), "Quý": (0, 1)}
    triet_1, triet_2 = triet_map.get(year_gan, (0, 1))
    return (tuan_1, tuan_2), (triet_1, triet_2)

def place_trang_sinh_dai_han(cuc_num, gender, is_yang_year, menh_idx):
    is_thuan = (gender == "Nam" and is_yang_year) or (gender == "Nữ" and not is_yang_year)
    ts_start = {2: 8, 5: 8, 3: 11, 4: 5, 6: 2}.get(cuc_num, 8)
    ts_dict, dh_dict = {}, {}
    step = 1 if is_thuan else -1
    for i in range(12):
        ts_dict[(ts_start + i * step) % 12] = TRANG_SINH_12[i]
        dh_age = cuc_num + (i * 10)
        dh_dict[(menh_idx + i * step) % 12] = f"{dh_age}-{dh_age+9}"
    return ts_dict, dh_dict

def get_cuc(can_menh, zhi_menh):
    can_val = {"Giáp": 1, "Ất": 1, "Bính": 2, "Đinh": 2, "Mậu": 3, "Kỷ": 3, "Canh": 4, "Tân": 4, "Nhâm": 5, "Quý": 5}.get(can_menh, 1)
    zhi_val = {"Tý": 1, "Sửu": 1, "Ngọ": 1, "Mùi": 1, "Dần": 2, "Mão": 2, "Thân": 2, "Dậu": 2, "Thìn": 3, "Tỵ": 3, "Tuất": 3, "Hợi": 3}.get(zhi_menh, 1)
    na_yin = (can_val + zhi_val) % 5 or 5
    return {1: ("Kim Tứ Cục", 4), 2: ("Thủy Nhị Cục", 2), 3: ("Hỏa Lục Cục", 6), 4: ("Thổ Ngũ Cục", 5), 5: ("Mộc Tam Cục", 3)}[na_yin]

def build_tuvi_palaces(lunar, gender, gans, zhis):
    lunar_month = abs(lunar.getMonth())
    hour_idx = ZHI_LIST.index(zhis[3]) if zhis[3] in ZHI_LIST else 0
    menh_idx = (2 + (lunar_month - 1) - hour_idx) % 12
    
    start_idx = {"Giáp": 2, "Kỷ": 2, "Ất": 4, "Canh": 4, "Bính": 6, "Tân": 6, "Đinh": 8, "Nhâm": 8, "Mậu": 0, "Quý": 0}.get(gans[0], 0)
    can_menh = GAN_LIST[(start_idx + (menh_idx - 2 if menh_idx >= 2 else menh_idx + 10)) % 10]
    zhi_menh = ZHI_LIST[menh_idx]
    cuc_name, cuc_num = get_cuc(can_menh, zhi_menh)
    
    palaces = {i: {"main": [], "minor": [], "bad": [], "ring": []} for i in range(12)}
    
    day = lunar.getDay()
    y = math.ceil(day / cuc_num)
    diff = (y * cuc_num) - day
    tu_vi_idx = (y + 1 - diff) % 12 if diff % 2 == 1 else (y + 1 + diff) % 12
    
    palaces[tu_vi_idx]["main"].append(f"Tử Vi ({STAR_STATE['Tử Vi'][tu_vi_idx]})")
    palaces[(tu_vi_idx - 1) % 12]["main"].append(f"Thiên Cơ ({STAR_STATE['Thiên Cơ'][(tu_vi_idx - 1) % 12]})")
    palaces[(tu_vi_idx - 3) % 12]["main"].append(f"Thái Dương ({STAR_STATE['Thái Dương'][(tu_vi_idx - 3) % 12]})")
    palaces[(tu_vi_idx - 4) % 12]["main"].append(f"Vũ Khúc ({STAR_STATE['Vũ Khúc'][(tu_vi_idx - 4) % 12]})")
    palaces[(tu_vi_idx - 5) % 12]["main"].append(f"Thiên Đồng ({STAR_STATE['Thiên Đồng'][(tu_vi_idx - 5) % 12]})")
    palaces[(tu_vi_idx - 8) % 12]["main"].append(f"Liêm Trinh ({STAR_STATE['Liêm Trinh'][(tu_vi_idx - 8) % 12]})")
    
    tp = (4 - tu_vi_idx) % 12
    palaces[tp]["main"].append(f"Thiên Phủ ({STAR_STATE['Thiên Phủ'][tp]})")
    palaces[(tp + 1) % 12]["main"].append(f"Thái Âm ({STAR_STATE['Thái Âm'][(tp + 1) % 12]})")
    palaces[(tp + 2) % 12]["main"].append(f"Tham Lang ({STAR_STATE['Tham Lang'][(tp + 2) % 12]})")
    palaces[(tp + 3) % 12]["main"].append(f"Cự Môn ({STAR_STATE['Cự Môn'][(tp + 3) % 12]})")
    palaces[(tp + 4) % 12]["main"].append(f"Thiên Tướng ({STAR_STATE['Thiên Tướng'][(tp + 4) % 12]})")
    palaces[(tp + 5) % 12]["main"].append(f"Thiên Lương ({STAR_STATE['Thiên Lương'][(tp + 5) % 12]})")
    palaces[(tp + 6) % 12]["main"].append(f"Thất Sát ({STAR_STATE['Thất Sát'][(tp + 6) % 12]})")
    palaces[(tp + 10) % 12]["main"].append(f"Phá Quân ({STAR_STATE['Phá Quân'][(tp + 10) % 12]})")

    thai_tue_idx = ZHI_LIST.index(zhis[0])
    v_thaitue = ["Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù", "Tử Phù", "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù"]
    for i in range(12): palaces[(thai_tue_idx + i) % 12]["ring"].append(v_thaitue[i])

    loc_ton_map = {"Giáp": 2, "Ất": 3, "Bính": 5, "Mậu": 5, "Đinh": 6, "Kỷ": 6, "Canh": 8, "Tân": 9, "Nhâm": 11, "Quý": 0}
    lt_idx = loc_ton_map.get(gans[0], 2)
    palaces[lt_idx]["minor"].append("Lộc Tồn")
    palaces[(lt_idx + 1) % 12]["bad"].append("Kình Dương")
    palaces[(lt_idx - 1) % 12]["bad"].append("Đà La")
    
    is_yang_year = YIN_YANG.get(gans[0], True)
    thuan_bacsi = (gender == "Nam" and is_yang_year) or (gender == "Nữ" and not is_yang_year)
    v_bacsi = ["Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao", "Tướng Quân", "Tấu Thư", "Phi Liêm", "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ"]
    step = 1 if thuan_bacsi else -1
    for i in range(12): palaces[(lt_idx + i * step) % 12]["ring"].append(v_bacsi[i])

    palaces[(4 + lunar_month - 1) % 12]["minor"].append("Tả Phù")
    palaces[(10 - lunar_month + 1) % 12]["minor"].append("Hữu Bật")
    palaces[(10 - hour_idx) % 12]["minor"].append("Văn Xương")
    palaces[(4 + hour_idx) % 12]["minor"].append("Văn Khúc")
    palaces[(11 - hour_idx) % 12]["bad"].append("Địa Không")
    palaces[(11 + hour_idx) % 12]["bad"].append("Địa Kiếp")

    khoi_viet = {"Giáp": (1, 7), "Mậu": (1, 7), "Canh": (1, 7), "Ất": (0, 8), "Kỷ": (0, 8), "Bính": (11, 9), "Đinh": (11, 9), "Nhâm": (3, 5), "Quý": (3, 5), "Tân": (6, 2)}
    k_idx, v_idx = khoi_viet.get(gans[0], (0, 0))
    palaces[k_idx]["minor"].append("Thiên Khôi")
    palaces[v_idx]["minor"].append("Thiên Việt")
    
    hoa_linh_map = {"Dần": (1, 3), "Ngọ": (1, 3), "Tuất": (1, 3), "Thân": (2, 10), "Tý": (2, 10), "Thìn": (2, 10), "Tỵ": (3, 10), "Dậu": (3, 10), "Sửu": (3, 10), "Hợi": (9, 10), "Mão": (9, 10), "Mùi": (9, 10)}
    hoa_start, linh_start = hoa_linh_map.get(zhis[0], (1, 3))
    palaces[(hoa_start + hour_idx) % 12]["bad"].append("Hỏa Tinh")
    palaces[(linh_start - hour_idx) % 12]["bad"].append("Linh Tinh")
    
    return palaces, menh_idx, cuc_name, cuc_num

class TransitEngine:
    def __init__(self, birth_year, gender, menh_idx, cuc_num, is_yang_year):
        self.birth_year = birth_year
        self.gender = gender
        self.menh_idx = menh_idx
        self.cuc_num = cuc_num
        self.is_yang_year = is_yang_year
        
    def get_current_transit(self, target_year):
        age = target_year - self.birth_year + 1
        is_thuan = (self.gender == "Nam" and self.is_yang_year) or (self.gender == "Nữ" and not self.is_yang_year)
        step = 1 if is_thuan else -1
        
        if age < self.cuc_num:
            dh_idx = self.menh_idx
            dh_str = f"Chưa vào Vận (Dưới {self.cuc_num} tuổi)"
        else:
            periods = (age - self.cuc_num) // 10
            dh_idx = (self.menh_idx + periods * step) % 12
            start_age = self.cuc_num + periods * 10
            dh_str = f"Đại Vận {start_age}-{start_age+9}"
            
        offset = target_year - 1984
        target_can_idx = offset % 10
        target_zhi_idx = offset % 12
        target_can = GAN_LIST[target_can_idx]
        target_zhi = ZHI_LIST[target_zhi_idx]
        luu_nien_idx = target_zhi_idx
        luu_tu_hoa = TU_HOA_MAP.get(target_can, {})
        
        return {
            "age": age, "target_year": f"{target_can} {target_zhi} ({target_year})",
            "dai_han_idx": dh_idx, "dai_han_info": dh_str,
            "luu_nien_idx": luu_nien_idx, "luu_tu_hoa": luu_tu_hoa
        }

class SynastryEngine:
    def __init__(self, p1_data, p2_data):
        self.p1 = p1_data
        self.p2 = p2_data
        
    def evaluate_compatibility(self):
        score, details = 0, []
        nc_rel = get_thap_than(self.p1['nhat_chu'], self.p2['nhat_chu'])
        
        if nc_rel in ["Chính Ấn", "Thiên Ấn", "Tỷ Kiên", "Thực Thần"]: 
            score += 30; details.append(f"**Tương tác Nội Tâm:** Rất tốt ({self.p1['nhat_chu']} gặp {self.p2['nhat_chu']} là {nc_rel}). Dễ đồng cảm, thấu hiểu.")
        elif nc_rel in ["Chính Quan", "Thương Quan", "Chính Tài", "Thiên Tài"]:
            score += 20; details.append(f"**Tương tác Nội Tâm:** Khá ({self.p1['nhat_chu']} gặp {self.p2['nhat_chu']} là {nc_rel}). Bổ khuyết nhưng thỉnh thoảng áp đặt.")
        else:
            score += 10; details.append(f"**Tương tác Nội Tâm:** Xung khắc nhẹ ({self.p1['nhat_chu']} gặp {self.p2['nhat_chu']} là {nc_rel}). Cần nhường nhịn.")
            
        p1_dom, p2_dom = self.p1['bazi']['dominant_el'], self.p2['bazi']['dominant_el']
        p1_needs = self.p1['bazi']['dung_than'] + self.p1['bazi']['hy_than']
        p2_needs = self.p2['bazi']['dung_than'] + self.p2['bazi']['hy_than']
        p1_hates, p2_hates = self.p1['bazi']['ky_than'], self.p2['bazi']['ky_than']
        
        a_helps_b, b_helps_a = p1_dom in p2_needs, p2_dom in p1_needs
        a_hurts_b, b_hurts_a = p1_dom in p2_hates, p2_dom in p1_hates
        
        if a_helps_b and b_helps_a:
            score += 40; details.append(f"**Chuyển Giao Năng Lượng: TƯƠNG TRỢ HOÀN HẢO.** Cạnh nhau gia đạo hưng vượng.")
        elif a_helps_b:
            if b_hurts_a: score += 15; details.append(f"**Chuyển Giao Năng Lượng: HỖ TRỢ MỘT CHIỀU.** {self.p1['name']} hao tổn vì {self.p2['name']}.")
            else: score += 25; details.append(f"**Chuyển Giao Năng Lượng: {self.p1['name']} KÍCH VƯỢNG CHO {self.p2['name']}.**")
        elif b_helps_a:
            if a_hurts_b: score += 15; details.append(f"**Chuyển Giao Năng Lượng: HỖ TRỢ MỘT CHIỀU.** {self.p2['name']} hao tổn vì {self.p1['name']}.")
            else: score += 25; details.append(f"**Chuyển Giao Năng Lượng: {self.p2['name']} KÍCH VƯỢNG CHO {self.p1['name']}.**")
        else:
            score += 15; details.append(f"**Chuyển Giao Năng Lượng: ĐỘC LẬP TÀI VẬN.**")
            
        chi1, chi2 = self.p1['chi_year'], self.p2['chi_year']
        luc_hop, tam_hop = [{"Tý", "Sửu"}, {"Dần", "Hợi"}, {"Mão", "Tuất"}, {"Thìn", "Dậu"}, {"Tỵ", "Thân"}, {"Ngọ", "Mùi"}], [{"Thân", "Tý", "Thìn"}, {"Dần", "Ngọ", "Tuất"}, {"Hợi", "Mão", "Mùi"}, {"Tỵ", "Dậu", "Sửu"}]
        luc_xung, luc_hai = [{"Tý", "Ngọ"}, {"Sửu", "Mùi"}, {"Dần", "Thân"}, {"Mão", "Dậu"}, {"Thìn", "Tuất"}, {"Tỵ", "Hợi"}], [{"Tý", "Mùi"}, {"Sửu", "Ngọ"}, {"Dần", "Tỵ"}, {"Mão", "Thìn"}, {"Thân", "Hợi"}, {"Dậu", "Tuất"}]
        
        pair = {chi1, chi2}
        if len(pair) == 1: chi_rel, chi_score, chi_desc = "Đồng Vị", 20, "Có nét tương đồng."
        elif pair in luc_hop: chi_rel, chi_score, chi_desc = "Lục Hợp", 30, "Gắn kết tốt."
        elif any(pair.issubset(g) for g in tam_hop): chi_rel, chi_score, chi_desc = "Tam Hợp", 30, "Đồng điệu."
        elif pair in luc_xung: chi_rel, chi_score, chi_desc = "Lục Xung", 0, "Dễ va chạm."
        elif pair in luc_hai: chi_rel, chi_score, chi_desc = "Lục Hại", 5, "Dễ sinh mâu thuẫn ngầm."
        else: chi_rel, chi_score, chi_desc = "Bình Hòa", 15, "Không xung đột."
            
        details.append(f"**Góc nhìn bên ngoài (Tuổi):** {chi1} và {chi2} là **{chi_rel}**. {chi_desc}")
        score += chi_score
        
        if score >= 80: rating = "RẤT TỐT (Tri kỷ / Đối tác vàng)"
        elif score >= 60: rating = "KHÁ TỐT (Hòa hợp, ít sóng gió)"
        elif score >= 40: rating = "TRUNG BÌNH (Cần bao dung, nhường nhịn)"
        else: rating = "XUNG KHẮC (Cần hóa giải)"
        return score, rating, details

class GroupSynastryEngine:
    def __init__(self, members):
        self.members = members
        
    def evaluate_group(self):
        details = []
        if len(self.members) < 3: return details
            
        total_scores = {"Mộc": 0, "Hỏa": 0, "Thổ": 0, "Kim": 0, "Thủy": 0}
        for m in self.members:
            for el, val in m['bazi']['percentages'].items(): total_scores[el] += val

        total_sum = sum(total_scores.values()) or 1
        avg_percentages = {k: round((v/total_sum)*100, 1) for k, v in total_scores.items()}
        sorted_els = sorted(avg_percentages.items(), key=lambda x: x[1], reverse=True)
        dom_el, weak_el = sorted_els[0][0], sorted_els[-1][0]
        
        details.append("### 1. Bức tranh Ngũ Hành Tổng Thể Gia Đình")
        details.append(f"- **Tỷ lệ trung bình toàn gia:** {' | '.join([f'{k}: {v}%' for k, v in sorted_els])}")
        details.append(f"- **Khí trường:** Năng lượng **{dom_el}** chiếm chủ đạo. Điểm khuyết lớn nhất là **{weak_el}** (Cần bổ sung qua phong thủy/màu sắc).")

        details.append("### 2. Chuỗi Tương Tác (Luồng Sinh Khí)")
        for m1 in self.members:
            helps = [m2['name'] for m2 in self.members if m1['name'] != m2['name'] and m1['bazi']['dominant_el'] in (m2['bazi']['dung_than'] + m2['bazi']['hy_than'])]
            if helps: details.append(f"- **{m1['name']}** (vượng {m1['bazi']['dominant_el']}) hỗ trợ sinh khí cho: **{', '.join(helps)}**.")
            else: details.append(f"- **{m1['name']}** mang khí trường độc lập.")

        details.append("### 3. Cấu Trúc Nội Tâm Toàn Gia")
        nc_counts = {}
        for m in self.members: 
            nc_el = ELEMENTS.get(m['nhat_chu'], 'Unknown')
            nc_counts[nc_el] = nc_counts.get(nc_el, 0) + 1
        details.append(f"- **Phân bổ:** {' - '.join([f'Mệnh {k} ({v} người)' for k, v in nc_counts.items()])}")
        return details

# ==========================================
# PHẦN 3: GIAO DIỆN STREAMLIT
# ==========================================

st.set_page_config(page_title="Lá Số Gia Đạo Chuyên Sâu", layout="wide")

st.title("🌟 Phần Mềm Xem Tử vi made by MinhMup")
st.markdown("Nhập thông tin các thành viên trong gia đình để xem lá số chi tiết và ma trận tương hợp (Synastry).")

with st.sidebar:
    st.header("Thiết lập")
    num_members = st.number_input("Số lượng thành viên", min_value=1, max_value=10, value=1)
    current_year = st.number_input("Năm muốn xem vận hạn", value=2026)

members_input = []
for i in range(num_members):
    with st.expander(f"👤 Thành viên {i+1}", expanded=True):
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2,1,1,1,1,1,1.5])
        name = col1.text_input("Tên gọi", key=f"n_{i}", value=f"Người {i+1}")
        gender = col2.selectbox("Giới Tính", ["Nam", "Nữ"], key=f"g_{i}")
        y = col3.number_input("Năm sinh", 1900, 2100, 1990, key=f"y_{i}")
        m = col4.number_input("Tháng", 1, 12, 1, key=f"m_{i}")
        d = col5.number_input("Ngày", 1, 31, 1, key=f"d_{i}")
        h = col6.number_input("Giờ", 0, 23, 12, key=f"h_{i}")
        is_solar = col7.checkbox("Lịch Dương", True, key=f"s_{i}")
        
        if name.strip():
            members_input.append({
                "name": name, "gender": gender, "y": int(y), "m": int(m), "d": int(d), "h": int(h), "is_solar": is_solar
            })

# --- HÀM VẼ LÁ SỐ TỬ VI HTML ---
def render_tuvi_html(palaces, menh_idx, tuan_idx, triet_idx, dh_dict, ts_dict, tu_hoa_year_goc, thien_ban_html):
    def get_cell_html(idx):
        cung = CUNG_NAMES[(idx - menh_idx) % 12]
        tt = ""
        if idx in tuan_idx and idx in triet_idx: tt = "<br/><span style='color:purple;font-weight:bold'>[TUẦN-TRIỆT]</span>"
        elif idx in tuan_idx: tt = "<br/><span style='color:purple;font-weight:bold'>[TUẦN]</span>"
        elif idx in triet_idx: tt = "<br/><span style='color:purple;font-weight:bold'>[TRIỆT]</span>"

        main_stars = []
        for s in palaces[idx]["main"]:
            base_s = s.split(" (")[0]
            if base_s in tu_hoa_year_goc: main_stars.append(f"{s} (H.{tu_hoa_year_goc[base_s]})")
            else: main_stars.append(s)
            
        main_str = "<br/>".join(main_stars) if main_stars else "Vô Chính Diệu"
        minor_str = " ".join(palaces[idx]["minor"])
        bad_str = " ".join(palaces[idx]["bad"])
        ring_str = " - ".join(palaces[idx]["ring"])
        
        xung_idx, hop1_idx, hop2_idx = (idx + 6) % 12, (idx + 4) % 12, (idx + 8) % 12
        duong_cheo = f"C:{ZHI_LIST[xung_idx]} | H:{ZHI_LIST[hop1_idx]},{ZHI_LIST[hop2_idx]}"

        return f"""
        <div style='height: 100%; display: flex; flex-direction: column; justify-content: space-between;'>
            <div style='text-align:center; font-weight:bold; font-size:14px; margin-bottom:5px;'>{cung}{tt}</div>
            <div style='text-align:center; font-weight:bold; color:darkred; font-size:13px; margin-bottom:5px;'>{main_str}</div>
            <div style='text-align:center; color:darkgreen; font-size:11px;'>{minor_str}</div>
            <div style='text-align:center; color:black; font-size:11px;'>{bad_str}</div>
            <div style='text-align:center; color:dimgray; font-size:10px; margin-top:5px;'>{ring_str}</div>
            <div style='text-align:center; color:gray; font-size:9px; margin-top:5px;'><i>{duong_cheo}</i></div>
            <div style='text-align:center; font-weight:bold; color:mediumblue; font-size:12px; margin-top:10px;'>
                [{dh_dict[idx]}] - {ts_dict[idx]} - {ZHI_LIST[idx]}
            </div>
        </div>
        """

    html = f"""
    <table style='width:100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px;'>
        <tr>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(5)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(6)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(7)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(8)}</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(4)}</td>
            <td colspan='2' rowspan='2' style='border:1px solid #ccc; background-color:#f8f9fa; vertical-align:middle; text-align:center; padding:20px;'>{thien_ban_html}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(9)}</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(3)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(10)}</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(2)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(1)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(0)}</td>
            <td style='border:1px solid #ccc; padding:10px; height:200px; vertical-align:top;'>{get_cell_html(11)}</td>
        </tr>
    </table>
    """
    return html


# --- THỰC THI CHÍNH ---
if st.button("🔮 BẮT ĐẦU PHÂN TÍCH LÁ SỐ", type="primary"):
    if not members_input:
        st.warning("Vui lòng nhập ít nhất 1 thành viên hợp lệ!")
    else:
        processed_members = []
        
        for member in members_input:
            st.markdown(f"## 📌 LÁ SỐ: {member['name'].upper()} ({member['gender']})")
            
            # Tính toán Lịch
            if member["is_solar"]:
                solar = Solar.fromYmdHms(member["y"], member["m"], member["d"], member["h"], 0, 0)
                lunar = solar.getLunar()
            else:
                lunar = Lunar.fromYmdHms(member["y"], member["m"], member["d"], member["h"], 0, 0)
                solar = lunar.getSolar()
                
            st.info(f"**Dương Lịch:** {solar.getYear()}-{solar.getMonth():02d}-{solar.getDay():02d} {member['h']}h | **Âm Lịch:** Ngày {lunar.getDay()} Tháng {abs(lunar.getMonth())} Năm {lunar.getYear()}")

            # Bát Tự
            bt = lunar.getEightChar()
            gans = [TRANSLATE.get(x, x) for x in [bt.getYearGan(), bt.getMonthGan(), bt.getDayGan(), bt.getTimeGan()]]
            zhis = [TRANSLATE.get(x, x) for x in [bt.getYearZhi(), bt.getMonthZhi(), bt.getDayZhi(), bt.getTimeZhi()]]
            nhat_chu = gans[2]
            nc_element = ELEMENTS.get(nhat_chu, "Mộc")
            is_yang_year = YIN_YANG.get(gans[0], True)

            scorer = BaziScorer(gans, zhis)
            bazi_res = scorer.get_analysis()

            # Tử Vi
            palaces, menh_idx, cuc_name, cuc_num = build_tuvi_palaces(lunar, member["gender"], gans, zhis)
            tuan_idx, triet_idx = get_tuan_triet(gans[0], zhis[0])
            ts_dict, dh_dict = place_trang_sinh_dai_han(cuc_num, member["gender"], is_yang_year, menh_idx)

            tuvi_engine = TuviRuleEngine(palaces, menh_idx, tuan_idx, triet_idx)
            cach_cuc_info = tuvi_engine.evaluate_menh()

            transit = TransitEngine(member["y"], member["gender"], menh_idx, cuc_num, is_yang_year)
            limit_data = transit.get_current_transit(current_year)
            
            tu_hoa_year_goc = TU_HOA_MAP.get(gans[0], {})
            
            processed_members.append({
                "name": member['name'], "nhat_chu": nhat_chu, "chi_year": zhis[0], 
                "bazi": bazi_res, "limit": limit_data
            })

            # 1. Vẽ Bảng Tứ Trụ
            st.subheader("I. BẢNG TỨ TRỤ (BÁT TỰ)")
            t_gods, h_stems = [], []
            for i in range(4):
                h_stems.append("\n".join(HIDDEN_STEMS.get(zhis[i], [])))
                t_gods.append("NHẬT CHỦ" if i==2 else get_thap_than(nhat_chu, gans[i]))
            
            df_bazi = pd.DataFrame({
                "Trụ": ["Thập Thần", "Thiên Can", "Địa Chi", "Tàng Can"],
                "NĂM": [t_gods[0], gans[0], zhis[0], h_stems[0].replace("\n", ", ")],
                "THÁNG": [t_gods[1], gans[1], zhis[1], h_stems[1].replace("\n", ", ")],
                "NGÀY": [t_gods[2], gans[2], zhis[2], h_stems[2].replace("\n", ", ")],
                "GIỜ": [t_gods[3], gans[3], zhis[3], h_stems[3].replace("\n", ", ")]
            })
            st.table(df_bazi)

            # 2. Vẽ Lá Số Tử Vi
            st.subheader("II. LÁ SỐ TỬ VI ĐẨU SỐ")
            thien_ban = f"""
            <div style='font-size:20px; font-weight:bold; color:darkred; margin-bottom:10px;'>{member['name'].upper()}</div>
            <div style='font-size:14px;'><b>Năm sinh:</b> {gans[0]} {zhis[0]}</div>
            <div style='font-size:14px;'><b>Bản Mệnh:</b> Can {GAN_LIST[(GAN_LIST.index(gans[0])%5)*2]} Chi {ZHI_LIST[menh_idx]}</div>
            <div style='font-size:14px;'><b>Cục:</b> {cuc_name}</div><br/>
            <div style='font-size:14px;'><b>Nhật Chủ Bát Tự:</b> {nhat_chu} ({nc_element})</div>
            """
            st.markdown(render_tuvi_html(palaces, menh_idx, tuan_idx, triet_idx, dh_dict, ts_dict, tu_hoa_year_goc, thien_ban), unsafe_allow_html=True)

            # 3. Luận giải Ngũ Hành
            st.subheader("III. PHÂN TÍCH NGŨ HÀNH & DỤNG THẦN")
            perc_str = " | ".join([f"{k}: {v}%" for k, v in bazi_res['percentages'].items()])
            st.markdown(f"- **Tỷ lệ:** {perc_str}")
            st.markdown(f"- **Trạng thái:** {bazi_res['status']}")
            if bazi_res.get('dieu_hau_msg'):
                st.markdown(f"- **Góc nhìn Chuyên gia (Điều Hậu):** *{bazi_res['dieu_hau_msg']}*")
            st.markdown(f"- **Dụng Thần (Khuyên dùng):** <span style='color:blue;font-weight:bold'>{', '.join(bazi_res['dung_than'])}</span> | **Kỵ Thần (Né tránh):** <span style='color:red;font-weight:bold'>{', '.join(bazi_res['ky_than'])}</span>", unsafe_allow_html=True)

            # 4. Luận Giải Tính Cách & Nghề Nghiệp
            st.subheader("IV. TÍNH CÁCH & NGHỀ NGHIỆP")
            st.markdown(f"- **Tử Vi (Thế Mệnh):** {cach_cuc_info}")
            st.markdown(f"- **Bát Tự ({nhat_chu} - {nc_element}):** {TINH_CACH_MAP.get(nc_element, '')}")
            base_cach = check_cach_cuc_thau_can(gans, zhis, nhat_chu).split(' Cách')[0].replace('Giả ', '')
            st.markdown(f"- **Nghề nghiệp ({base_cach}):** {NGHE_NGHIEP_MAP.get(base_cach, 'Cân nhắc định hướng đa dạng.')}")

            # 5. Vận Hạn Năm
            st.subheader(f"V. VẬN HẠN NĂM {current_year}")
            st.markdown(f"- **Đại Vận:** {limit_data['dai_han_info']} (Cư cung {ZHI_LIST[limit_data['dai_han_idx']]})")
            st.markdown(f"- **Lưu Niên:** Năm {limit_data['target_year']} cư cung {ZHI_LIST[limit_data['luu_nien_idx']]}")
            
            for star_goc, hoa_goc in tu_hoa_year_goc.items():
                for star_luu, hoa_luu in limit_data['luu_tu_hoa'].items():
                    if star_goc == star_luu and hoa_goc == hoa_luu:
                        msg = f"⚠️ TRÙNG {hoa_goc} TẠI SAO {star_goc}!"
                        if hoa_goc == "Kỵ": st.error(f"{msg} (Hạn nặng về thị phi, cản trở)")
                        elif hoa_goc == "Lộc": st.success(f"{msg} (Cơ hội tài lộc nhân đôi, bùng nổ)")
            st.divider()

        # 6. Tương Hợp Gia Đình
        if len(processed_members) > 1:
            st.header("🤝 MA TRẬN TƯƠNG HỢP GIA ĐÌNH (1-1)")
            for p1, p2 in list(itertools.combinations(processed_members, 2)):
                syn_engine = SynastryEngine(p1, p2)
                score, rating, logs = syn_engine.evaluate_compatibility()
                
                with st.expander(f"Giao thoa: {p1['name']} ↔ {p2['name']} (Điểm: {score}/100)", expanded=True):
                    st.markdown(f"**Chỉ số Tương hợp: {score}/100 - {rating}**")
                    for line in logs: st.markdown("- " + line)

        if len(processed_members) >= 3:
            st.header("🏠 MA TRẬN NĂNG LƯỢNG TOÀN GIA (GROUP)")
            group_engine = GroupSynastryEngine(processed_members)
            group_logs = group_engine.evaluate_group()

            for line in group_logs: st.markdown(line)
