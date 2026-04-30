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
    "Lộc": {
        "Mệnh": "Hóa Lộc chiếu Mệnh là đại cát. Bản thân có duyên tài lộc, tính tình hào phóng, cuộc đời ít thiếu thốn. Quý nhân phù trợ nhiều, gặp hung dễ hóa cát. Nếu Lộc đồng thời tọa Lộc Tồn thì phú quý song toàn.",
        "Huynh Đệ": "Anh chị em hòa thuận, có tình nghĩa về tài chính. Hay được anh em giúp đỡ tiền bạc, hoặc chính mình hào phóng với anh em. Cung này sinh Tài Bạch — anh em là trợ lực làm ăn.",
        "Phu Thê": "Hôn phối có duyên phận sâu nặng, vợ/chồng mang lại tài lộc và an vui. Cuộc hôn nhân ổn định, ít cãi vã. Nếu Lộc nhập Phu Thê mà đối cung Quan Lộc vô sát, sự nghiệp đôi nhờ hôn nhân mà thăng.",
        "Tử Tức": "Con cái hiếu thảo, mang phúc về nhà. Dễ có con, hoặc con cái thành đạt hơn cha mẹ. Cung Tử Tức Hóa Lộc còn ám chỉ người có phúc đức về tình cảm, dễ được lòng cấp dưới.",
        "Tài Bạch": "Cực kỳ thuận lợi về tài chính. Tiền vào nhiều đường, tài lộc chảy về không ngừng. Nếu Lộc Tồn đồng cung thì thành 'Song Lộc' — phú quý cực độ. Thích hợp kinh doanh, đầu tư.",
        "Tật Ách": "Lộc nhập Tật Ách mang ý nghĩa giải hung — cơ thể khỏe mạnh, tuổi thọ cao. Khi gặp bệnh cũng mau bình phục, hay gặp thầy thuốc giỏi. Sức đề kháng tốt, ít ốm vặt.",
        "Thiên Di": "Ra ngoài hay gặp quý nhân, bôn ba đất khách dễ phát tài. Thích hợp công việc liên quan xuất ngoại, giao thương quốc tế. Đi xa tốt hơn ở nhà.",
        "Nô Bộc": "Bạn bè, đồng nghiệp, cấp dưới đắc lực và trung thành. Dễ thu hút người tài phò trợ. Kinh doanh có nhân sự tốt, ít bị phản bội.",
        "Quan Lộc": "Công danh sự nghiệp hanh thông, được cấp trên tin dùng. Kinh doanh thuận lợi, hay thăng chức. Nếu Văn Xương/Văn Khúc đồng cung thì danh tiếng tốt trong giới chuyên môn.",
        "Điền Trạch": "Nhà cửa đất đai tốt, dễ tích lũy bất động sản. Môi trường sống êm ấm, gia đạo hòa thuận. Cha mẹ để lại tài sản hoặc tự mình tạo lập được nơi ở tử tế.",
        "Phúc Đức": "Hưởng phúc tổ tiên, tâm tính lạc quan, ít âu lo. Tinh thần thoải mái, hay có trực giác tốt. Phúc báu nhiều đời chiếu rọi.",
        "Phụ Mẫu": "Cha mẹ yêu thương, cưng chiều và hỗ trợ tài chính. Hay được bề trên nâng đỡ, giấy tờ hành chính ít trắc trở. Phúc ấm từ cha mẹ dày."
    },
    "Quyền": {
        "Mệnh": "Hóa Quyền chiếu Mệnh — bản thân có uy quyền, cá tính mạnh, năng lực lãnh đạo xuất sắc. Tham vọng cao, không chịu đứng sau người khác. Dễ thành công trong các lĩnh vực đòi hỏi quyết đoán, quản lý.",
        "Huynh Đệ": "Anh chị em có cá tính mạnh, dễ lấn lướt hoặc tranh giành. Cần khéo léo trong ứng xử với anh em. Tuy nhiên nếu biết phân công, anh em là đội ngũ chiến đấu mạnh.",
        "Phu Thê": "Vợ/chồng tài giỏi, có bản lĩnh nhưng dễ áp đặt trong hôn nhân. Hai người đều mạnh ý kiến, cần học cách nhường nhịn. Hôn nhân kiểu 'hai thủ lĩnh' — hào hứng nhưng dễ va chạm.",
        "Tử Tức": "Con cái bướng bỉnh, có ý chí và cá tính riêng. Không dễ uốn nắn nhưng khi lớn dễ thành đạt. Người có Quyền ở Tử Tức cần kiên nhẫn giáo dục con theo hướng tôn trọng tự do.",
        "Tài Bạch": "Thích nắm quyền về tài chính, giỏi quản lý tiền bạc. Kiếm tiền chủ động, không thích bị chi phối. Tiềm năng tài chính lớn nếu không bị Kỵ xung phá.",
        "Tật Ách": "Sức khỏe tốt, thể lực mạnh mẽ, ý chí kiên cường. Khi ốm bệnh có khả năng hồi phục nhanh chóng. Quyền ở Tật Ách — tinh thần thắng thể xác.",
        "Thiên Di": "Ra ngoài có uy thế, dễ làm chủ tình huống. Thích hợp làm lãnh đạo trong công việc đối ngoại, kinh doanh xa nhà. Bôn ba phương xa mà lập nghiệp.",
        "Nô Bộc": "Có khả năng thu phục nhân tài, cấp dưới phục tùng. Tuy nhiên cần tránh độc đoán với người xung quanh. Quản lý nhân sự tốt nhờ uy quyền.",
        "Quan Lộc": "Sự nghiệp thăng tiến nhanh, dễ lên vị trí lãnh đạo. Có thực quyền hơn hư danh. Rất phù hợp con đường chính trị, quản lý nhà nước, hoặc làm chủ doanh nghiệp.",
        "Điền Trạch": "Có tài quản lý và mở rộng tài sản bất động sản. Nhà đất thường tăng giá sau khi mua. Tuy nhiên cung nhà đất Quyền — dễ tranh chấp nếu có sát tinh đồng cung.",
        "Phúc Đức": "Ý chí mạnh mẽ, thích kiểm soát cuộc sống của mình. Tâm tư phức tạp, hay có những toan tính sâu xa. Phúc báu thiên về ý chí và nghị lực hơn là hưởng thụ.",
        "Phụ Mẫu": "Cha mẹ nghiêm khắc, có uy quyền hoặc địa vị xã hội. Được cha mẹ kỳ vọng cao. Quan hệ với cấp trên, cơ quan nhà nước mang tính chủ động."
    },
    "Khoa": {
        "Mệnh": "Hóa Khoa chiếu Mệnh — thanh nhã, hiếu học, danh tiếng tốt. Là ngôi sao giải thần, mang lại danh dự và học vấn. Dù gặp hung tinh, Khoa hay hóa giải phần nào. Cuộc đời được tiếng thơm, ít kẻ thù.",
        "Huynh Đệ": "Anh chị em hiền lành, có học thức, ứng xử lịch sự. Tình cảm anh em nhẹ nhàng ít xung đột. Có thể được anh em đứng ra bảo lãnh danh tiếng.",
        "Phu Thê": "Vợ/chồng cư xử nho nhã, có học thức. Hôn nhân nên duyên nhờ trí tuệ tương đồng. Ít cãi lộn, giải quyết mâu thuẫn bằng lý lẽ. Tuy nhiên Khoa đôi khi thiếu nồng nhiệt — cần vun đắp cảm xúc.",
        "Tử Tức": "Con cái thông minh, học giỏi, có xu hướng theo con đường học thuật. Dễ đỗ đạt thi cử. Con là niềm tự hào của gia đình về mặt học vấn.",
        "Tài Bạch": "Kiếm tiền bằng tài năng và danh tiếng, không thích con đường tắt. Thu nhập từ công việc chuyên môn, tư vấn, giảng dạy. Tài chính ổn định và minh bạch.",
        "Tật Ách": "Khoa nhập Tật Ách — gặp hung hóa cát trong bệnh tật. Khi ốm hay gặp được thầy thuốc giỏi, điều trị đúng hướng. Sức khỏe tổng thể ổn định.",
        "Thiên Di": "Ra ngoài được người đời kính trọng, giữ được tiếng thơm nơi xa xứ. Công việc liên quan đến giáo dục, tư vấn quốc tế mang lại danh tiếng.",
        "Nô Bộc": "Bạn bè, cộng sự tử tế, có học thức và đức hạnh. Dễ kết bạn với người danh giá. Cấp dưới trung thực, làm việc minh bạch.",
        "Quan Lộc": "Công danh thiên về học thuật, nghiên cứu, chuyên gia. Danh tiếng trong nghề nghiệp tốt. Được đánh giá cao về chuyên môn hơn là quyền lực.",
        "Điền Trạch": "Môi trường sống yên tĩnh, trí thức. Nhà cửa sạch sẽ, có không khí học hành. Dễ mua được nhà đất qua con đường chính thống, giấy tờ minh bạch.",
        "Phúc Đức": "Tâm hồn thanh cao, an lạc nội tâm. Hưởng phúc qua đường học vấn và trí tuệ. Hay có trực giác tinh tế, tâm linh nhạy cảm.",
        "Phụ Mẫu": "Cha mẹ có học thức, cư xử lịch sự. Quan hệ với cấp trên êm đẹp, được bề trên tin tưởng về đạo đức và tài năng."
    },
    "Kỵ": {
        "Mệnh": "Hóa Kỵ tại Mệnh — cuộc đời nhiều thăng trầm, hay gặp chướng ngại không lường trước. Tính hay lo âu, cầu toàn dễ sinh phiền não. Cần nhận thức rõ điểm yếu để hóa giải. Nếu gặp Hóa Lộc đối xung thì giảm bớt hung.",
        "Huynh Đệ": "Anh chị em dễ bất hòa, có thể tranh chấp tiền bạc hoặc quan điểm. Tình anh em lạnh nhạt hoặc xa cách. Cẩn thận bảo lãnh tài chính cho anh em.",
        "Phu Thê": "Tình duyên trắc trở, hôn nhân dễ có sóng gió. Vợ/chồng hay hiểu lầm nhau, hoặc một trong hai mang nỗi khổ riêng. Cần kiên nhẫn và bao dung để giữ hôn nhân bền vững.",
        "Tử Tức": "Muộn con hoặc phiền lòng vì con cái. Con cái dễ gặp khó khăn trong học tập hoặc sức khỏe. Nên chú ý chăm sóc con từ nhỏ. Đôi khi Kỵ ở Tử Tức ám chỉ hao tổn vì con.",
        "Tài Bạch": "Dòng tiền hay tắc nghẽn, tiền vào rồi lại ra. Dễ bị mất tiền do sơ suất, lừa đảo hoặc đầu tư sai. Cẩn thận ký kết hợp đồng tài chính. Không nên làm bảo lãnh tài chính cho người khác.",
        "Tật Ách": "Dễ mắc bệnh mãn tính hoặc tai nạn bất ngờ. Sức đề kháng yếu, cần chú trọng sức khỏe định kỳ. Kỵ tại Tật Ách là một trong những dấu hiệu cần cẩn thận nhất về thể chất.",
        "Thiên Di": "Ra ngoài dễ gặp thị phi, thất bại nơi xa xứ. Đi đường dễ gặp tai nạn, nên cẩn thận phương tiện. Bôn ba không thuận, ở nhà tốt hơn ra ngoài.",
        "Nô Bộc": "Dễ bị bạn bè, cấp dưới phản trắc hoặc lợi dụng. Cần cẩn thận chọn lọc người hợp tác. Mối quan hệ xã hội dễ trở thành gánh nặng.",
        "Quan Lộc": "Công việc lận đận, hay gặp cản trở trong sự nghiệp. Dễ bị oan uổng, hiểu lầm trong môi trường công sở. Kinh doanh dễ gặp rủi ro pháp lý. Cần chọn nghề phù hợp tránh cạnh tranh khốc liệt.",
        "Điền Trạch": "Rắc rối giấy tờ nhà đất, dễ bị tranh chấp hoặc hỏng hóc bất ngờ. Nơi ở không ổn định, hay dọn nhà. Cẩn thận khi ký hợp đồng mua bán bất động sản.",
        "Phúc Đức": "Hay bồn chồn lo âu không lý do. Tâm thần dễ bất an, hay có suy nghĩ tiêu cực. Cần tu tâm tích đức để hóa giải. Đời sống tâm linh dễ bị nhiễu loạn.",
        "Phụ Mẫu": "Dễ khắc khẩu với cha mẹ hoặc bề trên. Quan hệ với cơ quan nhà nước dễ trục trặc giấy tờ. Cha mẹ hoặc người thân lớn tuổi hay gặp vấn đề sức khỏe."
    }
}

TINH_CACH_MAP = {
    "Mộc": "**Nhân ái, ngay thẳng, có chí tiến thủ.** Người Mộc thường có tấm lòng rộng lượng, trọng nhân nghĩa và tình cảm. Thẳng thắn đến mức đôi khi thiếu khéo léo. Khi Mộc Vượng: sáng tạo, lãnh đạo tốt, đa tài. Khi Mộc Nhược: thiếu kiên định, dễ nản lòng. Khi Mộc quá vượng không có Kim chế: cố chấp, bảo thủ, khó nghe lời khuyên. Mộc người hay suy nghĩ dài hạn, giỏi lập kế hoạch.",
    "Hỏa": "**Nhiệt tình, sáng tạo, trọng lễ, năng động.** Người Hỏa có sức hút tự nhiên, dễ lôi cuốn người khác. Tính tình bốc đồng, cả thèm chóng chán nếu Hỏa vượng thiếu Thủy điều tiết. Khi Hỏa Vượng: lãnh đạo xuất sắc, rực rỡ trong nghệ thuật và trình diễn. Khi Hỏa Nhược: thiếu tự tin, dễ bị tác động bởi ý kiến người khác. Người Hỏa thường sống vì hiện tại, hành động nhanh nhưng đôi khi thiếu kiên nhẫn.",
    "Thổ": "**Trầm ổn, đáng tin cậy, bao dung, trọng tín nghĩa.** Người Thổ làm việc chắc chắn, uy tín cao trong cộng đồng. Khi Thổ Vượng: trở thành trụ cột gia đình và xã hội, khéo kết giao. Khi Thổ Nhược: thiếu chính kiến, dễ bị người khác lợi dụng. Khi Thổ quá dày đặc: bảo thủ, trì trệ, khó thay đổi. Người Thổ hay coi trọng sự ổn định hơn cơ hội mạo hiểm.",
    "Kim": "**Sắc sảo, quyết đoán, trọng nghĩa khí, kiên cường.** Người Kim có bản lĩnh rõ ràng, không thích vòng vo. Khi Kim Vượng: tiên phong, dám nghĩ dám làm, trung thành. Khi Kim Nhược: hay do dự, dễ bị kẻ mạnh lấn át. Khi Kim quá cứng không có Hỏa luyện: cứng nhắc, ít linh hoạt, đôi khi lạnh lùng. Người Kim thường giỏi phán đoán và ra quyết định dứt khoát.",
    "Thủy": "**Linh hoạt, thông minh, đa mưu, khéo léo ứng xử.** Người Thủy như dòng chảy — biết thích nghi với mọi hoàn cảnh. Khi Thủy Vượng: trí tuệ bén nhọn, giao tiếp xuất sắc, đa tài. Khi Thủy Nhược: thiếu linh hoạt, hay cứng nhắc trong suy nghĩ. Khi Thủy tràn không có Thổ đê điều: phân tán, thiếu trọng tâm, nhiều tâm sự ít hành động. Người Thủy giỏi quan sát và đọc vị tâm lý người khác."
}

NGHE_NGHIEP_MAP = {
    "Chính Quan": "Phù hợp công chức nhà nước, hành chính, quản lý hệ thống, luật pháp, kiểm toán. Làm việc trong môi trường kỷ luật cao, tuân thủ quy tắc. Thích hợp thăng tiến theo thâm niên và quy trình chính thống.",
    "Thất Sát": "Xuất sắc trong quân đội, công an, lực lượng vũ trang, thể thao tranh đấu. Cũng phù hợp với doanh nhân mạo hiểm, nhà đầu tư tiên phong, bác sĩ phẫu thuật, thám tử. Cần môi trường có thách thức và áp lực để phát huy tối đa.",
    "Chính Ấn": "Giáo dục, giảng dạy đại học, nghiên cứu khoa học, văn phòng chính phủ, y tế công lập, tư vấn học thuật. Giỏi viết lách và truyền đạt kiến thức. Môi trường ổn định, cấu trúc rõ ràng phù hợp nhất.",
    "Thiên Ấn": "Nghệ thuật, thiết kế sáng tạo, y học cổ truyền, tâm linh, triết học, lập trình IT, nghiên cứu bí ẩn. Tư duy phi tuyến tính, giỏi giải quyết vấn đề phức tạp theo cách riêng. Làm việc tự do hoặc nghiên cứu độc lập phù hợp.",
    "Chính Tài": "Tài chính, ngân hàng, kế toán, kinh doanh có kế hoạch, quản lý tài sản. Giỏi tích lũy từng bước, ít mạo hiểm. Phù hợp đầu tư dài hạn, bất động sản ổn định, quản lý quỹ.",
    "Thiên Tài": "Đầu tư mạo hiểm, kinh doanh đa ngành, bán hàng, marketing, môi giới. Giỏi nắm bắt cơ hội tức thời. Lợi nhuận đột phá nhưng rủi ro cao. Phù hợp startup, kinh doanh theo cảm quan thị trường.",
    "Thực Thần": "Sư phạm, tư vấn tâm lý, ẩm thực, phúc lợi xã hội, nuôi dưỡng, y tế cộng đồng. Tính tình ôn hòa, hay giúp đỡ người khác. Làm việc mang lại phúc lợi cho cộng đồng mang lại nhiều thỏa mãn.",
    "Thương Quan": "Nghệ thuật biểu diễn, diễn thuyết, truyền thông, marketing sáng tạo, luật sư tranh tụng, nhà văn, nhà báo. Tư duy phản biện sắc bén, không ngại thách thức chuẩn mực. Cần không gian sáng tạo tự do.",
    "Tỷ Kiên": "Tự lập kinh doanh, làm chủ doanh nghiệp gia đình, hợp tác cùng bạn bè đồng trang lứa. Môi trường bình đẳng, ít thứ bậc phù hợp. Giỏi đoàn kết nhóm khi có mục tiêu chung.",
    "Kiếp Tài": "Thể thao chuyên nghiệp, cạnh tranh thương mại, môi giới, đấu thầu, bán hàng trực tiếp. Thích thử thách và cạnh tranh. Cần kiềm chế tính bốc đồng để tránh thua lỗ do quyết định vội vàng."
}

# ==========================================
# TỪ ĐIỂN LUẬN GIẢI CHÍNH TINH TỬ VI
# ==========================================

CHINH_TINH_LUAN_GIAI = {
    "Tử Vi": {
        "B": "Tử Vi Miếu — vua sao ở vị trí tối thượng. Khí vượng tự chủ, có tài lãnh đạo bẩm sinh, được quý nhân trọng vọng. Cuộc đời thường có bước ngoặt thăng hoa rõ rệt.",
        "V": "Tử Vi Vượng — uy quyền dồi dào, khả năng tổ chức và điều hành tốt. Được người khác nể phục, dễ thành công trong môi trường nhiều quyết định.",
        "M": "Tử Vi Bình — tài năng có nhưng cần điều kiện phát huy. Ý chí quyết tâm là chìa khóa. Cần tránh kiêu ngạo.",
        "Đ": "Tử Vi Hãm — uy lực kém phát huy. Dễ bị cô lập hoặc quyền uy không thực chất. Cần khiêm tốn học hỏi."
    },
    "Thiên Cơ": {
        "B": "Thiên Cơ Miếu — trí tuệ mẫn tiệp, linh hoạt ứng biến xuất sắc. Sở trường phân tích, tham mưu, quyền biến. Học gì cũng nhanh.",
        "V": "Thiên Cơ Vượng — thông minh lanh lợi, giỏi thích nghi. Tư duy chiến lược tốt. Thích hợp công việc đòi hỏi trí não hơn thể lực.",
        "M": "Thiên Cơ Bình — thông minh nhưng hay lăn tăn. Suy nghĩ nhiều đôi khi làm chậm hành động. Cần quyết đoán hơn.",
        "H": "Thiên Cơ Hãm — tài trí không phát huy được, dễ tính toán sai. Cẩn thận kẻ tiểu nhân lợi dụng trí tuệ."
    },
    "Thái Dương": {
        "M": "Thái Dương Miếu (Dần-Mão-Thìn) — mặt trời buổi sáng, quang minh chính đại. Tài năng tỏa sáng, được công nhận rộng rãi. Đặc biệt tốt cho nam giới.",
        "V": "Thái Dương Vượng — nhiệt huyết, hào phóng, có tầm ảnh hưởng trong cộng đồng. Danh tiếng tốt.",
        "B": "Thái Dương Bình — ánh sáng vừa đủ. Thành công vừa phải, cần nỗ lực không ngừng.",
        "H": "Thái Dương Hãm (Thân-Dậu-Tuất-Hợi) — mặt trời lặn. Tài năng bị che khuất. Dễ lao lực mà ít được ghi nhận. Nữ giới gặp Thái Dương Hãm ở Mệnh — chồng hay gặp trắc trở.",
        "Đ": "Thái Dương Đắc Địa — tương tự Vượng, phát huy tốt trong môi trường phù hợp."
    },
    "Vũ Khúc": {
        "V": "Vũ Khúc Vượng — sao tài bạch mạnh nhất. Cứng rắn, quyết đoán, tự lực cánh sinh. Kiếm tiền bằng chính tài năng và nỗ lực.",
        "M": "Vũ Khúc Bình — tài lực trung bình, cần kiên trì tích lũy. Tính cách hơi cứng nhắc.",
        "B": "Vũ Khúc Miếu — tài năng tài chính xuất sắc, cứng rắn như kim loại. Quyết đoán, không sợ khó khăn.",
        "Đ": "Vũ Khúc Đắc — tiền tài tốt nhưng hay đơn độc. Cần mềm mỏng hơn trong quan hệ."
    },
    "Thiên Đồng": {
        "V": "Thiên Đồng Vượng — phúc thọ, hưởng thụ, cuộc đời bình yên êm ả. Không thích cạnh tranh khốc liệt.",
        "M": "Thiên Đồng Bình — phúc đức vừa phải. Tính tình lười biếng đôi chút nếu không có sao động lực.",
        "H": "Thiên Đồng Hãm — phúc bị hao mòn. Dễ trì trệ, thiếu động lực phấn đấu. Cần Sát Tinh kích thích.",
        "B": "Thiên Đồng Miếu — phúc thọ dồi dào, tâm tính lạc quan hồn nhiên.",
        "Đ": "Thiên Đồng Đắc — có phúc nhưng hay ỷ lại."
    },
    "Liêm Trinh": {
        "B": "Liêm Trinh Miếu — trong sạch, đoan chính, có tài năng thực sự. Người nguyên tắc và đáng tin.",
        "M": "Liêm Trinh Bình — tài năng có nhưng dễ bị thị phi vây quanh. Cẩn thận quan hệ xã hội.",
        "H": "Liêm Trinh Hãm — dễ vướng vào phong lưu, đào hoa hoặc pháp lý. Cần giữ gìn đạo đức.",
        "V": "Liêm Trinh Vượng — nghiêm túc, kỷ luật, có thành tích trong công việc.",
        "Đ": "Liêm Trinh Đắc — tương tự Miếu, tài chính và đạo đức đi đôi."
    },
    "Thiên Phủ": {
        "M": "Thiên Phủ Miếu/Bình — kho trời, người giữ tài sản. Thận trọng, tích lũy, bảo thủ theo nghĩa tốt. Gia đình ổn định, con cái đề huề.",
        "B": "Thiên Phủ Bình — năng lực tốt, tích lũy được nhưng đôi khi thiếu sáng tạo đột phá."
    },
    "Thái Âm": {
        "V": "Thái Âm Vượng — trực giác tốt, tinh tế, nhạy cảm. Tài lộc đến êm ả, không ồn ào. Đặc biệt tốt cho nữ giới.",
        "M": "Thái Âm Bình — tình cảm dạt dào nhưng dễ mộng mơ. Cần thực tế hơn.",
        "B": "Thái Âm Miếu — phú quý âm thầm, thường giàu mà không phô trương. Trực giác cực tốt.",
        "H": "Thái Âm Hãm — cảm xúc bị tổn thương, tài lộc thất thường. Nam gặp Thái Âm Hãm ở Mệnh — hay gặp khó khăn về phụ nữ.",
        "Đ": "Thái Âm Đắc — tài tình kín đáo, hay tích lũy được tài sản lặng lẽ."
    },
    "Tham Lang": {
        "V": "Tham Lang Vượng — đa tài đa năng, có sức hút mạnh. Giỏi giao tiếp và kiếm tiền theo nhiều cách.",
        "M": "Tham Lang Bình — tài năng đa dạng nhưng không chuyên sâu. Cần chọn một hướng rõ ràng.",
        "H": "Tham Lang Hãm — dễ sa vào đào hoa, cờ bạc, chất kích thích nếu không có định hướng.",
        "B": "Tham Lang Miếu — bản lĩnh mạnh mẽ, thu hút người khác, nhiều tài lẻ xuất sắc."
    },
    "Cự Môn": {
        "V": "Cự Môn Vượng — biện luận sắc bén, ăn nói thuyết phục. Thích hợp luật sư, MC, giảng dạy.",
        "M": "Cự Môn Bình — hay gặp thị phi và tranh cãi. Cần kiểm soát lời nói.",
        "H": "Cự Môn Hãm — miệng lưỡi mang họa. Dễ bị hiểu nhầm hoặc tạo mâu thuẫn không đáng. Cẩn thận lời nói.",
        "B": "Cự Môn Miếu — tài năng ngôn từ đỉnh cao. Ăn nói thuyết phục mọi người."
    },
    "Thiên Tướng": {
        "V": "Thiên Tướng Vượng — công bằng, chính trực, làm trọng tài hoặc quản lý tốt. Được tín nhiệm.",
        "M": "Thiên Tướng Bình — có khả năng quản lý nhưng đôi khi do dự.",
        "H": "Thiên Tướng Hãm — dễ bị cuốn vào tranh chấp người khác. Khó giữ trung lập.",
        "Đ": "Thiên Tướng Đắc — uy tín vừa đủ, làm cầu nối tốt giữa các bên."
    },
    "Thiên Lương": {
        "M": "Thiên Lương Miếu/Bình — ân cứu, thọ tinh. Hay cứu giúp người khác, được ơn báo đáp. Sống thọ, gặp hung hóa cát.",
        "V": "Thiên Lương Vượng — phúc thọ dày, gặp quý nhân nhiều. Thích hợp nghề y, tư vấn, từ thiện.",
        "H": "Thiên Lương Hãm — hay lo cho người khác mà quên bản thân. Phúc bị tiêu hao vì người."
    },
    "Thất Sát": {
        "M": "Thất Sát Miếu/Bình — dũng mãnh quyết đoán. Chiến đấu không ngại khó khăn. Thành công sau nhiều thử thách gian nan.",
        "V": "Thất Sát Vượng — sức mạnh và ý chí vượt trội. Lãnh đạo trong khủng hoảng.",
        "B": "Thất Sát Bình — dũng cảm có nhưng đôi khi liều lĩnh quá mức."
    },
    "Phá Quân": {
        "M": "Phá Quân Bình — phá cũ lập mới. Hay thay đổi môi trường, sự nghiệp. Sáng tạo trong phá vỡ quy tắc cũ.",
        "V": "Phá Quân Vượng — đổi mới mạnh mẽ, tiên phong. Không giỏi giữ gìn mà giỏi khai phá.",
        "H": "Phá Quân Hãm — phá hoại không xây dựng được. Dễ tự làm hỏng cơ hội của mình.",
        "B": "Phá Quân Miếu — sức mạnh đổi mới lớn, có thể lật ngược cục diện bất lợi."
    }
}

# Thần Sát quan trọng và ý nghĩa
THAN_SAT_LUAN_GIAI = {
    "Lộc Tồn": "Lộc Tồn — tài lộc cố định, giữ tiền tốt. Tuy nhiên hay ở một mình, cô đơn trong lòng dù bề ngoài đủ đầy.",
    "Kình Dương": "Kình Dương — hung tinh có tính hai mặt. Trong cung tốt: ý chí mạnh, chiến đấu kiên cường. Trong cung xấu hoặc Hãm: tai họa bất ngờ, phẫu thuật, tai nạn. Cần chính tinh tốt đi kèm.",
    "Đà La": "Đà La — hung tinh mang tính kéo lê, chậm trễ. Mọi việc hay bị trì hoãn, chướng ngại vật ngầm. Dễ bị người khác gây khó dễ từ phía sau.",
    "Địa Không": "Địa Không — tinh thần thoát tục, hay mơ mộng. Không hợp với công việc đòi hỏi kết quả vật chất. Dễ bị hao tổn tài lộc đột ngột nếu gặp Tài cung.",
    "Địa Kiếp": "Địa Kiếp — giống Địa Không nhưng hung hơn về mặt vật chất. Dễ bị mất trộm, hao tán, hoặc đầu tư thất bại bất ngờ.",
    "Hỏa Tinh": "Hỏa Tinh — bùng phát nhanh. Có thể thúc đẩy thành công nhanh chóng trong cung tốt, hoặc tai họa đột ngột trong cung xấu.",
    "Linh Tinh": "Linh Tinh — tương tự Hỏa Tinh nhưng âm ỉ hơn. Gây tổn hại chậm và khó nhận ra.",
    "Tả Phù": "Tả Phù — quý tinh, trợ thủ đắc lực từ phía tả (nam giới). Được quý nhân nam giới giúp đỡ. Trong Quan Lộc: có cấp trên hoặc đồng nghiệp hỗ trợ.",
    "Hữu Bật": "Hữu Bật — quý tinh, trợ thủ từ phía hữu (nữ giới). Được quý nhân nữ hoặc phụ nữ giúp đỡ. Có khả năng hợp tác tốt.",
    "Văn Xương": "Văn Xương — văn học tinh hoa, thi cử học vấn xuất sắc. Giỏi viết lách, học thuật, văn chương. Ở Mệnh: người có học thức, lời nói có trọng lượng.",
    "Văn Khúc": "Văn Khúc — nghệ thuật, âm nhạc, tài năng sáng tạo. Khác Văn Xương ở chỗ thiên về nghệ thuật hơn học thuật. Ở Mệnh: người tài hoa, đa năng.",
    "Thiên Khôi": "Thiên Khôi — quý nhân tinh. Được bề trên quý mến, giúp đỡ. Đặc biệt tốt khi ở Mệnh hoặc Quan Lộc. Xin việc, thi cử hay gặp may.",
    "Thiên Việt": "Thiên Việt — tương tự Thiên Khôi nhưng quý nhân đến từ phía khác (thường là nữ giới hoặc theo chiều ngang).",
    "Bác Sĩ": "Bác Sĩ — thông minh, học vấn cao. Giỏi quản lý chi tiết.",
    "Thanh Long": "Thanh Long — phát tài đột phá, cơ hội tốt.",
    "Tiểu Hao": "Tiểu Hao — hao tổn nhỏ, chi tiêu lặt vặt.",
    "Đại Hao": "Đại Hao — hao tổn lớn, cẩn thận đầu tư và chi tiêu lớn.",
    "Phi Liêm": "Phi Liêm — hay bị thị phi, tai tiếng.",
    "Bệnh Phù": "Bệnh Phù — dễ ốm đau, cần chú ý sức khỏe.",
    "Quan Phủ": "Quan Phủ — dễ gặp kiện tụng, tranh chấp pháp lý.",
    "Thái Tuế": "Thái Tuế — năm Thái Tuế chiếu cung nào thì cung đó bị xáo trộn. Cẩn thận thay đổi lớn.",
    "Tang Môn": "Tang Môn — dễ gặp buồn bã, tang sự, chia ly.",
    "Bạch Hổ": "Bạch Hổ — dễ gặp tai nạn, phẫu thuật, máu me.",
    "Điếu Khách": "Điếu Khách — dễ gặp người đau yếu, bệnh viện, tang lễ xung quanh."
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

def get_than_sat_bat_tu(gans, zhis):
    """Nhận diện Thần Sát quan trọng trong Bát Tự"""
    year_zhi, month_zhi, day_zhi, hour_zhi = zhis
    year_gan, month_gan, day_gan, hour_gan = gans
    results = []
    
    # Thiên Ất Quý Nhân (Thiên Ất Quý Nhân theo Nhật Chủ)
    quy_nhan_map = {
        "Giáp": ["Sửu", "Mùi"], "Mậu": ["Sửu", "Mùi"],
        "Ất": ["Tý", "Thân"], "Kỷ": ["Tý", "Thân"],
        "Bính": ["Hợi", "Dậu"], "Đinh": ["Hợi", "Dậu"],
        "Canh": ["Sửu", "Mùi"], "Tân": ["Ngọ", "Dần"],
        "Nhâm": ["Mão", "Tỵ"], "Quý": ["Mão", "Tỵ"]
    }
    qn_zhis = quy_nhan_map.get(day_gan, [])
    qn_found = [z for z in zhis if z in qn_zhis]
    if qn_found:
        results.append(f"✨ **Thiên Ất Quý Nhân** tại {', '.join(qn_found)}: Đây là thần sát quý nhất. Cuộc đời luôn có quý nhân phò trợ lúc khó khăn, tai nạn dễ hóa giải, bề trên tin yêu.")
    
    # Văn Xương Quý Nhân
    van_xuong_map = {"Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Thân", "Đinh": "Dậu",
                     "Mậu": "Thân", "Kỷ": "Dậu", "Canh": "Hợi", "Tân": "Tý",
                     "Nhâm": "Dần", "Quý": "Mão"}
    vx_zhi = van_xuong_map.get(day_gan)
    if vx_zhi and vx_zhi in zhis:
        pos = ["Năm", "Tháng", "Ngày", "Giờ"][zhis.index(vx_zhi)]
        results.append(f"📚 **Văn Xương Quý Nhân** tại trụ {pos}: Thiên tư thông minh, học hành dễ thành công, thi cử hay đỗ đạt. Viết lách và ngôn từ là điểm mạnh.")

    # Dịch Mã (theo Địa Chi năm hoặc ngày)
    dich_ma_map = {"Dần": "Thân", "Ngọ": "Thân", "Tuất": "Thân",
                   "Thân": "Dần", "Tý": "Dần", "Thìn": "Dần",
                   "Tỵ": "Hợi", "Dậu": "Hợi", "Sửu": "Hợi",
                   "Hợi": "Tỵ", "Mão": "Tỵ", "Mùi": "Tỵ"}
    dm_zhi = dich_ma_map.get(year_zhi)
    if dm_zhi and dm_zhi in [month_zhi, day_zhi, hour_zhi]:
        results.append(f"🚀 **Dịch Mã** xuất hiện trong lá số: Cuộc đời hay di chuyển, bôn ba. Kinh doanh, công việc liên quan đi lại, vận chuyển, xuất ngoại rất thuận lợi. Ở nhà thì tù túng, ra ngoài thì phát.")

    # Đào Hoa (theo Địa Chi năm)
    dao_hoa_map = {"Dần": "Mão", "Ngọ": "Mão", "Tuất": "Mão",
                   "Thân": "Dậu", "Tý": "Dậu", "Thìn": "Dậu",
                   "Tỵ": "Ngọ", "Dậu": "Ngọ", "Sửu": "Ngọ",
                   "Hợi": "Tý", "Mão": "Tý", "Mùi": "Tý"}
    dh_zhi = dao_hoa_map.get(year_zhi)
    if dh_zhi and dh_zhi in [month_zhi, day_zhi, hour_zhi]:
        pos = ["Tháng", "Ngày", "Giờ"][([month_zhi, day_zhi, hour_zhi]).index(dh_zhi)]
        results.append(f"🌸 **Đào Hoa** tại trụ {pos}: Có sức hút về tình cảm, duyên gặp gỡ nhiều. Đào Hoa ở trụ Ngày — cuộc hôn nhân đẹp nhưng cần đề phòng bất trắc về sau. Trụ Giờ — đào hoa muộn hoặc đào hoa ẩn.")

    # Kiếp Sát / Kiếp Tinh (theo Địa Chi năm)
    kiep_sat_map = {"Dần": "Tỵ", "Ngọ": "Dậu", "Tuất": "Sửu",
                    "Thân": "Hợi", "Tý": "Mão", "Thìn": "Mùi",
                    "Tỵ": "Dần", "Dậu": "Ngọ", "Sửu": "Tuất",
                    "Hợi": "Thân", "Mão": "Tý", "Mùi": "Thìn"}
    ks_zhi = kiep_sat_map.get(year_zhi)
    if ks_zhi and ks_zhi in [day_zhi, hour_zhi]:
        results.append(f"⚠️ **Kiếp Sát** trong lá số: Dễ gặp tai họa bất ngờ, mất mát do rủi ro ngoài ý muốn. Cẩn thận khi tham gia các hoạt động có nguy cơ cao (đi xe, thể thao mạo hiểm).")

    # Hợp trong tứ trụ
    luc_hop_pairs = [("Tý", "Sửu"), ("Dần", "Hợi"), ("Mão", "Tuất"), ("Thìn", "Dậu"), ("Tỵ", "Thân"), ("Ngọ", "Mùi")]
    for z1, z2 in luc_hop_pairs:
        positions = []
        for pos_name, z in zip(["Năm","Tháng","Ngày","Giờ"], zhis):
            if z == z1 or z == z2:
                positions.append(pos_name)
        if len(positions) >= 2 and z1 in zhis and z2 in zhis:
            results.append(f"🤝 **Lục Hợp {z1}-{z2}** giữa trụ {positions[0]} và {positions[1]}: Hợp lực tốt, hai trụ này nâng đỡ nhau. Mang ý nghĩa hòa hợp và phát triển trong lĩnh vực tương ứng.")

    # Xung trong tứ trụ
    luc_xung_pairs = [("Tý", "Ngọ"), ("Sửu", "Mùi"), ("Dần", "Thân"), ("Mão", "Dậu"), ("Thìn", "Tuất"), ("Tỵ", "Hợi")]
    for z1, z2 in luc_xung_pairs:
        if z1 in zhis and z2 in zhis:
            p1 = ["Năm","Tháng","Ngày","Giờ"][zhis.index(z1)]
            p2 = ["Năm","Tháng","Ngày","Giờ"][zhis.index(z2)]
            results.append(f"💥 **Xung {z1}-{z2}** giữa trụ {p1} và {p2}: Hai trụ xung khắc nhau. Cuộc đời dễ biến động mạnh trong giai đoạn liên quan. Cần chú ý sức khỏe và quan hệ tương ứng với hai trụ đó.")
    
    # Tam Hợp cục
    tam_hop_groups = [("Thân", "Tý", "Thìn"), ("Dần", "Ngọ", "Tuất"), ("Hợi", "Mão", "Mùi"), ("Tỵ", "Dậu", "Sửu")]
    for group in tam_hop_groups:
        found = [z for z in group if z in zhis]
        if len(found) == 3:
            results.append(f"🌟 **Tam Hợp Cục {'-'.join(group)}** đầy đủ: Đây là cách cục đặc biệt quý. Năng lượng ngũ hành {ZHI_ELEMENTS[group[1]]} cực vượng, sự nghiệp và tài lộc phát đạt theo hướng {ZHI_ELEMENTS[group[1]]}.")
        elif len(found) == 2:
            results.append(f"🔗 **Bán Tam Hợp {'-'.join(found)}**: Có tiềm năng phát triển tốt, cần đại vận hoặc lưu niên kích thêm chi còn lại để phát huy trọn vẹn.")

    if not results:
        results.append("Không phát hiện Thần Sát đặc biệt nổi bật trong tứ trụ. Cục diện bình ổn.")
    
    return results


def analyze_thap_than_detail(gans, zhis, nhat_chu):
    """Phân tích chi tiết thập thần và ý nghĩa thực tế"""
    results = []
    nc_el = ELEMENTS.get(nhat_chu, "")
    
    than_labels = ["NĂM", "THÁNG", "GIỜ"]
    other_gans = [gans[0], gans[1], gans[3]]
    
    tt_counts = {}
    for g in other_gans:
        tt = get_thap_than(nhat_chu, g)
        if tt:
            tt_counts[tt] = tt_counts.get(tt, 0) + 1
    
    # Phân tích tổ hợp thập thần nổi bật
    dominant_tt = sorted(tt_counts.items(), key=lambda x: x[1], reverse=True)
    
    if dominant_tt:
        top_tt, count = dominant_tt[0]
        if count >= 2:
            results.append(f"**Thập Thần nổi trội: {top_tt} (xuất hiện {count} lần)**")
        
        if "Thương Quan" in tt_counts:
            results.append("🎭 **Thương Quan** hiện diện: Tư duy sáng tạo, không chịu bị ràng buộc. Rất giỏi trong nghệ thuật và truyền thông. Tuy nhiên Thương Quan khắc Quan — cẩn thận quan hệ với cấp trên và trong hôn nhân (đặc biệt nữ giới).")
        
        if "Kiếp Tài" in tt_counts:
            results.append("⚔️ **Kiếp Tài** hiện diện: Tính cạnh tranh cao, hay chia sẻ tài sản ngoài ý muốn. Cẩn thận hợp tác kinh doanh và bảo lãnh tài chính.")
        
        if "Thiên Ấn" in tt_counts and "Thực Thần" not in tt_counts:
            results.append("🔮 **Thiên Ấn** (Chánh Ấn) mạnh: Trực giác tốt, có tài năng thiên phú. Nhưng nếu thiếu Thực/Thương để cân bằng — dễ lười biếng hoặc ỷ lại vào người khác.")
        
        if "Chính Quan" in tt_counts and "Chính Ấn" in tt_counts:
            results.append("🏛️ **Quan Ấn tương sinh**: Danh tiếng và quyền lực đi đôi với học vấn. Cách cục này rất thuận lợi cho con đường công danh và quản lý nhà nước.")
        
        if "Chính Tài" in tt_counts and "Chính Ấn" in tt_counts:
            results.append("💰 **Tài Ấn đồng lộ**: Tài chính và học vấn cùng xuất hiện. Thường thể hiện người vừa giỏi kiếm tiền vừa có học thức. Cẩn thận Tài phá Ấn nếu Tài quá mạnh.")

    # Phân tích trụ Nhật (ngày) — cung Phu Thê ẩn
    day_zhi = zhis[2]
    phu_the_hidden = HIDDEN_STEMS.get(day_zhi, [])
    if phu_the_hidden:
        phu_the_tt = get_thap_than(nhat_chu, phu_the_hidden[0])
        phu_the_desc = {
            "Chính Tài": "người yêu/vợ/chồng hiền lành, ổn định", 
            "Thiên Tài": "người yêu/vợ/chồng năng động, nhiều tiền nhưng khó nắm",
            "Chính Quan": "chồng/vợ có địa vị, nghiêm túc (tốt cho nữ)",
            "Thất Sát": "chồng/vợ mạnh mẽ nhưng dễ có manh tính áp đặt",
            "Chính Ấn": "chồng/vợ nhân từ, hay lo lắng cho đối phương",
            "Thiên Ấn": "chồng/vợ cá tính, khác thường, hay bí ẩn",
            "Thực Thần": "chồng/vợ hiền, dễ sống, hay chiều chuộng",
            "Thương Quan": "chồng/vợ tài năng nhưng khó tính, hay chỉ trích",
            "Tỷ Kiên": "chồng/vợ tính cách giống mình, dễ tranh luận",
            "Kiếp Tài": "chồng/vợ cạnh tranh, dễ tranh giành"
        }
        if phu_the_tt in phu_the_desc:
            results.append(f"💑 **Tàng Can trong trụ Ngày ({day_zhi} chứa {phu_the_hidden[0]} = {phu_the_tt})**: Ẩn trong cung Phu Thê cho thấy {phu_the_desc[phu_the_tt]}.")
    
    return results


def get_tuan_triet(year_gan, year_zhi):
    can_idx = GAN_LIST.index(year_gan) if year_gan in GAN_LIST else 0
    zhi_idx = ZHI_LIST.index(year_zhi) if year_zhi in ZHI_LIST else 0
    diff = (zhi_idx - can_idx) % 12
    tuan_1, tuan_2 = (diff - 2) % 12, (diff - 1) % 12
    triet_map = {"Giáp": (8, 9), "Kỷ": (8, 9), "Ất": (6, 7), "Canh": (6, 7), "Bính": (4, 5), "Tân": (4, 5), "Đinh": (2, 3), "Nhâm": (2, 3), "Mậu": (0, 1), "Quý": (0, 1)}
    triet_1, triet_2 = triet_map.get(year_gan, (0, 1))
    return (tuan_1, tuan_2), (triet_1, triet_2)


def luan_giai_cung_tu_vi(cung_name, main_stars_raw, bad_stars, minor_stars, tuan_triet_note, tu_hoa_menh, tu_hoa_luu_nien=None):
    """Luận giải chi tiết một cung Tử Vi"""
    lines = []

    main_stars = []
    for s in main_stars_raw:
        base = s.split(" (")[0]
        state_part = s.split("(")[1].rstrip(")") if "(" in s else ""
        state = state_part.split(")")[0] if state_part else "B"
        main_stars.append((base, state))

    if not main_stars:
        lines.append(f"**Cung {cung_name}: Vô Chính Diệu** — Tính linh hoạt, dễ thích nghi. Cung này bị ảnh hưởng nhiều bởi sao chiếu từ cung đối diện.")

    for star_name, state in main_stars:
        state_map = {"B": "Miếu (★★★★★)", "V": "Vượng (★★★★)", "M": "Bình (★★★)",
                     "H": "Hãm (★★)", "Đ": "Đắc Địa (★★★★)"}
        state_display = state_map.get(state, state)

        star_luan = CHINH_TINH_LUAN_GIAI.get(star_name, {})
        star_detail = star_luan.get(state, star_luan.get("M", f"{star_name} ở trạng thái {state}."))
        lines.append(f"**{star_name} {state_display}** — {star_detail}")

        if star_name in tu_hoa_menh:
            hoa_type = tu_hoa_menh[star_name]
            hoa_detail = TU_HOA_LUAN_GIAI.get(hoa_type, {}).get(cung_name, "")
            lines.append(f"  → *Hóa {hoa_type} Bản Mệnh*: {hoa_detail}")

        if tu_hoa_luu_nien and star_name in tu_hoa_luu_nien:
            hoa_type_ln = tu_hoa_luu_nien[star_name]
            hoa_detail_ln = TU_HOA_LUAN_GIAI.get(hoa_type_ln, {}).get(cung_name, "")
            lines.append(f"  → *Hóa {hoa_type_ln} Lưu Niên*: {hoa_detail_ln}")

    if minor_stars:
        minor_notes = []
        for s in minor_stars:
            note = THAN_SAT_LUAN_GIAI.get(s, "")
            if note:
                minor_notes.append(f"**{s}**: {note.split('—')[1].strip() if '—' in note else note}")
            else:
                minor_notes.append(s)
        if minor_notes:
            lines.append(f"  *Phụ tinh*: {' | '.join(minor_notes)}")

    if bad_stars:
        bad_notes = []
        for s in bad_stars:
            note = THAN_SAT_LUAN_GIAI.get(s, "")
            if note:
                bad_notes.append(f"**{s}**: {note.split('—')[1].strip() if '—' in note else note}")
            else:
                bad_notes.append(s)
        if bad_notes:
            lines.append(f"  *Sát tinh cần lưu ý*: {' | '.join(bad_notes)}")

    if tuan_triet_note:
        lines.append(f"  ⚠️ {tuan_triet_note}: Sức mạnh sao bị suy giảm đáng kể. Cần nỗ lực gấp đôi để đạt kết quả bình thường trong lĩnh vực này.")

    return lines


def analyze_transit_detail(palaces, menh_idx, dai_han_idx, luu_nien_idx, tu_hoa_menh, luu_tu_hoa, current_year, dai_han_str):
    """Phân tích chi tiết vận hạn năm"""
    lines = []

    dh_cung = CUNG_NAMES[(dai_han_idx - menh_idx) % 12]
    dh_stars = [s.split(" (")[0] for s in palaces[dai_han_idx]["main"]]
    dh_bad = palaces[dai_han_idx]["bad"]

    lines.append(f"### 🔵 Đại Vận: {dai_han_str}")
    lines.append(f"Đại Hạn đang đi qua **cung {dh_cung}** ({ZHI_LIST[dai_han_idx]}).")

    cung_y_nghia = {
        "Mệnh": "Đại hạn chính cung Mệnh — giai đoạn cực kỳ quan trọng, toàn bộ vận mệnh bùng nổ hoặc thách thức lớn.",
        "Quan Lộc": "Đại hạn tốt cho sự nghiệp, thăng tiến, cơ hội nghề nghiệp dồi dào.",
        "Tài Bạch": "Đại hạn tài lộc — giai đoạn kiếm tiền thuận lợi, dễ tích lũy.",
        "Phu Thê": "Đại hạn hôn nhân — dễ lập gia đình hoặc sóng gió hôn nhân tùy sao.",
        "Tử Tức": "Đại hạn con cái và sáng tạo — sinh con, hoặc phát triển dự án mới.",
        "Điền Trạch": "Đại hạn nhà đất — mua sắm bất động sản hoặc thay đổi nơi ở.",
        "Thiên Di": "Đại hạn di chuyển — đi xa, xuất ngoại, thay đổi môi trường lớn.",
        "Tật Ách": "Đại hạn cần chú ý sức khỏe đặc biệt. Cũng là giai đoạn tự soi lại bản thân.",
        "Phúc Đức": "Đại hạn tâm linh và hưởng thụ — giai đoạn nội tâm phong phú.",
        "Phụ Mẫu": "Đại hạn liên quan cha mẹ và học vấn. Tốt cho học hành, thi cử.",
        "Nô Bộc": "Đại hạn bạn bè, đối tác — hợp tác và mạng lưới quan hệ là chìa khóa.",
        "Huynh Đệ": "Đại hạn anh em, đồng nghiệp — cạnh tranh và đoàn kết cùng lúc."
    }
    lines.append(cung_y_nghia.get(dh_cung, ""))

    if dh_stars:
        lines.append(f"Chính tinh đại hạn: **{', '.join(dh_stars)}**")
    if dh_bad:
        lines.append(f"⚠️ Cung đại hạn có sát tinh **{', '.join(dh_bad)}** — cần cẩn thận các rủi ro liên quan.")

    lines.append(f"\n### 🟡 Lưu Niên {current_year}")
    ln_cung = CUNG_NAMES[(luu_nien_idx - menh_idx) % 12]
    ln_stars = [s.split(" (")[0] for s in palaces[luu_nien_idx]["main"]]
    ln_bad = palaces[luu_nien_idx]["bad"]

    lines.append(f"Lưu Niên chiếu **cung {ln_cung}** ({ZHI_LIST[luu_nien_idx]}).")
    lines.append(cung_y_nghia.get(ln_cung, ""))
    if ln_stars:
        lines.append(f"Sao trong cung lưu niên: **{', '.join(ln_stars)}**")
    if ln_bad:
        lines.append(f"⚠️ Lưu niên có sát tinh **{', '.join(ln_bad)}** — đây là điểm cần chú ý trong năm.")

    if luu_tu_hoa:
        lines.append(f"\n### 🔴 Tứ Hóa Lưu Niên {current_year}")
        for star, hoa in luu_tu_hoa.items():
            for idx in range(12):
                cung_stars = [s.split(" (")[0] for s in palaces[idx]["main"]]
                if star in cung_stars:
                    cung_of_star = CUNG_NAMES[(idx - menh_idx) % 12]
                    hoa_detail = TU_HOA_LUAN_GIAI.get(hoa, {}).get(cung_of_star, f"Hóa {hoa} ảnh hưởng cung {cung_of_star}.")
                    lines.append(f"**{star} Hóa {hoa}** (tại cung {cung_of_star}): {hoa_detail}")
                    break

    if dai_han_idx == luu_nien_idx:
        lines.append(f"\n⚡ **ĐẠI HẠN - LƯU NIÊN ĐỒNG CUNG** ({dh_cung}): Hiệu ứng nhân đôi! Mọi việc liên quan đến cung {dh_cung} được khuếch đại gấp bội năm nay.")

    for star_goc, hoa_goc in tu_hoa_menh.items():
        for star_luu, hoa_luu in luu_tu_hoa.items():
            if star_goc == star_luu:
                if hoa_goc == hoa_luu:
                    if hoa_goc == "Kỵ":
                        lines.append(f"\n🚨 **TRÙNG KỴ sao {star_goc}**: Bản mệnh Kỵ gặp Lưu Niên Kỵ — năm cực kỳ cần cẩn thận. Thị phi, hao tổn tài chính, sức khỏe đều có thể bị ảnh hưởng nghiêm trọng.")
                    elif hoa_goc == "Lộc":
                        lines.append(f"\n🎉 **TRÙNG LỘC sao {star_goc}**: Bản mệnh Lộc gặp Lưu Niên Lộc — tài lộc nhân đôi, năm đặc biệt thuận lợi!")
                elif hoa_goc == "Lộc" and hoa_luu == "Kỵ":
                    lines.append(f"\n⚠️ **Lộc-Kỵ xung chiếu tại {star_goc}**: Tiền có vào nhưng hay bị cản trở, tiêu hao đột ngột.")
                elif hoa_goc == "Kỵ" and hoa_luu == "Lộc":
                    lines.append(f"\n💡 **Kỵ được Lộc hóa giải tại {star_goc}**: Năm nay Lộc lưu niên chiếu vào Kỵ bản mệnh — phần nào hóa giải hung khí.")

    return lines


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
        KHUNG_GIO = [
            ("Tý",   "23:00 – 00:59", 23),
            ("Sửu",  "01:00 – 02:59",  1),
            ("Dần",  "03:00 – 04:59",  3),
            ("Mão",  "05:00 – 06:59",  5),
            ("Thìn", "07:00 – 08:59",  7),
            ("Tỵ",   "09:00 – 10:59",  9),
            ("Ngọ",  "11:00 – 12:59", 11),
            ("Mùi",  "13:00 – 14:59", 13),
            ("Thân", "15:00 – 16:59", 15),
            ("Dậu",  "17:00 – 18:59", 17),
            ("Tuất", "19:00 – 20:59", 19),
            ("Hợi",  "21:00 – 22:59", 21),
        ]
        KHUNG_GIO_LABELS = [f"Giờ {chi}  ({span})" for chi, span, _ in KHUNG_GIO]

        col1, col2, col3, col4, col5, col7 = st.columns([2,1,1,1,1,1.5])
        name     = col1.text_input("Tên gọi", key=f"n_{i}", value=f"Người {i+1}")
        gender   = col2.selectbox("Giới Tính", ["Nam", "Nữ"], key=f"g_{i}")
        y        = col3.number_input("Năm sinh", 1900, 2100, 1990, key=f"y_{i}")
        m        = col4.number_input("Tháng", 1, 12, 1, key=f"m_{i}")
        d        = col5.number_input("Ngày", 1, 31, 1, key=f"d_{i}")
        is_solar = col7.checkbox("Lịch Dương", True, key=f"s_{i}")

        gio_idx = st.selectbox(
            "⏰ Giờ sinh (chọn khung giờ)",
            options=list(range(12)),
            format_func=lambda x: KHUNG_GIO_LABELS[x],
            index=6,
            key=f"gio_{i}",
            help="Ví dụ sinh lúc 3h30 → chọn Giờ Dần (03:00–04:59)"
        )
        h = KHUNG_GIO[gio_idx][2]
        
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
            st.markdown(f"- **Tỷ lệ ngũ hành:** {perc_str}")
            st.markdown(f"- **Trạng thái Nhật Chủ:** {bazi_res['status']}")
            if bazi_res.get('dieu_hau_msg'):
                st.info(f"🌡️ **Điều Hậu Dụng Thần:** {bazi_res['dieu_hau_msg']}")
            
            dung_str = ', '.join([f"**{x}**" for x in bazi_res['dung_than']]) if bazi_res['dung_than'] else "Đang xác định"
            hy_str = ', '.join(bazi_res['hy_than']) if bazi_res['hy_than'] else "—"
            ky_str = ', '.join([f"**{x}**" for x in bazi_res['ky_than']]) if bazi_res['ky_than'] else "—"
            st.markdown(f"- 🔵 **Dụng Thần** (cần bổ sung, màu sắc, hướng nhà): {dung_str}")
            st.markdown(f"- 🟢 **Hỷ Thần** (hỗ trợ, ưu tiên): {hy_str}")
            st.markdown(f"- 🔴 **Kỵ Thần** (nên tránh): {ky_str}")
            
            # Hướng dẫn thực tế theo Dụng Thần
            el_color = {"Mộc": "xanh lá, xanh lam | Hướng Đông", "Hỏa": "đỏ, cam, tím | Hướng Nam",
                        "Thổ": "vàng, nâu, be | Hướng Trung tâm", "Kim": "trắng, bạc, xám | Hướng Tây",
                        "Thủy": "đen, navy, xanh đậm | Hướng Bắc"}
            if bazi_res['dung_than']:
                dt = bazi_res['dung_than'][0]
                st.markdown(f"- 💡 **Gợi ý màu sắc/hướng nhà theo Dụng Thần {dt}:** {el_color.get(dt, '')}")

            # 3b. Thần Sát Bát Tự
            st.subheader("IIIb. THẦN SÁT & TỔ HỢP ĐẶC BIỆT TRONG TỨ TRỤ")
            than_sat_list = get_than_sat_bat_tu(gans, zhis)
            for ts in than_sat_list:
                st.markdown(f"- {ts}")
            
            # 3c. Phân tích thập thần chuyên sâu
            st.subheader("IIIc. PHÂN TÍCH THẬP THẦN CHUYÊN SÂU")
            tt_analysis = analyze_thap_than_detail(gans, zhis, nhat_chu)
            for line in tt_analysis:
                st.markdown(f"- {line}")
            
            cach_cuc_full = check_cach_cuc_thau_can(gans, zhis, nhat_chu)
            st.markdown(f"- **Cách Cục Thấu Can:** `{cach_cuc_full}`")

            # 4. Luận Giải Tính Cách & Nghề Nghiệp
            st.subheader("IV. TÍNH CÁCH & NGHỀ NGHIỆP")
            st.markdown(f"#### Phân tích Tính Cách Nhật Chủ {nhat_chu} ({nc_element})")
            st.markdown(TINH_CACH_MAP.get(nc_element, ''))
            
            st.markdown(f"#### Cách Cục Tử Vi: Thế Mệnh")
            st.info(cach_cuc_info)
            
            base_cach = check_cach_cuc_thau_can(gans, zhis, nhat_chu).split(' Cách')[0].replace('Giả ', '')
            nghe_nghiep_detail = NGHE_NGHIEP_MAP.get(base_cach, 'Cân nhắc định hướng đa dạng — cần xem xét toàn cục.')
            st.markdown(f"#### Định Hướng Nghề Nghiệp (Cách: {base_cach})")
            st.markdown(nghe_nghiep_detail)

            # 4b. Luận giải từng cung chính Tử Vi
            st.subheader("IVb. LUẬN GIẢI CUNG MỆNH VÀ CÁC CUNG QUAN TRỌNG")
            important_cung_offsets = {
                "Mệnh": 0, "Quan Lộc": 4, "Tài Bạch": 8, "Phu Thê": 6,
                "Phúc Đức": 2, "Thiên Di": 7, "Tử Tức": 9, "Tật Ách": 10
            }
            for cung_disp, offset in important_cung_offsets.items():
                idx = (menh_idx + offset) % 12
                tuan_note = ""
                if idx in tuan_idx and idx in triet_idx: tuan_note = "Bị Tuần VÀ Triệt"
                elif idx in tuan_idx: tuan_note = "Bị Tuần Không"
                elif idx in triet_idx: tuan_note = "Bị Triệt Không"
                
                with st.expander(f"🔍 Cung {cung_disp} ({ZHI_LIST[idx]}) — {'sao: ' + ', '.join([s.split(' (')[0] for s in palaces[idx]['main']]) if palaces[idx]['main'] else 'Vô Chính Diệu'}", expanded=(cung_disp == "Mệnh")):
                    detail_lines = luan_giai_cung_tu_vi(
                        cung_disp,
                        palaces[idx]["main"],
                        palaces[idx]["bad"],
                        palaces[idx]["minor"],
                        tuan_note,
                        tu_hoa_year_goc,
                        limit_data['luu_tu_hoa']
                    )
                    for dl in detail_lines:
                        st.markdown(dl)

            # 5. Vận Hạn Năm
            st.subheader(f"V. VẬN HẠN NĂM {current_year} — PHÂN TÍCH CHUYÊN SÂU")
            transit_lines = analyze_transit_detail(
                palaces, menh_idx,
                limit_data['dai_han_idx'], limit_data['luu_nien_idx'],
                tu_hoa_year_goc, limit_data['luu_tu_hoa'],
                current_year, limit_data['dai_han_info']
            )
            for line in transit_lines:
                st.markdown(line)
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
