"""Kịch bản tạo 100 Bộ thẻ (Decks), ~400 Thẻ (Cards), 100 Đề thi (Quizzes),
~400 Câu hỏi (Questions), kèm Lượt thi mẫu (Attempts & Answers) chất lượng cao.

- 50 Deck & Quiz đầu: Chủ đề Tiếng Anh (English: Oxford 3000, Idioms, Phrasal Verbs, IELTS, TOEIC, Grammar).
- 50 Deck & Quiz sau: Chủ đề Công nghệ thông tin, DSA, Python, OS, Networks, AI, Toán học, Khoa học.
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# -----------------------------------------------------------------------------
# Dữ liệu nguồn 100 Chủ đề (50 Tiếng Anh, 50 Công nghệ / Khoa học)
# -----------------------------------------------------------------------------

RAW_DATA = [
    # --- 1-10: Oxford 3000 Từ vựng Đời sống & Giao tiếp ---
    {
        "title": "Oxford 3000: Daily Routines",
        "description": "Từ vựng tiếng Anh thông dụng về thói quen sinh hoạt và nhịp sống hàng ngày.",
        "cards": [
            ("Commute", "Đi lại hàng ngày giữa nơi ở và nơi làm việc bằng phương tiện giao thông."),
            ("Errand", "Chuyến đi ngắn để làm một việc vặt hoặc nhiệm vụ cụ thể (mua sắm, gửi đồ)."),
            ("Chore", "Công việc vặt định kỳ trong gia đình như dọn dẹp, rửa bát, giặt giũ."),
            ("Punctual", "Đúng giờ, không bao giờ chậm trễ so với thời gian đã hẹn trước."),
        ],
        "quiz": [
            ("Từ nào diễn tả việc đi lại đều đặn mỗi ngày giữa nhà và nơi làm việc?", "Commute", "Errand", "Vacation", "Stroll", "A"),
            ("Một chuyến đi nhanh ra ngoài để giải quyết việc cá nhân gọi là gì?", "Holiday", "Errand", "Chore", "Flight", "B"),
            ("Tính từ nào mang ý nghĩa luôn xuất hiện đúng giờ hẹn?", "Punctual", "Reluctant", "Tardy", "Careless", "A"),
            ("Từ nào chỉ những công việc lặp lại nhàm chán trong nhà (rửa bát, lau nhà)?", "Adventure", "Hobby", "Chore", "Mission", "C"),
        ],
    },
    {
        "title": "Oxford 3000: Family & Relationships",
        "description": "Từ vựng tiếng Anh về mối quan hệ gia đình, bạn bè và tương tác xã hội.",
        "cards": [
            ("Sibling", "Anh, chị hoặc em ruột trong cùng một gia đình."),
            ("Acquaintance", "Người quen biết sơ qua nhưng chưa phải là bạn bè thân thiết."),
            ("Kinship", "Mối quan hệ họ hàng huyết thống hoặc sự gắn kết gia tộc sâu sắc."),
            ("Upbringing", "Sự nuôi dưỡng và giáo dục một đứa trẻ trong suốt thời niên thiếu."),
        ],
        "quiz": [
            ("Từ 'Sibling' trong tiếng Anh dùng để chỉ đối tượng nào?", "Bố mẹ", "Anh chị em ruột", "Họ hàng xa", "Bạn cùng lớp", "B"),
            ("Một người bạn quen mặt nhưng chưa thân gọi là gì?", "Colleague", "Spouse", "Acquaintance", "Soulmate", "C"),
            ("Từ nào mô tả sự giáo dưỡng, dạy dỗ của cha mẹ đối với con cái từ nhỏ?", "Upbringing", "Heritage", "Adolescence", "Kinship", "A"),
            ("'Kinship' thể hiện điều gì?", "Tình bạn bè", "Quan hệ huyết thống/gia tộc", "Hợp đồng kinh doanh", "Cạnh tranh công việc", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Food & Culinary Arts",
        "description": "Từ vựng về ẩm thực, nguyên liệu và các phương pháp chế biến món ăn.",
        "cards": [
            ("Appetizer", "Món khai vị nhẹ nhàng phục vụ trước bữa ăn chính để kích thích vị giác."),
            ("Seasoning", "Gia vị hoặc hương liệu thêm vào món ăn để tăng thêm hương vị đậm đà."),
            ("Nutritious", "Chứa nhiều chất dinh dưỡng có lợi cho sự phát triển và sức khỏe."),
            ("Beverage", "Đồ uống các loại (trừ nước lọc nguyên chất thông thường)."),
        ],
        "quiz": [
            ("Món ăn khai vị phục vụ đầu bữa tiệc được gọi là gì?", "Dessert", "Beverage", "Appetizer", "Entree", "C"),
            ("Muối, tiêu, thảo mộc dùng để nêm nếm món ăn được xếp vào nhóm nào?", "Seasoning", "Appetizer", "Utensil", "Nutrient", "A"),
            ("Từ nào chỉ chung các loại thức uống (trà, cà phê, nước trái cây)?", "Beverage", "Cuisine", "Course", "Snack", "A"),
            ("Thực phẩm giàu vitamin và khoáng chất tốt cho sức khỏe có tính chất gì?", "Harmful", "Nutritious", "Bland", "Stale", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Travel & Aviation",
        "description": "Từ vựng chuyên dùng khi đi du lịch, tại sân bay và di chuyển quốc tế.",
        "cards": [
            ("Itinerary", "Lịch trình chi tiết về các địa điểm, thời gian và hoạt động của chuyến đi."),
            ("Boarding pass", "Thẻ lên máy bay do hãng hàng không cấp sau khi hành khách làm thủ tục."),
            ("Jet lag", "Cảm giác mệt mỏi, rối loạn nhịp sinh học do bay qua nhiều múi giờ khác nhau."),
            ("Layover", "Khoảng thời gian dừng quá cảnh ngắn giữa hai chặng của chuyến bay dài."),
        ],
        "quiz": [
            ("Bản kế hoạch ghi rõ lộ trình và các điểm dừng chân trong chuyến đi gọi là gì?", "Receipt", "Itinerary", "Passport", "Brochure", "B"),
            ("Hành khách cần xuất trình giấy tờ gì tại cửa khởi hành máy bay?", "Driver license", "Boarding pass", "Credit card", "Luggage tag", "B"),
            ("Triệu chứng mệt mỏi sau chuyến bay dài vượt nhiều múi giờ gọi là gì?", "Homesick", "Seasick", "Jet lag", "Headache", "C"),
            ("Khoảng thời gian chờ nối chuyến tại sân bay trung gian gọi là gì?", "Takeoff", "Layover", "Check-in", "Turbulence", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Shopping & Personal Finance",
        "description": "Từ vựng mua sắm, quản lý ngân sách cá nhân và giao dịch thương mại.",
        "cards": [
            ("Bargain", "Món đồ mua được với giá hời, rẻ hơn nhiều so với giá trị thực tế."),
            ("Receipt", "Biên lai hoặc hóa đơn bằng giấy/điện tử chứng nhận đã thanh toán tiền."),
            ("Installment", "Khoản tiền trả góp định kỳ hàng tháng khi mua hàng có giá trị cao."),
            ("Affordable", "Có giá cả phải chăng, vừa vặn với túi tiền và khả năng chi trả."),
        ],
        "quiz": [
            ("Khi mua được một món hàng chất lượng tốt với giá rất rẻ, ta gọi đó là gì?", "Rip-off", "Bargain", "Deficit", "Debt", "B"),
            ("Giấy tờ chứng minh bạn đã hoàn tất thanh toán tại quầy thu ngân là gì?", "Coupon", "Warranty", "Receipt", "Catalog", "C"),
            ("Hình thức trả tiền mua hàng chia nhỏ thành nhiều tháng gọi là gì?", "Lump sum", "Installment", "Cash advance", "Mortgage", "B"),
            ("Sản phẩm có mức giá hợp lý và nằm trong khả năng tài chính gọi là gì?", "Extravagant", "Priceless", "Affordable", "Costly", "C"),
        ],
    },
    {
        "title": "Oxford 3000: Weather & Meteorology",
        "description": "Từ vựng miêu tả hiện tượng thời tiết, khí hậu và cảnh báo tự nhiên.",
        "cards": [
            ("Drizzle", "Mưa phùn hạt nhỏ li ti, rơi nhẹ nhàng và kéo dài nhiều giờ."),
            ("Humidity", "Độ ẩm trong không khí, lượng hơi nước chứa trong bầu khí quyển."),
            ("Forecast", "Bản tin dự báo tình hình thời tiết trong những ngày sắp tới."),
            ("Scorching", "Rất nóng nực, oi bức như thiêu đốt dưới ánh mặt trời gay gắt."),
        ],
        "quiz": [
            ("Cơn mưa hạt nhỏ, bay lất phất trong không gian được gọi là gì?", "Downpour", "Hail", "Drizzle", "Blizzard", "C"),
            ("Khái niệm chỉ lượng hơi nước có trong không khí là gì?", "Pressure", "Altitude", "Humidity", "Visibility", "C"),
            ("Thời tiết mùa hè với nắng gắt và nhiệt độ cực cao được miêu tả bằng từ nào?", "Freezing", "Breezy", "Scorching", "Overcast", "C"),
            ("Thông tin dự đoán thời tiết trong 24-48 giờ tới gọi là gì?", "Weather log", "Weather forecast", "Weather history", "Weather alarm", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Health & Medicine",
        "description": "Từ vựng về tình trạng thể chất, y tế cơ bản và lối sống lành mạnh.",
        "cards": [
            ("Symptom", "Triệu chứng hoặc dấu hiệu cảnh báo cơ thể đang mắc bệnh lý nào đó."),
            ("Prescription", "Đơn thuốc do bác sĩ có chuyên môn kê sau khi thăm khám bệnh nhân."),
            ("Immunity", "Hệ miễn dịch, khả năng tự chống lại các mầm bệnh và virus của cơ thể."),
            ("Diagnosis", "Kết luận chẩn đoán chính xác về căn bệnh sau quá trình xét nghiệm."),
        ],
        "quiz": [
            ("Biểu hiện sốt, ho, đau đầu khi cơ thể nhiễm bệnh được gọi là gì?", "Treatment", "Symptom", "Placebo", "Vaccine", "B"),
            ("Tờ giấy ghi danh mục thuốc do bác sĩ chỉ định dùng gọi là gì?", "Receipt", "Prescription", "Manual", "Certificate", "B"),
            ("Khả năng cơ thể tự bảo vệ trước sự xâm nhập của virus và vi khuẩn gọi là gì?", "Fatigue", "Allergy", "Immunity", "Infection", "C"),
            ("Quá trình bác sĩ xác định bệnh nhân mắc căn bệnh cụ thể nào gọi là gì?", "Diagnosis", "Prognosis", "Therapy", "Surgery", "A"),
        ],
    },
    {
        "title": "Oxford 3000: House & Living Space",
        "description": "Từ vựng về kiến trúc nhà ở, nội thất và không gian sinh hoạt gia đình.",
        "cards": [
            ("Balcony", "Ban công nhô ra ngoài tường của tầng trên có lan can bảo vệ an toàn."),
            ("Basement", "Tầng hầm của ngôi nhà nằm hoàn toàn hoặc một phần dưới mặt đất."),
            ("Appliance", "Thiết bị điện gia dụng phục vụ nhu cầu sinh hoạt (tủ lạnh, máy giặt)."),
            ("Spacious", "Rộng rãi, thoáng đãng, có nhiều không gian trống để di chuyển."),
        ],
        "quiz": [
            ("Phần tầng nhà nằm bên dưới mặt đất thường dùng để chứa đồ gọi là gì?", "Attic", "Balcony", "Basement", "Porch", "C"),
            ("Các thiết bị điện như máy giặt, lò vi sóng trong nhà được gọi chung là gì?", "Utensils", "Fixtures", "Appliances", "Tools", "C"),
            ("Một căn phòng có diện tích lớn và thoáng mát có thể miêu tả bằng từ nào?", "Cramped", "Spacious", "Narrow", "Gloomy", "B"),
            ("Khu vực ban công ngoài trời ở các tầng lầu gọi là gì?", "Terrace", "Balcony", "Basement", "Hallway", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Emotions & Personality",
        "description": "Từ vựng miêu tả cảm xúc, tính cách và phẩm chất con người.",
        "cards": [
            ("Empathetic", "Có khả năng thấu cảm và chia sẻ cảm xúc sâu sắc với người khác."),
            ("Optimistic", "Luôn lạc quan, suy nghĩ tích cực và tin tưởng vào tương lai tốt đẹp."),
            ("Diligent", "Chăm chỉ, siêng năng, làm việc có trách nhiệm và cẩn thận chu đáo."),
            ("Resilient", "Kiên cường, có khả năng phục hồi nhanh chóng sau biến cố hoặc thất bại."),
        ],
        "quiz": [
            ("Người luôn nhìn thấy mặt tích cực trong mọi hoàn cảnh được gọi là gì?", "Pessimistic", "Cynical", "Optimistic", "Indifferent", "C"),
            ("Phẩm chất kiên cường, mau chóng đứng dậy sau thất bại gọi là gì?", "Vulnerable", "Fragile", "Resilient", "Stubborn", "C"),
            ("Người biết đặt mình vào vị trí của người khác để cảm nhận được gọi là gì?", "Empathetic", "Arrogant", "Selfish", "Ruthless", "A"),
            ("Tính từ miêu tả người làm việc cần mẫn, chịu khó và kiên trì là gì?", "Lazy", "Diligent", "Hasty", "Passive", "B"),
        ],
    },
    {
        "title": "Oxford 3000: Hobbies & Leisure",
        "description": "Từ vựng về sở thích cá nhân, hoạt động giải trí và thư giãn.",
        "cards": [
            ("Pastime", "Trò tiêu khiển hoặc hoạt động giải trí yêu thích vào thời gian rảnh rỗi."),
            ("Photography", "Nghệ thuật nhiếp ảnh, chụp và xử lý những bức ảnh nghệ thuật."),
            ("Recreation", "Hoạt động tái tạo năng lượng, nghỉ ngơi thư giãn sau giờ làm việc."),
            ("Enthusiast", "Người đam mê, say mê cuồng nhiệt một môn thể thao hoặc sở thích nào đó."),
        ],
        "quiz": [
            ("Hoạt động làm vào thời gian rảnh rỗi để giải trí gọi là gì?", "Pastime", "Duty", "Chore", "Obligation", "A"),
            ("Người có niềm đam mê đặc biệt sâu sắc với một lĩnh vực nào đó gọi là gì?", "Amateur", "Enthusiast", "Spectator", "Critic", "B"),
            ("Nghệ thuật chụp ảnh và ghi lại khoảnh khắc bằng máy ảnh gọi là gì?", "Pottery", "Sculpture", "Photography", "Calligraphy", "C"),
            ("Từ 'Recreation' đồng nghĩa gần nhất với khái niệm nào sau đây?", "Labor", "Exhaustion", "Relaxation", "Discipline", "C"),
        ],
    },

    # --- 11-20: Idioms & Phrasal Verbs thông dụng ---
    {
        "title": "Phrasal Verbs with 'Get'",
        "description": "Các cụm động từ quan trọng nhất đi với 'Get' trong giao tiếp tiếng Anh.",
        "cards": [
            ("Get along with", "Có mối quan hệ hòa hợp, thân thiện với một ai đó."),
            ("Get over", "Vượt qua cú sốc, hồi phục sau khi ốm đau hoặc chuyện buồn tình cảm."),
            ("Get by", "Xoay xở sống qua ngày với lượng tiền bạc hoặc tài nguyên ít ỏi."),
            ("Get away with", "Thoát tội, làm điều sai trái mà không bị phát hiện hay xử phạt."),
        ],
        "quiz": [
            ("Cụm từ nào mang nghĩa 'hòa thuận, hợp tính với ai đó'?", "Get out of", "Get along with", "Get down to", "Get behind", "B"),
            ("Khi bạn hồi phục sau một cơn bạo bệnh hoặc chia tay, bạn đã làm gì?", "Get through", "Get over", "Get off", "Get up", "B"),
            ("Xoay xở sống sót trong điều kiện kinh tế khó khăn dùng cụm từ nào?", "Get by", "Get away", "Get across", "Get into", "A"),
            ("Làm điều phạm pháp nhưng không bị bắt hay trừng phạt gọi là gì?", "Get off with", "Get around", "Get away with", "Get in on", "C"),
        ],
    },
    {
        "title": "Phrasal Verbs with 'Take'",
        "description": "Các cụm động từ phổ biến nhất đi với 'Take' trong đời sống.",
        "cards": [
            ("Take off", "Máy bay cất cánh bay lên; hoặc trở nên cực kỳ thành công đột phá."),
            ("Take after", "Trông giống hoặc có tính cách tương đồng với cha mẹ/họ hàng."),
            ("Take over", "Tiếp quản quyền điều hành, kiểm soát một công ty hay vị trí công việc."),
            ("Take up", "Bắt đầu học hoặc theo đuổi một sở thích mới; chiếm dụng không gian/thời gian."),
        ],
        "quiz": [
            ("Khi máy bay rời khỏi mặt đất để bay lên không trung, động từ nào được dùng?", "Take in", "Take off", "Take away", "Take down", "B"),
            ("'She really takes after her mother' có nghĩa là gì?", "Cô ấy chăm sóc mẹ", "Cô ấy giống mẹ về ngoại hình/tính cách", "Cô ấy đuổi theo mẹ", "Cô ấy nghe lời mẹ", "B"),
            ("Một tập đoàn mua lại và nắm quyền điều hành doanh nghiệp khác gọi là gì?", "Take up", "Take down", "Take over", "Take out", "C"),
            ("Bắt đầu luyện tập một môn thể thao mới như Yoga thì dùng cụm nào?", "Take up", "Take on", "Take back", "Take off", "A"),
        ],
    },
    {
        "title": "Phrasal Verbs with 'Look'",
        "description": "Các cụm từ đi với 'Look' thường xuất hiện trong các bài thi quốc tế.",
        "cards": [
            ("Look forward to", "Háo hức, mong chờ một sự kiện sắp diễn ra trong tương lai gần."),
            ("Look into", "Điều tra, nghiên cứu hoặc kiểm tra kỹ lưỡng một vấn đề/sự cố."),
            ("Look down on", "Khinh thường, xem thường người khác vì nghĩ mình vượt trội hơn."),
            ("Look up to", "Ngưỡng mộ, tôn trọng và coi ai đó là tấm gương sáng để noi theo."),
        ],
        "quiz": [
            ("Sau cụm 'Look forward to' ta luôn dùng dạng từ nào?", "V-infinitive", "V-ing / Danh từ", "V-ed", "Bare verb", "B"),
            ("Cảnh sát đang kiểm tra nguyên nhân vụ cháy, họ đang làm gì?", "Looking after", "Looking down", "Looking into", "Looking back", "C"),
            ("Tôn trọng và ngưỡng mộ thần tượng được diễn tả bằng cụm nào?", "Look out for", "Look up to", "Look down upon", "Look away", "B"),
            ("Coi thường những người có hoàn cảnh khó khăn hơn mình là hành vi gì?", "Look up to", "Look after", "Look down on", "Look around", "C"),
        ],
    },
    {
        "title": "Phrasal Verbs with 'Put'",
        "description": "Tuyển tập cụm động từ thực tế đi với 'Put'.",
        "cards": [
            ("Put off", "Trì hoãn, dời lịch làm một công việc gì đó sang thời điểm sau."),
            ("Put up with", "Chịu đựng một tình huống khó chịu hoặc một người phiền toái."),
            ("Put out", "Dập tắt ngọn lửa hoặc đốm cháy đang bốc lên; phát hành tài liệu."),
            ("Put on", "Mặc quần áo vào người; tăng cân nặng; bật thiết bị điện tử."),
        ],
        "quiz": [
            ("'Don't put off until tomorrow what you can do today' khuyên chúng ta điều gì?", "Không nên trì hoãn", "Không nên dập lửa", "Nên mặc ấm", "Nên chịu đựng", "A"),
            ("Tôi không thể chịu đựng được tiếng ồn này nữa' tương ứng với cụm từ nào?", "Put up with", "Put across", "Put away", "Put forward", "A"),
            ("Lực lượng cứu hỏa đã dập tắt đám cháy rừng, họ đã làm gì?", "Put off the fire", "Put out the fire", "Put up the fire", "Put in the fire", "B"),
            ("Mặc áo khoác trước khi ra ngoài trời lạnh được nói là gì?", "Put down your coat", "Put on your coat", "Put up your coat", "Put off your coat", "B"),
        ],
    },
    {
        "title": "Phrasal Verbs with 'Turn'",
        "description": "Các biến thể cụm động từ thường gặp của động từ 'Turn'.",
        "cards": [
            ("Turn down", "Từ chối một lời mời/đề nghị; hoặc giảm âm lượng thiết bị."),
            ("Turn up", "Xuất hiện bất ngờ; hoặc tăng âm lượng, nhiệt độ thiết bị."),
            ("Turn out", "Hóa ra là, kết cục trở thành một kết quả bất ngờ ngoài dự kiến."),
            ("Turn into", "Biến đổi hoàn toàn từ trạng thái này sang một trạng thái khác."),
        ],
        "quiz": [
            ("Từ chối một lời đề nghị việc làm hấp dẫn dùng cụm từ nào?", "Turn in", "Turn down", "Turn over", "Turn away", "B"),
            ("Anh ấy đến bữa tiệc muộn và bất ngờ, ta có thể nói gì?", "He turned off", "He turned up", "He turned into", "He turned out", "B"),
            ("Kết quả sự việc hóa ra lại tốt đẹp ngoài mong đợi dùng cụm nào?", "Turned away", "Turned down", "Turned out", "Turned back", "C"),
            ("Nước đóng băng biến thành đá cứng là quá trình gì?", "Turns off ice", "Turns into ice", "Turns down ice", "Turns up ice", "B"),
        ],
    },
    {
        "title": "Common Business Idioms",
        "description": "Thành ngữ tiếng Anh được sử dụng phổ biến trong môi trường văn phòng và đàm phán.",
        "cards": [
            ("Cut corners", "Làm việc cẩu thả, bớt xén công đoạn để tiết kiệm tiền hoặc thời gian."),
            ("Back to the drawing board", "Bắt đầu lại kế hoạch từ con số không sau khi ý tưởng trước thất bại."),
            ("Call it a day", "Dừng công việc lại và nghỉ ngơi sau một ngày làm việc năng suất."),
            ("Think outside the box", "Tư duy sáng tạo, đột phá ngoài khuôn khổ tư duy truyền thống."),
        ],
        "quiz": [
            ("Bớt xén vật liệu xây dựng để giảm chi phí là hành vi gì trong tiếng Anh?", "Cutting corners", "Thinking outside the box", "Calling it a day", "Hitting the sack", "A"),
            ("Khi chiến dịch kinh doanh thất bại hoàn toàn và phải lập lại kế hoạch mới từ đầu:", "Back to the drawing board", "Piece of cake", "Spill the beans", "Break a leg", "A"),
            ("Đã 6 giờ tối rồi, chúng ta kết thúc công việc hôm nay thôi!", "Let's call it a day", "Let's bite the bullet", "Let's cut corners", "Let's burn bridges", "A"),
            ("Tìm kiếm giải pháp sáng tạo không đi theo lối mòn gọi là gì?", "Stay in the box", "Think outside the box", "Keep in mind", "Face the music", "B"),
        ],
    },
    {
        "title": "Food & Kitchen Idioms",
        "description": "Các thành ngữ tiếng Anh thú vị bắt nguồn từ ẩm thực và đồ ăn.",
        "cards": [
            ("Piece of cake", "Việc gì đó vô cùng dễ dàng thực hiện, dễ như ăn kẹo."),
            ("Spill the beans", "Vô tình hoặc cố ý tiết lộ bí mật cho người khác biết."),
            ("Take with a grain of salt", "Tiếp nhận thông tin với sự nghi ngờ, không nên tin 100%."),
            ("Bite off more than you can chew", "Nhận quá nhiều việc vượt quá khả năng xử lý của mình."),
        ],
        "quiz": [
            ("Bài kiểm tra hôm nay dễ đến mức ai cũng làm được điểm 10:", "A hot potato", "A piece of cake", "A bad apple", "A couch potato", "B"),
            ("Lỡ miệng tiết lộ kế hoạch tổ chức tiệc sinh nhật bí mật là gì?", "Spill the beans", "Cry over spilt milk", "Bring home the bacon", "Cool as a cucumber", "A"),
            ("Nghe tin đồn trên mạng thì nên cẩn trọng, không vội tin tuyệt đối:", "Take it with a grain of salt", "Butter someone up", "Chew the fat", "Egg someone on", "A"),
            ("Ôm đồm quá nhiều dự án cùng một lúc đến mức kiệt sức là biểu hiện của gì?", "Biting the dust", "Biting off more than you can chew", "Eating humble pie", "Having a sweet tooth", "B"),
        ],
    },
    {
        "title": "Animal Idioms in English",
        "description": "Thành ngữ tiếng Anh mượn hình ảnh các loài động vật quen thuộc.",
        "cards": [
            ("Let the cat out of the bag", "Vô ý để lộ một bí mật lẽ ra phải được giữ kín."),
            ("Kill two birds with one stone", "Một mũi tên trúng hai đích, giải quyết 2 việc cùng lúc."),
            ("White elephant", "Tài sản đắt tiền nhưng tốn kém duy trì và không mang lại lợi ích gì."),
            ("Dark horse", "Nhân tố bí ẩn, người ít ai ngờ tới nhưng lại giành chiến thắng vang dội."),
        ],
        "quiz": [
            ("Giải quyết được 2 công việc chỉ bằng một hành động duy nhất:", "Kill two birds with one stone", "Bark up the wrong tree", "Hold your horses", "Smell a rat", "A"),
            ("Một cây cầu xây hàng nghìn tỷ nhưng bỏ hoang không ai đi gọi là gì?", "Black sheep", "White elephant", "Trojan horse", "Paper tiger", "B"),
            ("Một ứng viên ít tên tuổi bỗng chốc trở thành quán quân cuộc thi:", "Dark horse", "Lone wolf", "Eager beaver", "Early bird", "A"),
            ("Ý nghĩa của 'Let the cat out of the bag' tương tự thành ngữ nào?", "Spill the beans", "Cry wolf", "Face the music", "Hit the road", "A"),
        ],
    },
    {
        "title": "Time & Money Idioms",
        "description": "Thành ngữ về thời gian, tiền tài và sự quý giá của tài nguyên cuộc sống.",
        "cards": [
            ("Cost an arm and a leg", "Cực kỳ đắt đỏ, tốn kém một khoản tiền khổng lồ."),
            ("Time flies", "Thời gian trôi qua quá nhanh chóng khi bạn đang vui vẻ."),
            ("Break the bank", "Tiêu tốn hết sạch tiền tiết kiệm hoặc làm khánh kiệt tài chính."),
            ("Once in a blue moon", "Rất hiếm khi xảy ra, năm thì mười họa mới có một lần."),
        ],
        "quiz": [
            ("Chiếc siêu xe này giá hàng chục triệu đô la, nó thật sự:", "Costs an arm and a leg", "Costs peanuts", "Is dirt cheap", "Is a dime a dozen", "A"),
            ("Chuyện hiếm khi diễn ra trong tự nhiên được ví với hiện tượng nào?", "Once in a blue moon", "At the drop of a hat", "Around the clock", "In the nick of time", "A"),
            ("Kỳ nghỉ hè trôi qua chớp mắt như một giấc mơ:", "Time stands still", "Time flies", "Time heals", "Time drags", "B"),
            ("Mua một món đồ vừa túi tiền mà không sợ rỗng ví:", "Won't break the bank", "Will cost a fortune", "Will pay through the nose", "Will cost the earth", "A"),
        ],
    },
    {
        "title": "Color Idioms & Expressions",
        "description": "Thành ngữ ẩn dụ bằng màu sắc trong văn hóa Anh - Mỹ.",
        "cards": [
            ("Out of the blue", "Hoàn toàn bất ngờ, không có dấu hiệu báo trước."),
            ("Green with envy", "Cực kỳ ghen tị, đố kỵ với thành công của người khác."),
            ("In the red", "Rơi vào tình trạng thâm hụt tài chính, nợ nần thua lỗ."),
            ("Golden opportunity", "Cơ hội ngàn vàng vô cùng quý báu khó có lần thứ hai."),
        ],
        "quiz": [
            ("Một lá thư bí ẩn bất ngờ gửi đến mà không ai hay biết trước:", "Out of the blue", "In black and white", "Red-handed", "Green thumb", "A"),
            ("Thấy bạn mình trúng số độc đắc, anh ấy cảm thấy ghen tức:", "Green with envy", "Tickled pink", "Feeling blue", "Grey area", "A"),
            ("Doanh nghiệp kinh doanh thua lỗ và đang ngập trong nợ nần:", "In the black", "In the red", "In the pink", "In the clear", "B"),
            ("Một cơ hội nghề nghiệp tuyệt vời không thể bỏ lỡ gọi là gì?", "Golden opportunity", "Silver lining", "White lie", "Blue-collar job", "A"),
        ],
    },

    # --- 21-30: IELTS Academic Vocabulary by Topic ---
    {
        "title": "IELTS: Environment & Climate Change",
        "description": "Từ vựng học thuật trọng điểm chủ đề môi trường và biến đổi khí hậu toàn cầu.",
        "cards": [
            ("Biodiversity", "Sự đa dạng sinh học của các loài sinh vật trong một hệ sinh thái."),
            ("Deforestation", "Hành vi phá rừng quy mô lớn gây suy thoái môi trường đất và khí hậu."),
            ("Sustainable", "Bền vững, có thể duy trì lâu dài mà không làm cạn kiệt tài nguyên thiên nhiên."),
            ("Carbon footprint", "Tổng lượng khí nhà kính thải ra khí quyển do hoạt động của con người."),
        ],
        "quiz": [
            ("Thuật ngữ chỉ sự phong phú về giống loài sinh vật trong tự nhiên là gì?", "Deforestation", "Biodiversity", "Erosion", "Emission", "B"),
            ("Nguồn năng lượng có thể tái tạo và không làm tổn hại môi trường trong tương lai có tính chất gì?", "Depleted", "Hazardous", "Sustainable", "Fossil", "C"),
            ("Chỉ số đo lường lượng khí nhà kính cá nhân hoặc tổ chức thải ra gọi là gì?", "Carbon footprint", "Ozone layer", "Acid rain", "Ecological niche", "A"),
            ("Nạn chặt phá rừng hàng loạt trên diện rộng gọi là gì?", "Afforestation", "Deforestation", "Irrigation", "Agriculture", "B"),
        ],
    },
    {
        "title": "IELTS: Technology & Artificial Intelligence",
        "description": "Từ vựng IELTS band cao về công nghệ hiện đại, tự động hóa và AI.",
        "cards": [
            ("Automation", "Quá trình tự động hóa thay thế thao tác thủ công của con người bằng máy móc."),
            ("Breakthrough", "Bước đột phá công nghệ quan trọng mở ra kỷ nguyên mới."),
            ("Ubiquitous", "Có mặt ở khắp mọi nơi, phổ biến cùng lúc ở mọi ngõ ngách đời sống."),
            ("Ethical dilemma", "Thế tiến thoái lưỡng nan về mặt đạo đức khi áp dụng công nghệ mới."),
        ],
        "quiz": [
            ("Một phát minh mang tính cách mạng mở ra hướng đi hoàn toàn mới được gọi là gì?", "Stagnation", "Breakthrough", "Setback", "Drawback", "B"),
            ("Smartphone hiện nay xuất hiện ở khắp mọi nơi trên thế giới, tính chất này là gì?", "Obsolete", "Ubiquitous", "Scarce", "Primitive", "B"),
            ("Việc máy móc thay thế dây chuyền sản xuất của con người được gọi là gì?", "Manual labor", "Automation", "Craftsmanship", "Deceleration", "B"),
            ("Khi AI đứng trước câu hỏi về tính đúng sai trong việc quyết định mạng sống, đó là gì?", "Technical bug", "Ethical dilemma", "Financial crisis", "Cyber attack", "B"),
        ],
    },
    {
        "title": "IELTS: Education & Academic Systems",
        "description": "Từ vựng về phương pháp giáo dục, thi cử và môi trường đại học.",
        "cards": [
            ("Curriculum", "Toàn bộ khung chương trình giảng dạy của một khóa học hoặc nhà trường."),
            ("Pedagogy", "Khoa học sư phạm, phương pháp và nghệ thuật truyền đạt kiến thức giảng dạy."),
            ("Literacy", "Khả năng biết đọc, biết viết và thấu hiểu văn bản cơ bản của con người."),
            ("Tertiary education", "Bậc giáo dục đại học và sau đại học (cao đẳng, đại học, viện nghiên cứu)."),
        ],
        "quiz": [
            ("Khung chương trình học tập toàn diện được thiết kế bởi nhà trường gọi là gì?", "Syllabus", "Curriculum", "Transcript", "Diploma", "B"),
            ("Phương pháp giảng dạy và nghệ thuật sư phạm của giáo viên gọi là gì?", "Psychology", "Pedagogy", "Sociology", "Morphology", "B"),
            ("Bậc học cao đẳng, đại học được gọi bằng thuật ngữ học thuật nào?", "Primary education", "Secondary education", "Tertiary education", "Vocational training", "C"),
            ("Tỷ lệ người dân biết đọc và biết viết trong một quốc gia gọi là tỷ lệ gì?", "Literacy rate", "Drop-out rate", "Employment rate", "Birth rate", "A"),
        ],
    },
    {
        "title": "IELTS: Modern Medicine & Healthcare",
        "description": "Từ vựng học thuật về chăm sóc y tế, phòng ngừa dịch bệnh và dược phẩm.",
        "cards": [
            ("Epidemic", "Dịch bệnh bùng phát bất ngờ và lây lan nhanh chóng trong một khu vực."),
            ("Vaccination", "Biện pháp tiêm chủng vắc-xin để tạo kháng thể miễn dịch chủ động."),
            ("Chronic", "Mãn tính, kéo dài dai dẳng trong nhiều năm (như bệnh tiểu đường, tim mạch)."),
            ("Rehabilitation", "Quá trình phục hồi chức năng thể chất hoặc tinh thần sau chấn thương nặng."),
        ],
        "quiz": [
            ("Căn bệnh kéo dài liên tục nhiều năm không thể chữa dứt điểm ngay gọi là bệnh gì?", "Acute", "Chronic", "Mild", "Transient", "B"),
            ("Quá trình tập luyện vật lý trị liệu để hồi phục cơ thể sau tai nạn gọi là gì?", "Surgery", "Rehabilitation", "Prescription", "Sterilization", "B"),
            ("Hiện tượng một bệnh truyền nhiễm bùng nổ dữ dội trong cộng đồng gọi là gì?", "Epidemic", "Remission", "Hygiene", "Immunity", "A"),
            ("Phương pháp tiêm phòng để kích hoạt hệ miễn dịch phòng bệnh được gọi là gì?", "Chemotherapy", "Vaccination", "Sedation", "Dialysis", "B"),
        ],
    },
    {
        "title": "IELTS: Globalization & International Trade",
        "description": "Từ vựng về toàn cầu hóa, thương mại tự do và hội nhập quốc tế.",
        "cards": [
            ("Tariff", "Thuế quan đánh vào hàng hóa xuất khẩu hoặc nhập khẩu giữa các nước."),
            ("Integration", "Quá trình hội nhập kinh tế, chính trị và văn hóa giữa các quốc gia."),
            ("Multinational", "Tập đoàn đa quốc gia hoạt động sản xuất kinh doanh tại nhiều nước."),
            ("Interdependence", "Sự phụ thuộc lẫn nhau về chuỗi cung ứng và kinh tế giữa các dân tộc."),
        ],
        "quiz": [
            ("Khoản thuế đánh vào hàng hóa nhập khẩu từ nước ngoài gọi là gì?", "Subsidy", "Tariff", "Dividend", "Inflation", "B"),
            ("Một công ty có chi nhánh và nhà máy tại 20 quốc gia được gọi là gì?", "Domestic firm", "Multinational corporation", "Start-up", "Sole trader", "B"),
            ("Hiện tượng các nền kinh tế trên thế giới phụ thuộc mật thiết vào nhau gọi là gì?", "Isolation", "Interdependence", "Protectionism", "Autonomy", "B"),
            ("Quá trình các quốc gia gắn kết và hợp tác sâu rộng trên toàn cầu gọi là gì?", "Integration", "Segregation", "Colonization", "Decoupling", "A"),
        ],
    },
    {
        "title": "IELTS: Art & Cultural Heritage",
        "description": "Từ vựng IELTS về bảo tồn di sản, văn hóa dân gian và nghệ thuật kiến trúc.",
        "cards": [
            ("Indigenous", "Thuộc về người bản địa, có nguồn gốc tự nhiên sinh sống lâu đời tại địa phương."),
            ("Preservation", "Công tác bảo tồn, gìn giữ các công trình lịch sử và di sản nguyên vẹn."),
            ("Artifact", "Cổ vật do bàn tay con người thời cổ đại chế tác mang giá trị khảo cổ."),
            ("Intangible", "Phi vật thể, không thể cầm nắm được (như truyền thống dân ca, lễ hội)."),
        ],
        "quiz": [
            ("Di sản văn hóa phi vật thể (như ca trù, nhã nhạc cung đình) được mô tả bằng từ nào?", "Tangible", "Intangible", "Concrete", "Physical", "B"),
            ("Những hiện vật khảo cổ học khai quật từ lăng mộ cổ gọi là gì?", "Artifacts", "Fossils", "Minerals", "Novels", "A"),
            ("Các bộ tộc bản địa sinh sống từ ngàn xưa tại vùng đất châu Úc gọi là gì?", "Immigrant population", "Indigenous people", "Colonial settlers", "Urban dwellers", "B"),
            ("Nỗ lực bảo vệ rừng nguyên sinh và các đền đài cổ khỏi sự tàn phá gọi là gì?", "Demolition", "Preservation", "Exploitation", "Urbanization", "B"),
        ],
    },
    {
        "title": "IELTS: Urbanization & City Infrastructure",
        "description": "Từ vựng về đô thị hóa, mật độ dân số và quy hoạch giao thông công cộng.",
        "cards": [
            ("Congestion", "Tình trạng tắc nghẽn giao thông hoặc quá tải mật độ nghiêm trọng."),
            ("Infrastructure", "Cơ sở hạ tầng kỹ thuật cơ bản của một thành phố (đường sá, cầu cống, điện nước)."),
            ("Metropolis", "Đô thị khổng lồ, siêu thành phố đóng vai trò trung tâm kinh tế lớn."),
            ("Pedestrian", "Người đi bộ lưu thông trên vỉa hè hoặc qua đường tại khu vực đô thị."),
        ],
        "quiz": [
            ("Hệ thống giao thông, điện lưới, cấp thoát nước của một quốc gia gọi chung là gì?", "Superstructure", "Infrastructure", "Demographics", "Architecture", "B"),
            ("Tình trạng ùn tắc kẹt xe giờ cao điểm tại các ngã tư được diễn đạt bằng từ nào?", "Free flow", "Traffic congestion", "Rapid transit", "Pedestrian zone", "B"),
            ("Người tham gia giao thông bằng cách đi bộ trên phố gọi là gì?", "Driver", "Cyclist", "Pedestrian", "Commuter", "C"),
            ("Một siêu đô thị hàng chục triệu dân như Tokyo hay New York được gọi là gì?", "Hamlet", "Village", "Metropolis", "Suburb", "C"),
        ],
    },
    {
        "title": "IELTS: Crime & Criminal Justice",
        "description": "Từ vựng học thuật về tội phạm, xét xử và hệ thống tư pháp.",
        "cards": [
            ("Deterrent", "Biện pháp răn đe nhằm ngăn ngừa người khác có ý định phạm tội."),
            ("Rehabilitate", "Cải tạo và giáo dục phạm nhân để họ tái hòa nhập tốt với xã hội."),
            ("Defendant", "Bị cáo, người bị đưa ra xét xử trước tòa án vì cáo buộc phạm pháp."),
            ("Verdict", "Phán quyết chính thức của bồi thẩm đoàn hoặc tòa án (có tội hay vô tội)."),
        ],
        "quiz": [
            ("Hình phạt nặng nhằm răn đe không cho kẻ khác phạm tội gọi là gì?", "Incentive", "Deterrent", "Reward", "Pardon", "B"),
            ("Phán quyết cuối cùng của tòa án tuyên bố bị cáo có tội hay không gọi là gì?", "Lawsuit", "Verdict", "Testimony", "Indictment", "B"),
            ("Mục tiêu cải tạo người lầm lỡ thành công dân có ích cho xã hội được diễn tả bằng từ nào?", "Incarcerate", "Rehabilitate", "Condemn", "Penalize", "B"),
            ("Người bị truy tố và đứng trước vành móng ngựa gọi là gì?", "Prosecutor", "Judge", "Defendant", "Juror", "C"),
        ],
    },
    {
        "title": "IELTS: Psychology & Human Behavior",
        "description": "Từ vựng tâm lý học, nhận thức và hành vi con người.",
        "cards": [
            ("Cognitive", "Liên quan đến quá trình nhận thức, suy nghĩ và tiếp nhận thông tin của não."),
            ("Subconscious", "Tiềm thức, những hoạt động tinh thần diễn ra dưới mức ý thức rõ ràng."),
            ("Trauma", "Chấn thương tâm lý sâu sắc gây ra bởi trải nghiệm đau buồn hoặc kinh hoàng."),
            ("Introvert", "Người hướng nội, có xu hướng thích suy ngẫm một mình hơn là đám đông."),
        ],
        "quiz": [
            ("Các quá trình tư duy, ghi nhớ và xử lý logic của não bộ gọi là khả năng gì?", "Sensory", "Cognitive", "Motor", "Reflex", "B"),
            ("Người nạp lại năng lượng tinh thần khi ở một mình và ít thích tụ tập đông người là ai?", "Extrovert", "Introvert", "Optimist", "Altruist", "B"),
            ("Vết thương tâm lý dai dẳng sau biến cố thảm khốc gọi là gì?", "Euphoria", "Nostalgia", "Trauma", "Apathy", "C"),
            ("Tầng nhận thức vận hành âm thầm phía sau ý thức hàng ngày được gọi là gì?", "Conscious", "Subconscious", "Instinct", "Intuition", "B"),
        ],
    },
    {
        "title": "IELTS: Space Exploration & Astrophysics",
        "description": "Từ vựng về thám hiểm không gian vũ trụ và vật lý thiên văn.",
        "cards": [
            ("Celestial", "Thuộc về bầu trời hoặc các thiên thể trong vũ trụ bao la (sao, hành tinh)."),
            ("Orbit", "Quỹ đạo chuyển động hình elip của một vật thể bay quanh một thiên thể khác."),
            ("Telescope", "Kính thiên văn quang học hoặc vô tuyến dùng để quan sát các vì sao xa xôi."),
            ("Extraterrestrial", "Thuộc về ngoài Trái Đất, sinh vật hoặc hiện tượng ngoài hành tinh."),
        ],
        "quiz": [
            ("Đường đi hình elip mà Trái Đất quay xung quanh Mặt Trời được gọi là gì?", "Axis", "Orbit", "Equator", "Horizon", "B"),
            ("Thiết bị chuyên dụng giúp các nhà khoa học ngắm nhìn các thiên hà xa xôi là gì?", "Microscope", "Periscope", "Telescope", "Stethoscope", "C"),
            ("Sinh vật được cho là đến từ các hành tinh khác ngoài Trái Đất gọi là gì?", "Terrestrial", "Extraterrestrial", "Aquatic", "Subterranean", "B"),
            ("Mặt trời, mặt trăng và các chòm sao được gọi chung là các thiên thể gì?", "Terrestrial bodies", "Celestial bodies", "Atmospheric bodies", "Oceanic bodies", "B"),
        ],
    },

    # --- 31-40: TOEIC Business & Corporate ---
    {
        "title": "TOEIC: Corporate Management",
        "description": "Từ vựng quản trị doanh nghiệp, điều hành và cơ cấu tổ chức công ty.",
        "cards": [
            ("Supervisor", "Người giám sát trực tiếp, theo dõi công việc của nhân viên cấp dưới."),
            ("Headquarters", "Trụ sở chính của một tập đoàn nơi đặt ban lãnh đạo cấp cao."),
            ("Delegation", "Sự ủy thác hoặc giao phó trách nhiệm, quyền hạn cho cấp dưới xử lý."),
            ("Productivity", "Năng suất lao động, hiệu quả đầu ra so với thời gian và công sức bỏ ra."),
        ],
        "quiz": [
            ("Văn phòng trung tâm đầu não của một doanh nghiệp lớn gọi là gì?", "Branch", "Warehouse", "Headquarters", "Outlet", "C"),
            ("Khả năng nhà quản lý giao việc cho cấp dưới thực hiện được gọi là gì?", "Delegation", "Supervision", "Demotion", "Resignation", "A"),
            ("Chỉ số đo lường khối lượng sản phẩm làm ra trên mỗi giờ làm việc là gì?", "Deficit", "Productivity", "Overhead", "Liability", "B"),
            ("Người quản lý theo dõi sát sao công việc hàng ngày của bạn trong công ty là ai?", "Intern", "Supervisor", "Competitor", "Shareholder", "B"),
        ],
    },
    {
        "title": "TOEIC: Contracts & Negotiations",
        "description": "Từ vựng đàm phán hợp đồng thương mại và các điều khoản pháp lý.",
        "cards": [
            ("Clause", "Điều khoản cụ thể được quy định trong một bản hợp đồng pháp lý."),
            ("Compromise", "Thỏa hiệp, đôi bên cùng nhượng bộ một phần lợi ích để đạt thỏa thuận."),
            ("Breach of contract", "Vi phạm hợp đồng, không thực hiện đúng các cam kết đã ký."),
            ("Binding", "Có tính chất ràng buộc pháp lý bắt buộc các bên phải tuân thủ nghiêm ngặt."),
        ],
        "quiz": [
            ("Mỗi mục quy định quyền lợi và nghĩa vụ riêng biệt trong hợp đồng gọi là gì?", "Clause", "Chapter", "Stanza", "Heading", "A"),
            ("Khi hai đối tác đàm phán cùng lùi một bước để đi đến tiếng nói chung:", "Breach", "Compromise", "Penalty", "Dispute", "B"),
            ("Hành vi phá vỡ cam kết đã ký kết trong văn bản thỏa thuận gọi là gì?", "Extension", "Breach of contract", "Amendment", "Termination", "B"),
            ("Một bản hợp đồng có hiệu lực pháp lý bắt buộc được miêu tả bằng tính từ nào?", "Void", "Optional", "Binding", "Informal", "C"),
        ],
    },
    {
        "title": "TOEIC: Banking & Corporate Finance",
        "description": "Từ vựng về tài chính công ty, báo cáo kế toán và dòng tiền doanh nghiệp.",
        "cards": [
            ("Revenue", "Tổng doanh thu bán hàng của doanh nghiệp trước khi trừ đi các chi phí."),
            ("Dividend", "Cổ tức, khoản lợi nhuận chia cho các cổ đông nắm giữ cổ phần công ty."),
            ("Bankruptcy", "Tình trạng phá sản, mất hoàn toàn khả năng thanh toán các khoản nợ đến hạn."),
            ("Audit", "Hoạt động kiểm toán độc lập kiểm tra tính minh bạch của sổ sách tài chính."),
        ],
        "quiz": [
            ("Tổng số tiền một công ty thu được từ hoạt động kinh doanh bán hàng là gì?", "Expense", "Revenue", "Debt", "Loss", "B"),
            ("Phần lợi nhuận ròng được ban lãnh đạo trích ra chia cho cổ đông gọi là gì?", "Bonus", "Dividend", "Commission", "Royalty", "B"),
            ("Tình trạng pháp lý khi một công ty không còn khả năng trả nợ và tuyên bố sụp đổ:", "Merger", "Liquidity", "Bankruptcy", "Solvency", "C"),
            ("Quá trình kiểm tra độc lập các báo cáo tài chính của công ty gọi là gì?", "Audit", "Forecast", "Transaction", "Investment", "A"),
        ],
    },
    {
        "title": "TOEIC: Marketing & Public Relations",
        "description": "Từ vựng về tiếp thị, chiến dịch quảng cáo và định vị thương hiệu.",
        "cards": [
            ("Demographics", "Đặc điểm nhân khẩu học của nhóm khách hàng mục tiêu (tuổi, giới tính)."),
            ("Slogan", "Khẩu hiệu thương mại ngắn gọn, ấn tượng tạo dấu ấn cho thương hiệu."),
            ("Endorsement", "Sự bảo chứng hoặc đại diện quảng bá sản phẩm của người nổi tiếng."),
            ("Launch", "Sự kiện ra mắt hoặc tung một sản phẩm mới ra thị trường rộng rãi."),
        ],
        "quiz": [
            ("Thông tin về độ tuổi, thu nhập, nơi ở của người tiêu dùng thuộc về chỉ số nào?", "Psychographics", "Demographics", "Geography", "Analytics", "B"),
            ("Câu khẩu hiệu ngắn gọn dễ nhớ của một nhãn hàng được gọi là gì?", "Logo", "Slogan", "Trademark", "Billboard", "B"),
            ("Việc thuê một ca sĩ nổi tiếng sử dụng và khen ngợi dòng điện thoại mới là gì?", "Endorsement", "Boycott", "Plagiarism", "Defamation", "A"),
            ("Ngày đầu tiên đưa một sản phẩm công nghệ mới toanh ra thị trường gọi là lễ gì?", "Recall", "Launch", "Liquidation", "Clearance", "B"),
        ],
    },
    {
        "title": "TOEIC: Human Resources & Recruitment",
        "description": "Từ vựng về tuyển dụng nhân sự, phỏng vấn và phúc lợi nhân viên.",
        "cards": [
            ("Candidate", "Ứng viên nộp hồ sơ xin việc đang ứng tuyển vào vị trí trống."),
            ("Probation", "Thời gian thử việc để đánh giá năng lực thực tế trước khi ký chính thức."),
            ("Compensation", "Chế độ đãi ngộ, tiền lương và phụ cấp đền bù cho sức lao động."),
            ("Resignation", "Đơn xin từ chức hoặc quyết định nghỉ việc tự nguyện của nhân viên."),
        ],
        "quiz": [
            ("Người nộp hồ sơ tham gia phỏng vấn xin việc được gọi là gì?", "Interviewer", "Candidate", "Executive", "Recruiter", "B"),
            ("Giai đoạn 2 tháng đầu làm quen và thử thách năng lực tại công ty gọi là gì?", "Tenure", "Sabbatical", "Probation", "Retirement", "C"),
            ("Gói thu nhập gồm lương cứng, thưởng và bảo hiểm y tế gọi chung là gì?", "Deduction", "Penalty", "Compensation", "Tax", "C"),
            ("Văn bản nhân viên gửi ban giám đốc khi muốn chủ động thôi việc là gì?", "Promotion", "Resignation", "Appraisal", "Contract", "B"),
        ],
    },
    {
        "title": "TOEIC: Logistics & Cargo Shipping",
        "description": "Từ vựng về vận chuyển hàng hải, kho bãi và giao nhận hàng hóa.",
        "cards": [
            ("Freight", "Hàng hóa vận chuyển số lượng lớn bằng đường biển, đường sắt hoặc máy bay."),
            ("Consignment", "Lô hàng được ký gửi hoặc bàn giao cho đơn vị vận tải chuyển phát."),
            ("Customs", "Cơ quan hải quan kiểm soát hàng hóa ra vào biên giới quốc gia."),
            ("Warehouse", "Nhà kho rộng lớn dùng để lưu trữ và bảo quản hàng tồn kho an toàn."),
        ],
        "quiz": [
            ("Hàng hóa được chuyên chở bằng tàu biển hoặc máy bay chở hàng gọi là gì?", "Luggage", "Baggage", "Freight", "Parcel", "C"),
            ("Cơ quan nhà nước chịu trách nhiệm thu thuế và kiểm tra hàng hóa tại cảng là gì?", "Customs", "Immigration", "Police", "Coast Guard", "A"),
            ("Tòa nhà có diện tích rộng dùng để chứa các pallet hàng hóa lưu kho gọi là gì?", "Factory", "Showroom", "Warehouse", "Laboratory", "C"),
            ("Mỗi kiện hàng hoặc lô hàng ký gửi chuyển phát nhanh gọi là gì?", "Consignment", "Insurance", "Inventory", "Vessel", "A"),
        ],
    },
    {
        "title": "TOEIC: Manufacturing & Quality Control",
        "description": "Từ vựng về quy trình sản xuất nhà máy và kiểm định chất lượng sản phẩm.",
        "cards": [
            ("Defect", "Khuyết tật hoặc lỗi sai hỏng kỹ thuật xuất hiện trên sản phẩm sản xuất."),
            ("Assembly line", "Dây chuyền lắp ráp tự động tuần tự trong các nhà máy công nghiệp."),
            ("Specification", "Bảng thông số kỹ thuật chi tiết quy định tiêu chuẩn vật liệu và kích thước."),
            ("Standardize", "Tiêu chuẩn hóa quy trình để mọi sản phẩm đều có chất lượng đồng đều."),
        ],
        "quiz": [
            ("Một lỗi kỹ thuật khiến sản phẩm không thể xuất xưởng gọi là gì?", "Asset", "Defect", "Feature", "Patent", "B"),
            ("Hệ thống chuyền sản phẩm qua từng công nhân để lắp ráp hoàn thiện gọi là gì?", "Supply chain", "Assembly line", "Pipeline", "Grid", "B"),
            ("Tài liệu ghi rõ kích thước, trọng lượng, điện áp của linh kiện là bảng gì?", "Invoice", "Specification", "Warranty", "Manifest", "B"),
            ("Hành động áp dụng chung một quy chuẩn thống nhất cho toàn nhà máy là gì?", "Diversify", "Standardize", "Complicate", "Disrupt", "B"),
        ],
    },
    {
        "title": "TOEIC: Office Technology & Telecommunications",
        "description": "Từ vựng về thiết bị văn phòng, mạng máy tính nội bộ và viễn thông.",
        "cards": [
            ("Troubleshoot", "Tìm kiếm nguyên nhân và khắc phục sự cố kỹ thuật của hệ thống phần cứng."),
            ("Intranet", "Mạng máy tính nội bộ khép kín chỉ dành riêng cho nhân viên công ty truy cập."),
            ("Malfunction", "Sự cố hỏng hóc hoặc vận hành sai chức năng của một thiết bị điện máy."),
            ("Upgrade", "Nâng cấp phần cứng hoặc cập nhật phần mềm lên phiên bản mới ưu việt hơn."),
        ],
        "quiz": [
            ("Khi máy in bị kẹt giấy, nhân viên IT đến tìm lỗi và sửa chữa, anh ta đang làm gì?", "Troubleshooting", "Purchasing", "Programming", "Marketing", "A"),
            ("Mạng thông tin nội bộ chỉ cho phép máy tính trong công ty kết nối là gì?", "Internet", "Intranet", "Ethernet", "Extranet", "B"),
            ("Thiết bị văn phòng đột ngột ngừng hoạt động hoặc chạy chập chờn gọi là gì?", "Efficiency", "Malfunction", "Optimization", "Innovation", "B"),
            ("Hành động thay thế thanh RAM dung lượng cao hơn cho máy tính là gì?", "Downgrade", "Discard", "Upgrade", "Installment", "C"),
        ],
    },
    {
        "title": "TOEIC: Customer Support & Service",
        "description": "Từ vựng về chăm sóc khách hàng, phản hồi dịch vụ và giải quyết khiếu nại.",
        "cards": [
            ("Inquiry", "Lời yêu cầu cung cấp thông tin hoặc câu hỏi thắc mắc từ khách hàng."),
            ("Feedback", "Ý kiến phản hồi, nhận xét đánh giá về chất lượng sản phẩm dịch vụ."),
            ("Satisfaction", "Mức độ hài lòng và thỏa mãn nhu cầu của khách hàng đối với dịch vụ."),
            ("Complaint", "Lời phàn nàn, khiếu nại chính thức khi khách hàng không ưng ý."),
        ],
        "quiz": [
            ("Một email hỏi về giá cả và thông số kỹ thuật của sản phẩm thuộc dạng gì?", "Complaint", "Inquiry", "Invoice", "Warranty", "B"),
            ("Phiếu khảo sát ý kiến người tiêu dùng nhằm thu thập thông tin gì?", "Feedback", "Deficit", "Dividend", "Revenue", "A"),
            ("Mục tiêu cao nhất của phòng chăm sóc khách hàng là gì?", "Customer satisfaction", "Customer dispute", "Customer turnover", "Customer penalty", "A"),
            ("Khi khách hàng nhận phải món đồ bị vỡ và gọi điện bức xúc, đó là một:", "Praise", "Complaint", "Referral", "Recommendation", "B"),
        ],
    },
    {
        "title": "TOEIC: Business Conferences & Networking",
        "description": "Từ vựng về hội thảo quốc tế, diễn đàn thương mại và giao lưu đối tác.",
        "cards": [
            ("Agenda", "Chương trình nghị sự liệt kê các nội dung sẽ thảo luận trong cuộc họp."),
            ("Keynote speaker", "Diễn giả chính danh dự phát biểu mở đầu tại một hội nghị lớn."),
            ("Participant", "Người tham dự, đại biểu có mặt trong sự kiện hoặc buổi hội thảo."),
            ("Networking", "Hoạt động kết nối, giao lưu xây dựng mối quan hệ làm ăn với đối tác mới."),
        ],
        "quiz": [
            ("Danh sách các đề mục cần bàn thảo trong buổi họp giao ban gọi là gì?", "Agenda", "Resume", "Manifest", "Brochure", "A"),
            ("Nhà khoa học nổi tiếng phát biểu bài nói quan trọng nhất tại hội nghị là ai?", "Keynote speaker", "Audience", "Organizer", "Sponsor", "A"),
            ("Hoạt động trao đổi danh thiếp và làm quen với các giám đốc công ty khác gọi là gì?", "Networking", "Benchmarking", "Outsourcing", "Downsizing", "A"),
            ("Những người có mặt và lắng nghe trong phòng hội thảo được gọi chung là gì?", "Participants", "Competitors", "Supervisors", "Inspectors", "A"),
        ],
    },

    # --- 41-50: English Grammar & Vocabulary Nuances ---
    {
        "title": "English Grammar: Advanced Tenses",
        "description": "Phân biệt các thì tiếng Anh nâng cao (Hoàn thành tiếp diễn, Quá khứ hoàn thành).",
        "cards": [
            ("Past Perfect", "Diễn tả một hành động đã hoàn tất trước một mốc thời điểm hoặc hành động khác trong quá khứ."),
            ("Future Continuous", "Diễn tả hành động đang xảy ra tại một thời điểm cụ thể được xác định trong tương lai."),
            ("Present Perfect Continuous", "Nhấn mạnh tính liên tục của hành động bắt đầu trong quá khứ và vẫn đang tiếp diễn."),
            ("Time Clause", "Mệnh đề trạng ngữ chỉ thời gian (when, as soon as, by the time) không dùng thì tương lai."),
        ],
        "quiz": [
            ("Thì nào dùng để nhấn mạnh tính liên tục của hành động kéo dài từ quá khứ đến hiện tại?", "Present Continuous", "Present Perfect Continuous", "Simple Past", "Future Simple", "B"),
            ("Hành động xảy ra trước một hành động khác trong quá khứ được chia ở thì nào?", "Past Simple", "Past Perfect", "Past Continuous", "Present Perfect", "B"),
            ("Trong câu: 'By the time you arrive tomorrow, I ______', chỗ trống cần điền thì gì?", "will have left", "had left", "have left", "left", "A"),
            ("Trong mệnh đề thời gian bắt đầu bằng 'As soon as', ta dùng thì gì thay cho tương lai đơn?", "Hiện tại đơn", "Quá khứ đơn", "Tương lai gần", "Quá khứ hoàn thành", "A"),
        ],
    },
    {
        "title": "English Grammar: Conditionals",
        "description": "Các dạng câu điều kiện (Loại 0, 1, 2, 3 và Câu điều kiện hỗn hợp Mixed Conditionals).",
        "cards": [
            ("Zero Conditional", "Diễn tả chân lý khoa học, quy luật tự nhiên luôn luôn đúng (If + V_s/es, V_s/es)."),
            ("First Conditional", "Diễn tả sự việc có thật hoặc khả năng cao sẽ xảy ra ở hiện tại hoặc tương lai."),
            ("Second Conditional", "Giả định sự việc trái ngược với thực tế ở hiện tại (If + V2/ed, would + V)."),
            ("Third Conditional", "Giả định sự việc trái ngược với sự thật trong quá khứ (If + had V3, would have V3)."),
        ],
        "quiz": [
            ("'If you heat ice, it melts' là cấu trúc câu điều kiện loại mấy?", "Loại 0", "Loại 1", "Loại 2", "Loại 3", "A"),
            ("Cấu trúc 'If I had studied harder, I would have passed the exam' là loại mấy?", "Loại 1", "Loại 2", "Loại 3", "Mixed", "C"),
            ("Giả định về một điều không có thật ở hiện tại: 'If I ______ a bird, I would fly':", "am", "were", "had been", "will be", "B"),
            ("Câu điều kiện hỗn hợp (Mixed) thường kết hợp giả định quá khứ (If had V3) với kết quả ở đâu?", "Ở tương lai xa", "Ở hiện tại (would + V)", "Ở thời tiền sử", "Ở quá khứ hoàn thành", "B"),
        ],
    },
    {
        "title": "English Grammar: Passive Voice & Causatives",
        "description": "Câu bị động nâng cao và cấu trúc nhờ vả (Have/Get something done).",
        "cards": [
            ("Passive Voice", "Cấu trúc nhấn mạnh đối tượng tiếp nhận hành động thay vì người thực hiện (Be + V3/ed)."),
            ("Have someone do", "Nhờ ai đó làm việc gì (chủ động): Have + Object (người) + Bare Infinitive."),
            ("Get someone to do", "Thuyết phục ai đó làm việc gì (chủ động): Get + Object (người) + To-Infinitive."),
            ("Causative Passive", "Nhờ/thuê việc gì được làm: Have/Get + Object (vật) + Past Participle (V3/ed)."),
        ],
        "quiz": [
            ("Điền từ vào chỗ trống: 'I had the mechanic ______ my car brakes.'", "repair", "to repair", "repaired", "repairing", "A"),
            ("Điền từ vào chỗ trống: 'I got my brother ______ me with my homework.'", "help", "to help", "helped", "helping", "B"),
            ("Cấu trúc nhờ cắt tóc: 'I am going to have my hair ______ tomorrow.'", "cut", "to cut", "cutting", "cuts", "A"),
            ("Trong câu bị động, tân ngữ 'by them/people' thường được xử lý như thế nào?", "Bắt buộc giữ lại", "Lược bỏ vì không xác định rõ", "Đặt lên đầu câu", "Chuyển thành tính từ", "B"),
        ],
    },
    {
        "title": "English Grammar: Relative & Participle Clauses",
        "description": "Mệnh đề quan hệ xác định/không xác định và mệnh đề phân từ rút gọn.",
        "cards": [
            ("Defining clause", "Mệnh đề quan hệ xác định, bắt buộc phải có để câu đủ nghĩa, không dùng dấu phẩy."),
            ("Non-defining clause", "Mệnh đề quan hệ không xác định, bổ sung thông tin phụ, ngăn cách bằng dấu phẩy và không dùng 'that'."),
            ("Present Participle", "Rút gọn mệnh đề chủ động cùng chủ ngữ bằng V-ing (Walking down the street, I saw him)."),
            ("Past Participle", "Rút gọn mệnh đề bị động bằng V3/ed (Injured in the accident, he was taken to hospital)."),
        ],
        "quiz": [
            ("Trong mệnh đề quan hệ có dấu phẩy (không xác định), đại từ quan hệ nào TUYỆT ĐỐI không được dùng?", "Which", "Who", "Whom", "That", "D"),
            ("Rút gọn câu chủ động: 'Because she felt tired, she went to bed early' thành:", "Feeling tired, she went to bed early", "Felt tired, she went to bed early", "To feel tired, she went to bed early", "Having felt, she went to bed early", "A"),
            ("Đại từ quan hệ 'Whose' được dùng để chỉ điều gì?", "Nơi chốn", "Thời gian", "Sở hữu", "Lý do", "C"),
            ("Rút gọn câu bị động: 'The car which was damaged in the crash was towed away' thành:", "The car damaging in the crash...", "The car damaged in the crash...", "The car to damage in the crash...", "The car being damaged...", "B"),
        ],
    },
    {
        "title": "English Grammar: Gerunds & Infinitives",
        "description": "Quy tắc sử dụng Danh động từ (V-ing) và Động từ nguyên mẫu (To-V).",
        "cards": [
            ("Gerund after Preposition", "Sau tất cả các giới từ (in, on, at, about, for, without) động từ luôn ở dạng V-ing."),
            ("Stop to do vs Stop doing", "Stop to do là dừng việc đang làm để làm việc khác; Stop doing là từ bỏ hoàn toàn thói quen."),
            ("Remember to do vs doing", "Remember to do là nhớ phải làm việc bổn phận; Remember doing là nhớ lại một kỷ niệm quá khứ."),
            ("Verbs followed by Gerund", "Các động từ luôn đi với V-ing: avoid, admit, enjoy, postpone, deny, practice, suggest."),
        ],
        "quiz": [
            ("Sau động từ 'Enjoy', động từ theo sau bắt buộc chia ở dạng nào?", "To-Infinitive", "Bare Infinitive", "Gerund (V-ing)", "Past Participle", "C"),
            ("'He stopped smoking 5 years ago' mang ý nghĩa gì?", "Anh ấy dừng lại để hút thuốc", "Anh ấy đã bỏ hẳn hút thuốc 5 năm trước", "Anh ấy quên hút thuốc", "Anh ấy nhớ đã hút thuốc", "B"),
            ("Sau giới từ 'without', dạng động từ nào là chính xác?", "Without leave", "Without to leave", "Without leaving", "Without left", "C"),
            ("'Remember ______ the front door before going to bed' cần điền gì?", "lock", "to lock", "locking", "locked", "B"),
        ],
    },
    {
        "title": "English Grammar: Modal Verbs of Deduction",
        "description": "Động từ khuyết thiếu suy đoán ở hiện tại và quá khứ (Must, Can't, May, Might).",
        "cards": [
            ("Must be", "Chắc chắn là (ở hiện tại) - suy đoán chắc chắn tới 95% dựa trên bằng chứng thuyết phục."),
            ("Can't be", "Chắc chắn không thể là - suy đoán phủ định chắc chắn dựa trên lý lẽ xác thực."),
            ("Must have V3", "Chắc chắn là đã xảy ra trong quá khứ (You must have been exhausted after the trip)."),
            ("Should have V3", "Lẽ ra nên làm gì trong quá khứ nhưng thực tế đã không làm (thể hiện sự tiếc nuối)."),
        ],
        "quiz": [
            ("Đèn phòng vẫn sáng và có tiếng gõ bàn phím: 'He ______ be working now.'", "can't", "must", "shouldn't", "needn't", "B"),
            ("Anh ấy đã ở Nhật Bản tuần trước nên không thể nào gặp tôi ở Hà Nội hôm đó:", "He must have seen me", "He can't have seen me", "He might see me", "He should see me", "B"),
            ("Lẽ ra tôi nên ôn tập bài kỹ hơn cho kỳ thi nhưng tôi lại mải chơi:", "I must have studied", "I should have studied", "I can't have studied", "I might have studied", "B"),
            ("Một phỏng đoán không chắc chắn lắm ở hiện tại (khoảng 30-50%) thường dùng từ nào?", "Must", "Might / May", "Can't", "Will", "B"),
        ],
    },
    {
        "title": "English Grammar: Subjunctive & Inversion",
        "description": "Thể giả định và Cấu trúc đảo ngữ nhấn mạnh trong tiếng Anh học thuật.",
        "cards": [
            ("Subjunctive Mood", "Cấu trúc giả định yêu cầu/đề xuất: It is vital/essential that S + (should) + Bare Verb."),
            ("Negative Inversion", "Đảo ngữ với phó từ phủ định đứng đầu câu (Never, Seldom, Rarely, Hardly) + Trợ động từ + S + V."),
            ("Not only ... but also Inversion", "Not only + Trợ động từ + S + V ... but also ... (Không những mà còn)."),
            ("Only after / Only when", "Only after / Only when + S + V + Trợ động từ + S + V (Chỉ sau khi... thì mới...)."),
        ],
        "quiz": [
            ("Chọn đáp án đúng: 'The doctor recommended that he ______ more exercise.'", "does", "do", "did", "doing", "B"),
            ("Đảo ngữ với 'Never': 'Never ______ such a magnificent view in my life.'", "I have seen", "have I seen", "I saw", "did I saw", "B"),
            ("Cấu trúc 'Hardly had he arrived ______ the phone rang.' điền từ gì?", "than", "when", "then", "after", "B"),
            ("Đảo ngữ với 'Not only': 'Not only ______ talented, but she is also hardworking.'", "is she", "she is", "does she", "she does", "A"),
        ],
    },
    {
        "title": "Collocations with 'Make' and 'Do'",
        "description": "Quy tắc phân biệt và các cụm từ cố định đi với động từ Make và Do.",
        "cards": [
            ("Make a decision", "Đưa ra quyết định cuối cùng sau khi cân nhắc."),
            ("Do research", "Tiến hành công việc nghiên cứu khoa học hoặc tìm hiểu thông tin."),
            ("Make an effort", "Nỗ lực, cố gắng hết sức mình để đạt mục tiêu."),
            ("Do business with", "Hợp tác làm ăn, giao thương kinh doanh với một đối tác."),
        ],
        "quiz": [
            ("Cụm từ nào sau đây là ĐÚNG chuẩn tiếng Anh?", "Do a mistake", "Make a mistake", "Create a mistake", "Take a mistake", "B"),
            ("Để nói về việc giặt quần áo dọn dẹp, ta dùng cụm nào?", "Make the laundry", "Do the laundry", "Build the laundry", "Give the laundry", "B"),
            ("Đưa ra một lời phàn nàn chính thức với cửa hàng:", "Do a complaint", "Make a complaint", "Form a complaint", "Act a complaint", "B"),
            ("Tập thể dục nâng cao sức khỏe:", "Make exercise", "Do exercise", "Hold exercise", "Get exercise", "B"),
        ],
    },
    {
        "title": "Easily Confused Words in English",
        "description": "Phân biệt những cặp từ đồng âm hoặc gần nghĩa dễ gây hiểu lầm trong tiếng Anh.",
        "cards": [
            ("Affect vs Effect", "Affect (động từ): gây ảnh hưởng lên; Effect (danh từ): hệ quả, tác động của sự việc."),
            ("Complement vs Compliment", "Complement: phần bổ sung cho hoàn thiện; Compliment: lời khen ngợi tán dương."),
            ("Principal vs Principle", "Principal: hiệu trưởng hoặc số vốn gốc; Principle: nguyên tắc đạo đức, chân lý."),
            ("Historic vs Historical", "Historic: có ý nghĩa trọng đại trong lịch sử; Historical: liên quan tới quá khứ, lịch sử."),
        ],
        "quiz": [
            ("Thời tiết xấu tác động tiêu cực đến tâm trạng: 'Bad weather ______ my mood.'", "effects", "affects", "effective", "affective", "B"),
            ("Anh ấy khen chiếc váy mới của cô ấy rất đẹp: 'He paid her a nice ______.'", "complement", "compliment", "component", "complex", "B"),
            ("Người đứng đầu một trường trung học được gọi là gì?", "Principle", "Principal", "Prince", "Primary", "B"),
            ("Chiến thắng Điện Biên Phủ là một sự kiện có ý nghĩa trọng đại trong lịch sử:", "A historical event", "A historic event", "A prehistoric event", "A history event", "B"),
        ],
    },
    {
        "title": "Academic Discourse Markers & Connectors",
        "description": "Các liên từ và từ nối logic nâng cấp bài viết học thuật (Furthermore, However, Consequently).",
        "cards": [
            ("Furthermore", "Hơn thế nữa, thêm vào đó (dùng để bổ sung thêm luận điểm mạnh mẽ)."),
            ("Consequently", "Do đó, kết quả là (dùng để nêu hệ quả logic tất yếu của sự việc)."),
            ("Conversely", "Ngược lại, trái lại (dùng để đối chiếu hai khía cạnh tương phản nhau)."),
            ("Notwithstanding", "Mặc dù vậy, bất chấp điều đó (đồng nghĩa với despite / in spite of)."),
        ],
        "quiz": [
            ("Từ nối nào mang nghĩa 'Hơn thế nữa, ngoài ra' tương đương với 'In addition'?", "Consequently", "Furthermore", "Otherwise", "Whereas", "B"),
            ("Từ nào diễn tả mối quan hệ nguyên nhân - kết quả (Do đó, vì vậy)?", "Consequently", "Conversely", "Meanwhile", "Instead", "A"),
            ("Để bắt đầu một đoạn văn đối chiếu quan điểm hoàn toàn trái ngược, ta dùng từ nào?", "Similarly", "Conversely", "Likewise", "Namely", "B"),
            ("Từ 'Notwithstanding' tương đương về nghĩa với từ nào sau đây?", "Because of", "In spite of", "Due to", "Owing to", "B"),
        ],
    },

    # --- 51-60: Cấu trúc Dữ liệu & Giải thuật (Module 1 DSA) ---
    {
        "title": "Cấu trúc dữ liệu: Mảng và Danh sách liên kết",
        "description": "So sánh chi tiết giữa Mảng tĩnh (Array) và Danh sách liên kết (Linked List).",
        "cards": [
            ("Array Random Access", "Truy cập phần tử theo chỉ số index trong mảng đạt O(1) nhờ các ô nhớ liên tục."),
            ("Singly Linked List", "Danh sách liên kết đơn gồm các node chứa dữ liệu và con trỏ next trỏ đến phần tử kế tiếp."),
            ("Doubly Linked List", "Danh sách liên kết đôi có cả con trỏ next và prev cho phép duyệt hai chiều linh hoạt."),
            ("Insert at Head", "Chèn phần tử vào đầu danh sách liên kết chỉ mất O(1) thời gian mà không cần dời chỗ các phần tử."),
        ],
        "quiz": [
            ("Độ phức tạp thời gian khi truy cập một phần tử trong mảng qua chỉ mục index là bao nhiêu?", "O(1)", "O(log N)", "O(N)", "O(N^2)", "A"),
            ("Ưu điểm nổi bật của Danh sách liên kết so với Mảng tĩnh là gì?", "Truy cập ngẫu nhiên nhanh hơn", "Bộ nhớ luôn liên tục", "Chèn/xóa ở đầu danh sách đạt O(1)", "Không tốn thêm bộ nhớ cho con trỏ", "C"),
            ("Trong danh sách liên kết đôi, mỗi nút lưu trữ bao nhiêu con trỏ liên kết?", "0", "1 (next)", "2 (prev và next)", "3", "C"),
            ("Khi xóa phần tử đầu tiên của một mảng tĩnh kích thước N, ta mất độ phức tạp bao nhiêu?", "O(1)", "O(log N)", "O(N)", "O(1) amortized", "C"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Ngăn xếp (Stack LIFO)",
        "description": "Nguyên lý Last In First Out (LIFO), các thao tác Push/Pop và ứng dụng 2-Stack Undo/Redo.",
        "cards": [
            ("LIFO Principle", "Vào sau - Ra trước: phần tử nào được đưa vào ngăn xếp cuối cùng sẽ được lấy ra đầu tiên."),
            ("Push Operation", "Thao tác đẩy một phần tử mới vào đỉnh (top) của ngăn xếp với thời gian O(1)."),
            ("Pop Operation", "Thao tác loại bỏ và trả về phần tử đang ở đỉnh của ngăn xếp với thời gian O(1)."),
            ("Two-Stack Mechanism", "Mô hình sử dụng 2 Stack (Back Stack & Forward Stack) để triển khai tính năng Undo/Redo."),
        ],
        "quiz": [
            ("Ngăn xếp (Stack) hoạt động theo nguyên tắc trật tự nào?", "FIFO (First In First Out)", "LIFO (Last In First Out)", "Priority First", "Random Access", "B"),
            ("Thao tác lấy phần tử ra khỏi đỉnh của ngăn xếp gọi là gì?", "Enqueue", "Dequeue", "Push", "Pop", "D"),
            ("Trong tính năng thi trắc nghiệm Quiz của hệ thống, nút 'Quay lại' (Undo) hoạt động thế nào?", "Pop từ _back_stack và Push vào _forward_stack", "Xóa hết ngăn xếp", "Duyệt cây AVL", "Dequeue hàng đợi", "A"),
            ("Ứng dụng nào sau đây KHÔNG phù hợp sử dụng ngăn xếp Stack?", "Khử đệ quy và quản lý Call Stack", "Kiểm tra đóng mở ngoặc hợp lệ", "Hàng đợi in ấn văn phòng theo thứ tự nộp", "Thuật toán duyệt đồ thị theo chiều sâu (DFS)", "C"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Hàng đợi (Queue FIFO)",
        "description": "Nguyên lý First In First Out (FIFO), Enqueue/Dequeue và Hàng đợi học lặp lại 2 giai đoạn.",
        "cards": [
            ("FIFO Principle", "Vào trước - Ra trước: phần tử nào được thêm vào trước sẽ được phục vụ và xử lý trước."),
            ("Enqueue", "Thao tác đưa một phần tử mới vào cuối (rear) của hàng đợi với độ phức tạp O(1)."),
            ("Dequeue", "Thao tác lấy phần tử ở đầu (front) ra khỏi hàng đợi với độ phức tạp O(1)."),
            ("Two-Stage Study Queue", "Hàng đợi 2 giai đoạn: Giai đoạn 1 duyệt lượt đầu; thẻ chưa nhớ đưa vào đuôi hàng đợi ôn tập tiếp."),
        ],
        "quiz": [
            ("Hàng đợi (Queue) tiêu chuẩn hoạt động theo nguyên lý nào?", "LIFO", "FIFO", "FILO", "Random", "B"),
            ("Thao tác đưa một phần tử vào cuối hàng đợi gọi là gì?", "Pop", "Peek", "Enqueue", "Dequeue", "C"),
            ("Trong tính năng Học thẻ Flashcard, khi người dùng bấm 'Chưa nhớ', thẻ đó sẽ được xử lý ra sao?", "Xóa vĩnh viễn khỏi bộ thẻ", "Được Enqueue vào cuối hàng đợi để học lại", "Đẩy vào đỉnh Stack", "Đổi tên thẻ", "B"),
            ("Cấu trúc dữ liệu nào thường dùng để triển khai duyệt đồ thị theo chiều rộng (BFS)?", "Stack", "Queue", "Binary Search Tree", "Max Heap", "B"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Cây AVL & Cân bằng tự động",
        "description": "Cây nhị phân tìm kiếm tự cân bằng AVL, hệ số Balance Factor và 4 phép xoay cây cơ bản.",
        "cards": [
            ("AVL Balance Factor", "Hệ số cân bằng của mỗi nút = Chiều cao(cây con trái) - Chiều cao(cây con phải), luôn nằm trong {-1, 0, 1}."),
            ("Rotation Complexity", "Tất cả các phép xoay cây (Left, Right, Left-Right, Right-Left) đều đạt độ phức tạp thời gian O(1)."),
            ("Tree Height", "Cây AVL chứa N nút luôn duy trì chiều cao không vượt quá 1.44 * log2(N), đảm bảo tra cứu O(log N)."),
            ("Prefix Search O(log N + K)", "Nhờ thứ tự BST, tìm kiếm tiền tố cho phép cắt tỉa nhánh trong O(log N) và thu thập K phần tử thỏa mãn."),
        ],
        "quiz": [
            ("Hệ số cân bằng (Balance Factor) hợp lệ của mỗi nút trong Cây AVL chỉ được phép nhận các giá trị nào?", "{-2, 0, 2}", "{-1, 0, 1}", "{0, 1, 2}", "{Tùy ý}", "B"),
            ("Khi một nút bị lệch Trái - Phải (Left-Right Case), cây AVL thực hiện phép xoay nào?", "Xoay phải 1 lần", "Xoay trái tại nút con, rồi xoay phải tại nút cha", "Xoay trái 1 lần", "Không cần xoay", "B"),
            ("Độ phức tạp thời gian của một thao tác xoay cây AVL là bao nhiêu?", "O(1)", "O(log N)", "O(N)", "O(N log N)", "A"),
            ("Độ phức tạp của thuật toán tìm kiếm tiền tố (Prefix Search) trên Cây AVL là gì?", "O(N)", "O(log N + K)", "O(K^2)", "O(1)", "B"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Cây B-Tree và B+ Tree",
        "description": "Cấu trúc cây nhiều nhánh tối ưu hóa cho hệ thống đĩa từ và cơ sở dữ liệu quan hệ.",
        "cards": [
            ("Multi-way Tree", "B-Tree là cây tìm kiếm đa nhánh, mỗi nút có thể chứa nhiều khóa và nhiều con trỏ con."),
            ("Disk I/O Optimization", "B-Tree giảm thiểu số lần đọc ghi đĩa cứng nhờ nút có kích thước vừa khít một block đĩa."),
            ("B+ Tree Leaf Links", "B+ Tree chỉ lưu bản ghi thực tế ở nút lá, các lá được liên kết dạng danh sách nối hỗ trợ quét khoảng cực nhanh."),
            ("Database Indexing", "Hầu hết các hệ quản trị CSDL (MySQL InnoDB, PostgreSQL) sử dụng B+ Tree cho chỉ mục khóa chính."),
        ],
        "quiz": [
            ("Lý do chính khiến B-Tree và B+ Tree được ưa chuộng trong các hệ quản trị CSDL là gì?", "Dễ cài đặt bằng đệ quy", "Giảm thiểu số lần truy xuất đĩa cứng (Disk I/O)", "Tiết kiệm RAM hơn AVL", "Không cần cân bằng", "B"),
            ("Điểm khác biệt quan trọng của B+ Tree so với B-Tree chuẩn là gì?", "Mọi dữ liệu thực tế chỉ nằm ở các nút lá", "Không có cây con", "Chỉ có 2 nhánh con", "Không thể tìm kiếm nhị phân", "A"),
            ("Các nút lá trong cây B+ Tree được liên kết với nhau theo cấu trúc nào để tối ưu duyệt khoảng (Range Query)?", "Ngăn xếp", "Danh sách liên kết", "Cây con nhị phân", "Hàng đợi ưu tiên", "B"),
            ("Số lượng khóa tối đa trong một nút B-Tree bậc M là bao nhiêu?", "M", "M - 1", "2M", "M / 2", "B"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Heap và Hàng đợi ưu tiên",
        "description": "Cấu trúc Binary Heap (Min-Heap, Max-Heap) và cài đặt Hàng đợi ưu tiên (Priority Queue).",
        "cards": [
            ("Heap Property", "Trong Max-Heap, khóa của nút cha luôn lớn hơn hoặc bằng khóa của các nút con tương ứng."),
            ("Array Representation", "Heap thường biểu diễn bằng mảng: nút tại vị trí i có con trái tại 2i+1 và con phải tại 2i+2."),
            ("Extract-Max / Min", "Thao tác lấy phần tử ưu tiên cao nhất ở gốc mất O(1), tái cấu trúc Heapify mất O(log N)."),
            ("HeapSort", "Thuật toán sắp xếp sử dụng cấu trúc Heap với độ phức tạp luôn đảm bảo O(N log N) trong mọi trường hợp."),
        ],
        "quiz": [
            ("Trong một Min-Heap, phần tử có giá trị nhỏ nhất luôn nằm ở vị trí nào?", "Nút lá cuối cùng", "Nút gốc (root)", "Bất kỳ vị trí nào", "Con bên phải", "B"),
            ("Nếu nút hiện tại trong mảng Heap nằm ở chỉ số i (bắt đầu từ 0), chỉ số nút con trái là gì?", "2i", "2i + 1", "2i + 2", "i / 2", "B"),
            ("Độ phức tạp thời gian để xây dựng một Heap từ mảng N phần tử chưa sắp xếp (Build-Heap) là gì?", "O(N)", "O(N log N)", "O(N^2)", "O(log N)", "A"),
            ("Hàng đợi ưu tiên (Priority Queue) thường được cài đặt hiệu quả nhất bằng cấu trúc dữ liệu nào?", "Danh sách liên kết đơn", "Binary Heap", "Ngăn xếp LIFO", "Mảng không sắp xếp", "B"),
        ],
    },
    {
        "title": "Cấu trúc dữ liệu: Bảng băm (Hash Table)",
        "description": "Hàm băm (Hash Function), xử lý xung đột (Chaining vs Open Addressing) và độ phức tạp trung bình.",
        "cards": [
            ("Hash Function", "Hàm ánh xạ một khóa tùy ý (chuỗi, số lớn) thành chỉ số mảng nguyên có kích thước cố định."),
            ("Chaining Method", "Giải quyết xung đột băm bằng cách gắn danh sách liên kết tại mỗi ô bucket trong bảng."),
            ("Open Addressing", "Giải quyết xung đột bằng cách tìm kiếm vị trí trống tiếp theo (Linear Probing, Quadratic Probing)."),
            ("Load Factor", "Hệ số tải alpha = N / M (số phần tử chia kích thước bảng). Khi alpha vượt ngưỡng (0.75), bảng cần Rehashing."),
        ],
        "quiz": [
            ("Độ phức tạp thời gian trung bình của thao tác tra cứu trên Bảng băm (Hash Table) là bao nhiêu?", "O(1)", "O(log N)", "O(N)", "O(N log N)", "A"),
            ("Phương pháp giải quyết xung đột băm gắn một danh sách liên kết tại mỗi ô gọi là gì?", "Separate Chaining", "Linear Probing", "Double Hashing", "Quadratic Probing", "A"),
            ("Khi bảng băm bị quá tải (nhiều phần tử bị xung đột dồn vào 1 ô), độ phức tạp tệ nhất rơi xuống mức nào?", "O(1)", "O(log N)", "O(N)", "O(N^2)", "C"),
            ("Hệ số tải (Load Factor) được tính bằng công thức nào?", "Số phần tử / Kích thước bảng", "Kích thước bảng / Số phần tử", "Chiều cao cây / 2", "Số khóa trùng lặp", "A"),
        ],
    },
    {
        "title": "Thuật toán: Duyệt đồ thị BFS và DFS",
        "description": "Thuật toán tìm kiếm theo chiều rộng (BFS - Queue) và theo chiều sâu (DFS - Stack/Recursion).",
        "cards": [
            ("Breadth-First Search", "BFS duyệt đồ thị theo từng tầng láng giềng gần nhất, sử dụng hàng đợi Queue, tìm đường đi ngắn nhất đồ thị không trọng số."),
            ("Depth-First Search", "DFS thám hiểm nhánh đồ thị càng sâu càng tốt trước khi quay lui (Backtracking), sử dụng Stack hoặc đệ quy."),
            ("Graph Representations", "Đồ thị thường biểu diễn bằng Ma trận kề (Adjacency Matrix) hoặc Danh sách kề (Adjacency List)."),
            ("Time Complexity O(V + E)", "Cả BFS và DFS đều có độ phức tạp thời gian là O(V + E) khi dùng danh sách kề với V đỉnh và E cạnh."),
        ],
        "quiz": [
            ("Thuật toán nào dùng để tìm đường đi ngắn nhất giữa hai đỉnh trên đồ thị không có trọng số?", "DFS", "BFS", "Linear Search", "Bubble Sort", "B"),
            ("Thuật toán duyệt theo chiều sâu (DFS) thường sử dụng cấu trúc dữ liệu nào để lưu vết duyệt?", "Hàng đợi Queue", "Ngăn xếp Stack", "Bảng băm", "Binary Heap", "B"),
            ("Độ phức tạp thời gian của BFS khi biểu diễn đồ thị bằng Danh sách kề (V đỉnh, E cạnh) là gì?", "O(V * E)", "O(V + E)", "O(V^2)", "O(E^2)", "B"),
            ("Ứng dụng nào sau đây thường sử dụng thuật toán DFS?", "Sắp xếp Tô pô (Topological Sort)", "Tìm đường đi ngắn nhất không trọng số", "Phát sóng vô tuyến trong mạng LAN", "Tìm kiếm theo tầng gần nhất", "A"),
        ],
    },
    {
        "title": "Thuật toán: Sắp xếp QuickSort và MergeSort",
        "description": "So sánh 2 thuật toán sắp xếp kinh điển chia để trị (Divide and Conquer).",
        "cards": [
            ("QuickSort Pivot", "Chia mảng thành 2 nửa quanh một phần tử chốt (pivot), sắp xếp tại chỗ (in-place) với độ phức tạp trung bình O(N log N)."),
            ("QuickSort Worst-Case", "Trường hợp xấu nhất của QuickSort là O(N^2) khi chọn pivot tồi (mảng đã sắp xếp và chọn phần tử đầu/cuối)."),
            ("MergeSort Stability", "MergeSort chia đôi mảng đệ quy và trộn lại, luôn đảm bảo O(N log N) trong mọi trường hợp và có tính ổn định (stable)."),
            ("Space Complexity", "MergeSort tốn O(N) bộ nhớ phụ để trộn mảng, trong khi QuickSort chỉ tốn O(log N) bộ nhớ Call Stack."),
        ],
        "quiz": [
            ("Độ phức tạp thời gian trung bình của thuật toán QuickSort là gì?", "O(N)", "O(N log N)", "O(N^2)", "O(log N)", "B"),
            ("Thuật toán sắp xếp nào luôn đảm bảo thời gian chạy O(N log N) ngay cả trong trường hợp xấu nhất?", "QuickSort", "MergeSort", "Bubble Sort", "Insertion Sort", "B"),
            ("Nhược điểm lớn nhất của thuật toán MergeSort so với QuickSort khi sắp xếp mảng trong RAM là gì?", "Chạy chậm hơn gấp 10 lần", "Tốn thêm O(N) bộ nhớ phụ để trộn", "Không có tính ổn định", "Dễ rơi vào O(N^2)", "B"),
            ("Tính ổn định (Stable Sort) của một thuật toán sắp xếp nghĩa là gì?", "Luôn chạy dưới 1 giây", "Giữ nguyên thứ tự tương đối của các phần tử có cùng giá trị", "Không dùng đệ quy", "Chỉ chạy trên mảng số nguyên", "B"),
        ],
    },
    {
        "title": "Thuật toán: Quy hoạch động (Dynamic Programming)",
        "description": "Nguyên lý tối ưu con, bài toán gối nhau (Overlapping Subproblems) và kỹ thuật Memoization/Tabulation.",
        "cards": [
            ("Optimal Substructure", "Cấu trúc tối ưu con: nghiệm tối ưu của bài toán lớn được xây dựng từ nghiệm tối ưu của các bài toán con nhỏ hơn."),
            ("Overlapping Subproblems", "Các bài toán con gối nhau bị tính toán lặp đi lặp lại nhiều lần nếu dùng đệ quy ngây thơ."),
            ("Memoization (Top-down)", "Kỹ thuật ghi nhớ kết quả bài toán con vào mảng/bảng băm trong quá trình đệ quy từ trên xuống."),
            ("Tabulation (Bottom-up)", "Kỹ thuật lặp giải quyết tuần tự từ bài toán cơ sở nhỏ nhất và điền bảng dần lên bài toán lớn."),
        ],
        "quiz": [
            ("Hai đặc trưng cốt lõi để một bài toán có thể giải được bằng Quy hoạch động là gì?", "Đồ thị và Cây", "Cấu trúc tối ưu con & Các bài toán con gối nhau", "Sắp xếp và Tìm kiếm", "Tham lam và Chia để trị", "B"),
            ("Kỹ thuật lưu trữ kết quả tính toán đệ quy vào bảng nhớ để tránh tính lại gọi là gì?", "Branch and Bound", "Memoization", "Backtracking", "Divide and Conquer", "B"),
            ("Bài toán kinh điển nào sau đây thường được giải hiệu quả bằng Quy hoạch động?", "Tìm kiếm nhị phân", "Bài toán Cái ba lô (0/1 Knapsack)", "Thuật toán tìm kiếm tuyến tính", "Kiểm tra số chẵn lẻ", "B"),
            ("Khác biệt cơ bản giữa Tabulation và Memoization là gì?", "Tabulation chạy từ dưới lên bằng vòng lặp, Memoization chạy từ trên xuống bằng đệ quy", "Tabulation tốn nhiều RAM hơn gấp 100 lần", "Tabulation không thể giải bài toán cái ba lô", "Memoization không dùng bộ nhớ", "A"),
        ],
    },

    # --- 61-70: Lập trình Python & Backend Web ---
    {
        "title": "Python: Cú pháp lõi & Data Structures",
        "description": "Kiểu dữ liệu Mutable vs Immutable, List Comprehension, Dict và Set trong Python.",
        "cards": [
            ("Mutable vs Immutable", "List, Dict, Set có thể thay đổi nội dung (Mutable); Tuple, Str, Int, Float bất biến (Immutable)."),
            ("List Comprehension", "Cú pháp ngắn gọn, tối ưu tốc độ để tạo danh sách mới dựa trên danh sách có sẵn [x for x in list if cond]."),
            ("Dict Hash Table", "Dict trong Python cài đặt bằng Bảng băm (Hash Table) giúp tra cứu key trong thời gian O(1) trung bình."),
            ("Set Operations", "Tập hợp Set loại bỏ trùng lặp tự động và hỗ trợ các phép toán tập hợp (union, intersection, difference)."),
        ],
        "quiz": [
            ("Kiểu dữ liệu nào sau đây trong Python là BẤT BIẾN (Immutable)?", "List", "Dictionary", "Tuple", "Set", "C"),
            ("Độ phức tạp thời gian khi kiểm tra phần tử 'x in my_set' trong Set là bao nhiêu?", "O(1) trung bình", "O(N)", "O(log N)", "O(N^2)", "A"),
            ("Kết quả của biểu thức: [x * 2 for x in range(3)] là gì?", "[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "[1, 2, 3]", "A"),
            ("Phương thức nào dùng để lấy giá trị trong Dict mà không bị văng lỗi KeyError nếu key không tồn tại?", "dict.search()", "dict.get(key, default)", "dict.find()", "dict.lookup()", "B"),
        ],
    },
    {
        "title": "Python: Lập trình Hướng đối tượng (OOP)",
        "description": "4 trụ cột OOP trong Python: Đóng gói, Kế thừa, Đa hình và Trừu tượng hóa.",
        "cards": [
            ("Encapsulation", "Đóng gói dữ liệu và phương thức bên trong class; quy ước biến private bằng dấu gạch dưới (_ hoặc __)."),
            ("Inheritance", "Kế thừa cho phép lớp con tái sử dụng và mở rộng các thuộc tính, phương thức của lớp cha."),
            ("Polymorphism", "Tính đa hình cho phép các đối tượng thuộc các lớp khác nhau cùng phản hồi một phương thức chung."),
            ("Dunder Methods", "Các phương thức đặc biệt hai gạch dưới (__init__, __str__, __repr__, __len__) tùy biến hành vi của đối tượng."),
        ],
        "quiz": [
            ("Phương thức khởi tạo (Constructor) của một class trong Python có tên là gì?", "__start__", "__init__", "__create__", "__new__", "B"),
            ("Từ khóa nào được sử dụng để gọi phương thức của lớp cha trong lớp con?", "this", "base", "super()", "parent", "C"),
            ("Quy ước đặt tên biến có một dấu gạch dưới ở đầu (_name) trong Python thể hiện điều gì?", "Biến công khai toàn cầu", "Biến nội bộ (Protected/Private theo quy ước)", "Hằng số bất biến", "Lỗi cú pháp", "B"),
            ("Trụ cột OOP nào cho phép định nghĩa các lớp con kế thừa hành vi từ lớp cha?", "Đóng gói", "Kế thừa", "Trừu tượng", "Đa hình", "B"),
        ],
    },
    {
        "title": "Python: Decorators & Generators",
        "description": "Cơ chế hàm bậc cao (First-class functions), Decorator bọc logic và Generator tiết kiệm bộ nhớ với yield.",
        "cards": [
            ("First-Class Functions", "Hàm trong Python có thể được truyền như tham số, gán cho biến hoặc trả về từ một hàm khác."),
            ("Decorator Pattern", "Decorator (@decorator) dùng để bổ sung tính năng (đo thời gian, ghi log, xác thực) cho hàm mà không sửa code hàm đó."),
            ("Generators with Yield", "Generator tạo ra iterator sinh giá trị từng bước bằng từ khóa 'yield', không tải toàn bộ dữ liệu vào RAM."),
            ("Memory Efficiency", "Duyệt tệp tin hàng triệu dòng bằng Generator chỉ tiêu tốn lượng RAM không đổi (O(1) memory footprint)."),
        ],
        "quiz": [
            ("Từ khóa nào trong Python biến một hàm bình thường thành một Generator?", "return", "yield", "generate", "produce", "B"),
            ("Ký hiệu nào đứng trước tên hàm được dùng để áp dụng Decorator trong Python?", "&", "@", "#", "$", "B"),
            ("Ưu điểm vượt trội của Generator khi đọc file dữ liệu lớn 10GB là gì?", "Chạy nhanh hơn gấp 100 lần", "Không nạp toàn bộ file vào RAM gây tràn bộ nhớ", "Tự động dịch sang mã máy C", "Không cần mở file", "B"),
            ("Hàm functools.wraps thường được dùng bên trong Decorator nhằm mục đích gì?", "Tăng tốc CPU", "Giữ nguyên tên hàm và docstring gốc của hàm được bọc", "Khóa biến", "Bỏ qua lỗi runtime", "B"),
        ],
    },
    {
        "title": "Python: Lập trình Bất đồng bộ Asyncio",
        "description": "Event Loop, từ khóa async/await, coroutine và xử lý non-blocking I/O.",
        "cards": [
            ("Event Loop", "Vòng lặp sự kiện quản lý và phân phối việc thực thi các tác vụ bất đồng bộ trên một luồng đơn."),
            ("async and await", "Từ khóa 'async def' định nghĩa coroutine; 'await' tạm dừng coroutine chờ tác vụ I/O hoàn thành."),
            ("Non-blocking I/O", "Khi chờ phản hồi mạng hoặc đọc đĩa, luồng CPU không bị chặn mà chuyển sang xử lý tác vụ khác."),
            ("asyncio.gather", "Thực thi đồng thời nhiều coroutine song song và thu thập kết quả trả về trong một mảng."),
        ],
        "quiz": [
            ("Từ khóa nào dùng để khai báo một hàm bất đồng bộ (coroutine) trong Python?", "def async", "async def", "promise def", "thread def", "B"),
            ("Thành phần nào chịu trách nhiệm điều phối và lên lịch thực thi các tác vụ async trong asyncio?", "Thread Pool", "Event Loop", "Garbage Collector", "Compiler", "B"),
            ("Lập trình bất đồng bộ (Async I/O) phát huy hiệu quả cao nhất trong bài toán nào sau đây?", "Tính toán ma trận số học nặng (CPU-bound)", "Gọi API mạng và truy vấn CSDL (I/O-bound)", "Đào tiền ảo", "Nén video 4K", "B"),
            ("Lệnh nào dùng để chờ nhiều tác vụ async chạy đồng thời và gom kết quả?", "asyncio.gather()", "asyncio.stop()", "asyncio.sleep()", "asyncio.kill()", "A"),
        ],
    },
    {
        "title": "Backend Web: Framework FastAPI & Pydantic",
        "description": "Kiến trúc hiện đại của FastAPI, kiểm thực kiểu dữ liệu với Pydantic và sinh tài liệu OpenAPI tự động.",
        "cards": [
            ("FastAPI Performance", "Xây dựng trên nền tảng Starlette và Pydantic, FastAPI là một trong những framework Python nhanh nhất hiện nay."),
            ("Pydantic Validation", "Pydantic tự động ép kiểu và xác thực dữ liệu đầu vào theo type hints, báo lỗi 422 chi tiết khi sai định dạng."),
            ("Automatic Swagger UI", "FastAPI tự động sinh tài liệu API tương tác tại endpoint /docs (Swagger UI) và /redoc theo chuẩn OpenAPI."),
            ("Dependency Injection", "Hệ thống phụ thuộc (Depends) mạnh mẽ giúp tái sử dụng logic xác thực, kết nối CSDL và phân quyền."),
        ],
        "quiz": [
            ("Thư viện nào được FastAPI sử dụng để xác thực và chuẩn hóa dữ liệu Request Body?", "SQLAlchemy", "Pydantic", "Django ORM", "Requests", "B"),
            ("Đường dẫn mặc định để xem tài liệu tương tác Swagger UI trong ứng dụng FastAPI là gì?", "/swagger", "/docs", "/api/spec", "/info", "B"),
            ("Mã trạng thái HTTP nào được FastAPI tự động trả về khi dữ liệu đầu vào không hợp lệ với schema Pydantic?", "400 Bad Request", "404 Not Found", "422 Unprocessable Entity", "500 Server Error", "C"),
            ("Cơ chế nào trong FastAPI cho phép chia sẻ kết nối cơ sở dữ liệu hoặc logic xác thực token giữa các endpoint?", "Global variables", "Dependency Injection (Depends)", "Hardcoding", "Eval", "B"),
        ],
    },
    {
        "title": "Backend Web: Thiết kế chuẩn RESTful API",
        "description": "Các phương thức HTTP (GET, POST, PUT, DELETE), mã trạng thái HTTP Status Codes và nguyên lý REST.",
        "cards": [
            ("HTTP Methods", "GET (lấy dữ liệu), POST (tạo mới), PUT (thay thế toàn bộ), PATCH (sửa một phần), DELETE (xóa bản ghi)."),
            ("Idempotency", "Tính bất biến: một phương thức gọi nhiều lần cho cùng kết quả (GET, PUT, DELETE là idempotent; POST thì không)."),
            ("HTTP Status Codes", "2xx (Thành công), 3xx (Chuyển hướng), 4xx (Lỗi từ phía client), 5xx (Lỗi nội bộ máy chủ)."),
            ("Stateless Principle", "Mỗi request gửi lên server phải chứa đầy đủ mọi thông tin cần thiết để xử lý, không lưu ngữ cảnh client trên server."),
        ],
        "quiz": [
            ("Phương thức HTTP nào được quy chuẩn dùng để tạo mới một tài nguyên trên server?", "GET", "POST", "PUT", "DELETE", "B"),
            ("Mã trạng thái HTTP nào biểu thị việc client chưa đăng nhập hoặc token không hợp lệ?", "401 Unauthorized", "403 Forbidden", "404 Not Found", "502 Bad Gateway", "A"),
            ("Phương thức HTTP nào KHÔNG có tính Idempotent (mỗi lần gọi có thể tạo ra bản ghi mới)?", "GET", "PUT", "DELETE", "POST", "D"),
            ("Mã trạng thái 404 Not Found có nghĩa là gì?", "Máy chủ bị sập", "Không tìm thấy tài nguyên được yêu cầu", "Dữ liệu bị cấm truy cập", "Hết thời gian chờ", "B"),
        ],
    },
    {
        "title": "Cơ sở dữ liệu: Tối ưu Truy vấn & Indexing",
        "description": "Chỉ mục B-Tree, Explain Plan, chuẩn hóa dữ liệu (Normal Forms) và giao dịch ACID.",
        "cards": [
            ("B-Tree Index", "Chỉ mục giúp tăng tốc độ tìm kiếm bản ghi từ O(N) quét bảng toàn bộ (Table Scan) lên O(log N)."),
            ("ACID Properties", "Tính chất giao dịch: Atomicity (Nguyên tử), Consistency (Nhất quán), Isolation (Cô lập), Durability (Bền vững)."),
            ("Explain Analyze", "Lệnh phân tích kế hoạch thực thi truy vấn của CSDL để phát hiện các câu lệnh chạy chậm."),
            ("Normalization", "Quá trình chuẩn hóa bảng dữ liệu (1NF, 2NF, 3NF) nhằm loại bỏ sự dư thừa và bất thường khi ghi/sửa."),
        ],
        "quiz": [
            ("Chữ 'A' trong từ viết tắt ACID của giao dịch cơ sở dữ liệu đại diện cho từ nào?", "Accuracy", "Atomicity (Nguyên tử)", "Availability", "Authentication", "B"),
            ("Chỉ mục (Index) trên cơ sở dữ liệu giúp tăng tốc thao tác đọc nhưng gây nhược điểm gì?", "Làm chậm thao tác ghi/sửa (INSERT, UPDATE) và tốn thêm dung lượng đĩa", "Không thể dùng mệnh đề WHERE", "Làm mất dữ liệu", "Chỉ dùng được cho kiểu chuỗi", "A"),
            ("Câu lệnh nào trong SQL dùng để xem kế hoạch thực thi và chi phí của một truy vấn?", "SHOW QUERY", "EXPLAIN / EXPLAIN ANALYZE", "DESCRIBE RUN", "TEST SELECT", "B"),
            ("Quá trình phân chia bảng để tránh trùng lặp dữ liệu và dị thường cập nhật gọi là gì?", "Denormalization", "Normalization", "Virtualization", "Compilation", "B"),
        ],
    },
    {
        "title": "DevOps: Containerization với Docker",
        "description": "Khái niệm Image, Container, Dockerfile, Docker Compose và cô lập môi trường ứng dụng.",
        "cards": [
            ("Image vs Container", "Image là khuôn mẫu đóng gói ứng dụng bất biến (blueprint); Container là phiên bản thực thi đang chạy của Image."),
            ("Dockerfile", "Tệp văn bản chứa các chỉ thị từng bước (FROM, RUN, COPY, CMD) để tự động hóa việc đóng gói Image."),
            ("Port Mapping", "Cơ chế ánh xạ cổng mạng giữa máy host và container (ví dụ: -p 8000:8000) để truy cập dịch vụ."),
            ("Docker Volumes", "Giải pháp lưu trữ dữ liệu bền vững (persistent data), không bị mất đi khi container bị xóa."),
        ],
        "quiz": [
            ("Khác biệt cơ bản giữa Docker Image và Docker Container là gì?", "Image là khuôn mẫu tĩnh, Container là thể hiện đang chạy trong bộ nhớ", "Image chạy nhanh hơn Container", "Container là file văn bản", "Không có khác biệt", "A"),
            ("Chỉ thị nào trong Dockerfile dùng để chỉ định câu lệnh mặc định thực thi khi container khởi động?", "RUN", "FROM", "CMD / ENTRYPOINT", "ENV", "C"),
            ("Cơ chế nào trong Docker dùng để lưu trữ dữ liệu an toàn ngay cả khi container bị hủy?", "Layering", "Docker Volume", "RAM disk", "Docker Cache", "B"),
            ("Công cụ nào của Docker cho phép định nghĩa và chạy nhiều container cùng lúc qua file YAML?", "Docker Swarm", "Docker Compose", "Docker Hub", "Docker Registry", "B"),
        ],
    },
    {
        "title": "Công cụ: Quản lý mã nguồn với Git",
        "description": "Các lệnh Git nâng cao, quy trình phân nhánh (Branching), Rebase vs Merge và xử lý Conflict.",
        "cards": [
            ("Git Commit", "Lưu lại một bức ảnh chụp nhanh (snapshot) trạng thái các tệp tin trong thư mục làm việc."),
            ("Merge vs Rebase", "Merge tạo commit hợp nhất lịch sử; Rebase dời gốc nhánh làm sạch lịch sử thành một đường thẳng."),
            ("Git Stash", "Lưu tạm các thay đổi chưa commit vào ngăn xếp an toàn để chuyển nhánh khẩn cấp."),
            ("Merge Conflict", "Xung đột xảy ra khi hai nhánh cùng chỉnh sửa những dòng mã giống nhau trên cùng một tệp tin."),
        ],
        "quiz": [
            ("Lệnh nào trong Git cho phép lưu tạm các thay đổi đang làm dở mà không cần tạo commit?", "git stash", "git save", "git pause", "git hide", "A"),
            ("Lệnh nào dùng để tạo và chuyển ngay sang một nhánh mới trong Git?", "git branch new_branch", "git checkout -b new_branch", "git push origin", "git merge", "B"),
            ("Sự khác biệt khi dùng 'git rebase' thay vì 'git merge' là gì?", "Tạo ra lịch sử commit tuyến tính và sạch hơn", "Luôn an toàn hơn trên nhánh công khai", "Không bao giờ bị conflict", "Chỉ dùng cho file ảnh", "A"),
            ("Lệnh nào hiển thị lịch sử các lần commit trong repository?", "git status", "git log", "git diff", "git blame", "B"),
        ],
    },
    {
        "title": "Kiến trúc phần mềm: Clean Code & Design Patterns",
        "description": "Nguyên lý SOLID, các mẫu thiết kế hướng đối tượng (Singleton, Factory, Observer, Strategy).",
        "cards": [
            ("Single Responsibility", "Nguyên lý S trong SOLID: Một lớp chỉ nên có một lý do duy nhất để thay đổi."),
            ("Singleton Pattern", "Mẫu thiết kế đảm bảo một lớp chỉ có duy nhất một thể hiện (instance) toàn cục trong ứng dụng."),
            ("Factory Pattern", "Mẫu tạo dựng ủy thác việc khởi tạo đối tượng cho các lớp con thông qua phương thức chung."),
            ("Observer Pattern", "Mẫu thiết kế định nghĩa mối quan hệ một-nhiều: khi một đối tượng đổi trạng thái, các đối tượng phụ thuộc đều được thông báo."),
        ],
        "quiz": [
            ("Nguyên lý 'Single Responsibility' (chữ S trong SOLID) yêu cầu điều gì?", "Một class chỉ nên đảm nhận một trách nhiệm duy nhất", "Một phần mềm chỉ có một dòng code", "Chỉ dùng một hàm main", "Tất cả các biến đều là hằng số", "A"),
            ("Design Pattern nào đảm bảo một class chỉ có đúng một thể hiện duy nhất trong suốt vòng đời ứng dụng?", "Factory", "Observer", "Singleton", "Adapter", "C"),
            ("Mẫu thiết kế nào được dùng khi hệ thống cần thông báo tự động cho hàng loạt thành phần khi có sự kiện mới?", "Observer", "Builder", "Singleton", "Decorator", "A"),
            ("Mẫu Strategy Pattern cho phép lập trình viên làm gì?", "Thay đổi linh hoạt thuật toán xử lý tại thời điểm chạy (runtime)", "Tăng tốc độ CPU", "Bảo mật mật khẩu", "Tạo giao diện", "A"),
        ],
    },

    # --- 71-80: Hệ điều hành & Kiến trúc Máy tính ---
    {
        "title": "Hệ điều hành: Tiến trình & Đa luồng (Thread)",
        "description": "Phân biệt Process và Thread, không gian địa chỉ ảo, Context Switch và đa nhiệm.",
        "cards": [
            ("Process vs Thread", "Tiến trình (Process) có không gian bộ nhớ độc lập; Luồng (Thread) là đơn vị thực thi nhẹ chia sẻ chung bộ nhớ tiến trình."),
            ("Context Switch", "Quá trình CPU lưu trạng thái luồng cũ và nạp trạng thái luồng mới để thực thi đa nhiệm."),
            ("Process States", "Các trạng thái của tiến trình: Ready (Sẵn sàng), Running (Đang chạy), Blocked/Waiting (Đang chờ I/O)."),
            ("Thread Safety", "Tính an toàn luồng: mã nguồn thực thi chính xác khi nhiều luồng truy cập dữ liệu đồng thời."),
        ],
        "quiz": [
            ("Sự khác biệt lớn nhất về mặt bộ nhớ giữa Tiến trình (Process) và Luồng (Thread) là gì?", "Các luồng trong cùng tiến trình chia sẻ chung vùng nhớ, còn các tiến trình có vùng nhớ riêng biệt", "Luồng tốn nhiều RAM hơn tiến trình", "Tiến trình không có mã code", "Luồng không thể chạy trên CPU", "A"),
            ("Quá trình CPU chuyển đổi qua lại giữa các tiến trình để tạo cảm giác chạy song song gọi là gì?", "Compilation", "Context Switch (Chuyển ngữ cảnh)", "Paging", "Deadlock", "B"),
            ("Khi một tiến trình đang chờ dữ liệu đọc từ đĩa cứng, nó ở trạng thái nào?", "Running", "Ready", "Blocked / Waiting", "Terminated", "C"),
            ("Đơn vị nhỏ nhất của quá trình thực thi mà hệ điều hành có thể lập lịch trên CPU là gì?", "Chương trình (Program)", "Luồng (Thread)", "Tệp tin (File)", "Lệnh nhảy (Jump)", "B"),
        ],
    },
    {
        "title": "Hệ điều hành: Đồng bộ hóa Mutex & Semaphore",
        "description": "Miền găng (Critical Section), tranh chấp tài nguyên (Race Condition) và công cụ đồng bộ hóa.",
        "cards": [
            ("Race Condition", "Hiện tượng tranh chấp dữ liệu khi nhiều luồng cùng đọc ghi đồng thời dẫn đến kết quả sai lệch."),
            ("Critical Section", "Đoạn mã truy cập tài nguyên dùng chung chỉ được phép có tối đa một luồng thực thi tại một thời điểm."),
            ("Mutex Lock", "Khóa loại trừ tương hỗ: luồng nào giữ khóa mới được vào miền găng, luồng khác phải chờ."),
            ("Counting Semaphore", "Biến đếm đồng bộ kiểm soát quyền truy cập đồng thời của một số lượng luồng nhất định vào tài nguyên."),
        ],
        "quiz": [
            ("Tình huống hai luồng cùng cộng dồn vào một biến toàn cục dẫn đến kết quả bị mất mát gọi là gì?", "Deadlock", "Race Condition", "Starvation", "Paging", "B"),
            ("Công cụ đồng bộ hóa nào hoạt động như một chiếc chìa khóa duy nhất: chỉ ai cầm khóa mới được vào phòng?", "Mutex", "Thread Pool", "Pipeline", "Compiler", "A"),
            ("Khác biệt chính giữa Mutex và Counting Semaphore là gì?", "Mutex chỉ cho phép 1 luồng duy nhất truy cập, Semaphore cho phép số lượng N luồng đồng thời", "Mutex chạy nhanh hơn 100 lần", "Semaphore không thể dùng trong C++", "Mutex chỉ dùng cho file", "A"),
            ("Vùng mã nguồn truy cập vào tài nguyên dùng chung cần được bảo vệ gọi là gì?", "Free Section", "Critical Section (Miền găng)", "Dead Zone", "Buffer", "B"),
        ],
    },
    {
        "title": "Hệ điều hành: Bộ nhớ ảo & Phân trang",
        "description": "Không gian địa chỉ ảo (Virtual Address Space), bảng trang (Page Table), TLB và lỗi trang (Page Fault).",
        "cards": [
            ("Virtual Memory", "Kỹ thuật cho phép thực thi chương trình có dung lượng lớn hơn bộ nhớ RAM vật lý thực tế."),
            ("Paging", "Chia bộ nhớ ảo thành các trang (Pages) kích thước cố định và RAM thành các khung trang (Frames)."),
            ("Page Fault", "Ngắt phát sinh khi CPU truy cập vào một trang nhớ chưa được nạp sẵn trong RAM vật lý."),
            ("Translation Lookaside Buffer", "Bộ nhớ đệm phần cứng TLB tăng tốc độ tra cứu ánh xạ địa chỉ ảo sang địa chỉ vật lý."),
        ],
        "quiz": [
            ("Lỗi trang (Page Fault) xảy ra trong trường hợp nào sau đây?", "Khi trang nhớ được yêu cầu chưa có trong RAM và phải nạp từ đĩa cứng", "Khi máy tính bị virus", "Khi bộ nhớ RAM bị hỏng vật lý", "Khi chia cho số 0", "A"),
            ("Kỹ thuật chia bộ nhớ ảo thành các khối kích thước cố định (thường là 4KB) gọi là gì?", "Segmentation", "Paging (Phân trang)", "Swapping", "Fragmentation", "B"),
            ("Bộ nhớ đệm phần cứng tốc độ cao dùng để lưu vết ánh xạ địa chỉ ảo sang vật lý gọi là gì?", "L1 Cache", "TLB (Translation Lookaside Buffer)", "Registers", "ROM", "B"),
            ("Lợi ích cốt lõi của Bộ nhớ ảo (Virtual Memory) là gì?", "Cho phép chạy các ứng dụng đòi hỏi nhiều bộ nhớ hơn dung lượng RAM thực", "Tăng tốc độ xung nhịp CPU", "Bảo vệ máy tính khỏi sét đánh", "Không cần đĩa cứng", "A"),
        ],
    },
    {
        "title": "Hệ điều hành: Hiện tượng Bế tắc (Deadlock)",
        "description": "4 điều kiện Coffman gây bế tắc, đồ thị cấp phát tài nguyên và thuật toán Banker.",
        "cards": [
            ("Deadlock Definition", "Bế tắc: trạng thái hai hoặc nhiều tiến trình vĩnh viễn chờ đợi tài nguyên do chính các tiến trình kia nắm giữ."),
            ("Mutual Exclusion", "Điều kiện 1: Tài nguyên không thể chia sẻ đồng thời, chỉ một tiến trình được sử dụng tại một thời điểm."),
            ("Hold and Wait", "Điều kiện 2: Tiến trình đang giữ một tài nguyên và tiếp tục yêu cầu thêm tài nguyên mới đang bị giữ."),
            ("Circular Wait", "Điều kiện 4: Tồn tại chu trình chờ đợi khép kín giữa các tiến trình (P1 chờ P2, P2 chờ P3, P3 chờ P1)."),
        ],
        "quiz": [
            ("Có bao nhiêu điều kiện Coffman phải đồng thời xảy ra để dẫn đến hiện tượng Bế tắc (Deadlock)?", "2 điều kiện", "3 điều kiện", "4 điều kiện", "5 điều kiện", "C"),
            ("Điều kiện nào sau đây KHÔNG phải là một trong các điều kiện gây Deadlock?", "Loại trừ tương hỗ (Mutual Exclusion)", "Giữ và chờ (Hold and Wait)", "Thu hồi tài nguyên cưỡng chế (Preemption)", "Chờ đợi vòng tròn (Circular Wait)", "C"),
            ("Thuật toán kinh điển nào được Dijkstra đề xuất nhằm phòng tránh bế tắc trong hệ điều hành?", "Thuật toán Banker", "Thuật toán Dijkstra tìm đường", "Thuật toán QuickSort", "Thuật toán Round-Robin", "A"),
            ("Cách đơn giản nhất để phá vỡ hiện tượng Chờ đợi vòng tròn (Circular Wait) là gì?", "Đánh số thứ tự các tài nguyên và bắt buộc xin cấp phát theo thứ tự tăng dần", "Tắt máy tính", "Tăng dung lượng RAM", "Dùng đa luồng", "A"),
        ],
    },
    {
        "title": "Kiến trúc máy tính: Mô hình Von Neumann",
        "description": "Các thành phần CPU (ALU, CU, Registers), Bus dữ liệu và chu trình Fetch-Decode-Execute.",
        "cards": [
            ("Von Neumann Architecture", "Kiến trúc máy tính dùng chung bộ nhớ cho cả dữ liệu và tập lệnh nhị phân."),
            ("ALU (Arithmetic Logic Unit)", "Khối số học và logic thực hiện các phép toán tính cộng, trừ, AND, OR, NOT."),
            ("Control Unit (CU)", "Khối điều khiển giải mã lệnh và điều phối tín hiệu đến các thành phần phần cứng."),
            ("Instruction Cycle", "Chu trình lệnh gồm 3 bước tuần tự: Nạp lệnh (Fetch) -> Giải mã (Decode) -> Thực thi (Execute)."),
        ],
        "quiz": [
            ("Đặc điểm nổi bật nhất của kiến trúc máy tính Von Neumann là gì?", "Dữ liệu và tập lệnh chương trình được lưu chung trong cùng một bộ nhớ", "CPU không có thanh ghi", "Không dùng hệ nhị phân", "Mỗi chương trình có một CPU riêng", "A"),
            ("Bộ phận nào trong CPU chịu trách nhiệm thực hiện các phép tính số học (+, -) và logic?", "CU (Control Unit)", "ALU (Arithmetic Logic Unit)", "Cache L3", "Bus điều khiển", "B"),
            ("Chu trình xử lý lệnh của CPU diễn ra theo thứ tự chuẩn nào?", "Fetch -> Decode -> Execute", "Execute -> Fetch -> Decode", "Decode -> Execute -> Fetch", "Fetch -> Execute -> Decode", "A"),
            ("Thanh ghi con trỏ lệnh (Program Counter - PC) có nhiệm vụ gì?", "Lưu trữ kết quả phép tính", "Lưu địa chỉ của lệnh tiếp theo cần được nạp để thực thi", "Đếm số lần khởi động máy", "Kiểm soát nhiệt độ CPU", "B"),
        ],
    },
    {
        "title": "Kiến trúc máy tính: Hệ thống Cache Memory",
        "description": "Phân cấp bộ nhớ, nguyên lý cục bộ (Locality of Reference), Cache Hit/Miss và Cache L1/L2/L3.",
        "cards": [
            ("Principle of Locality", "Nguyên lý cục bộ: theo thời gian (vừa dùng sẽ sớm dùng lại) và theo không gian (các ô nhớ liền kề dễ được truy cập)."),
            ("Cache Hierarchy", "Phân cấp: L1 (nhỏ nhất, nhanh nhất, nằm sát nhân CPU) -> L2 -> L3 (lớn hơn, chia sẻ chung giữa các nhân)."),
            ("Cache Hit vs Miss", "Cache Hit: tìm thấy dữ liệu trong cache; Cache Miss: không có, phải tốn thời gian truy cập xuống RAM."),
            ("Cache Coherence", "Tính nhất quán bộ nhớ đệm trong hệ thống đa nhân: đảm bảo dữ liệu trên các cache nhân không bị mâu thuẫn."),
        ],
        "quiz": [
            ("Nguyên lý cơ bản nào cho phép bộ nhớ đệm Cache hoạt động hiệu quả vượt bậc?", "Nguyên lý bất định Heisenberg", "Nguyên lý cục bộ (Locality of Reference)", "Định luật bảo toàn năng lượng", "Định luật Moore", "B"),
            ("Cấp độ bộ nhớ đệm nào có tốc độ truy xuất nhanh nhất nhưng dung lượng nhỏ nhất?", "L1 Cache", "L2 Cache", "L3 Cache", "Bộ nhớ RAM", "A"),
            ("Tình huống khi CPU cần dữ liệu nhưng không tìm thấy trong Cache được gọi là gì?", "Cache Hit", "Cache Miss", "Cache Overflow", "Cache Fault", "B"),
            ("Khi CPU ghi dữ liệu mới, chính sách ghi cập nhật ngay lập tức xuống cả RAM gọi là gì?", "Write-Back", "Write-Through", "Write-Allocate", "Write-Around", "B"),
        ],
    },
    {
        "title": "Hệ điều hành: Hệ thống Tệp tin (File Systems)",
        "description": "Cấu trúc Inode, bảng phân vùng FAT, NTFS, Ext4, quyền truy cập tệp tin (File Permissions).",
        "cards": [
            ("Inode Structure", "Cấu trúc dữ liệu trong hệ thống tệp Unix lưu metadata (kích thước, quyền, con trỏ khối) của tệp tin."),
            ("Journaling File System", "Hệ thống tệp có nhật ký (NTFS, Ext4) ghi lại thao tác trước khi thực hiện để phục hồi sau khi mất điện đột ngột."),
            ("File Permissions", "Quyền truy cập trên Linux gồm Đọc (r=4), Ghi (w=2), Thực thi (x=1) phân bổ cho Owner, Group, Others."),
            ("Directory Tree", "Tổ chức thư mục dạng cây phân cấp bắt đầu từ thư mục gốc (root / trong Unix hoặc C:\\ trong Windows)."),
        ],
        "quiz": [
            ("Trong hệ điều hành Linux/Unix, cấu trúc dữ liệu nào lưu trữ metadata và thông tin vị trí đĩa của tệp tin?", "Inode", "FAT Table", "Master Boot Record", "Registry", "A"),
            ("Hệ thống tệp có tính năng 'Journaling' (như Ext4, NTFS) mang lại lợi ích gì?", "Tăng dung lượng đĩa gấp đôi", "Ghi nhật ký thao tác để dễ dàng phục hồi dữ liệu khi mất điện đột ngột", "Tự động xóa virus", "Không cần format", "B"),
            ("Quyền truy cập tệp tin 'chmod 755 file.sh' trên Linux cấp quyền gì cho Owner (chủ sở hữu)?", "Chỉ đọc (r)", "Chỉ thực thi (x)", "Toàn quyền đọc, ghi và thực thi (rwx = 7)", "Không có quyền gì", "C"),
            ("Tệp tin đặc biệt trong Linux đại diện cho con trỏ liên kết đến tệp khác gọi là gì?", "Symbolic Link (Symlink)", "Hard Sector", "Cluster", "Partition", "A"),
        ],
    },
    {
        "title": "Hệ điều hành: Lời gọi hệ thống (System Calls)",
        "description": "Chuyển đổi User Mode sang Kernel Mode, các hàm fork, exec, read, write trong Unix.",
        "cards": [
            ("User Mode vs Kernel Mode", "Chế độ người dùng bị giới hạn quyền truy cập phần cứng; Chế độ nhân có toàn quyền điều khiển thiết bị."),
            ("System Call", "Cơ chế để chương trình người dùng yêu cầu hệ điều hành thực hiện các tác vụ đặc quyền (đọc đĩa, gửi gói tin)."),
            ("Fork System Call", "Lệnh fork() tạo ra một tiến trình con mới là bản sao giống hệt tiến trình cha đang chạy."),
            ("Context Switching Trap", "Lệnh ngắt mềm (software interrupt / trap) kích hoạt việc chuyển đổi an toàn từ User Mode sang Kernel Mode."),
        ],
        "quiz": [
            ("Cơ chế nào cho phép một ứng dụng thông thường yêu cầu hệ điều hành đọc một tệp tin từ đĩa?", "System Call (Lời gọi hệ thống)", "Vòng lặp vô tận", "Biến toàn cục", "Ép xung CPU", "A"),
            ("Trong hệ điều hành Unix, lời gọi hệ thống nào được dùng để tạo ra một tiến trình con mới?", "exec()", "fork()", "exit()", "kill()", "B"),
            ("Tại sao hệ điều hành hiện đại lại phân chia thành User Mode và Kernel Mode?", "Để tăng dung lượng ổ cứng", "Để bảo vệ hệ thống tránh phần mềm người dùng can thiệp làm sập phần cứng", "Để chạy chậm lại", "Để tiết kiệm pin", "B"),
            ("Lệnh ngắt phần mềm đưa CPU từ User Mode vào Kernel Mode thường được gọi là gì?", "Trap", "Fault", "Abort", "Signal", "A"),
        ],
    },
    {
        "title": "Hợp ngữ: Lập trình Assembly x86 cơ bản",
        "description": "Các thanh ghi cơ bản (EAX, EBX, ESP, EBP), lệnh MOV, PUSH, POP, ADD, JMP.",
        "cards": [
            ("General Purpose Registers", "Các thanh ghi đa năng 32-bit: EAX (tích lũy/giá trị trả về), EBX (cơ sở), ECX (đếm vòng lặp), EDX (dữ liệu)."),
            ("Stack Pointer (ESP)", "Thanh ghi con trỏ trỏ tới đỉnh hiện tại của ngăn xếp thời gian chạy trong bộ nhớ."),
            ("MOV Instruction", "Lệnh MOV destination, source sao chép dữ liệu từ nguồn sang đích."),
            ("JMP and Conditional Jumps", "Lệnh nhảy không điều kiện JMP và nhảy có điều kiện (JE, JNE, JG, JL) dựa trên thanh ghi cờ EFLAGS."),
        ],
        "quiz": [
            ("Trong quy ước gọi hàm chuẩn x86, giá trị trả về của một hàm thường được lưu trữ trong thanh ghi nào?", "EAX", "ESP", "EBP", "EDX", "A"),
            ("Thanh ghi nào luôn trỏ tới đỉnh hiện tại của Call Stack trong kiến trúc x86?", "EAX", "ESP (Stack Pointer)", "EBX", "ECX", "B"),
            ("Lệnh hợp ngữ 'MOV EAX, 5' thực hiện công việc gì?", "So sánh EAX với 5", "Gán giá trị 5 vào thanh ghi EAX", "Cộng 5 vào EAX", "Xóa thanh ghi EAX", "B"),
            ("Lệnh nhảy 'JE label' (Jump if Equal) sẽ nhảy đến nhãn label khi nào?", "Khi cờ Zero Flag (ZF) = 1 (kết quả so sánh bằng nhau)", "Khi cờ Carry Flag = 1", "Luôn luôn nhảy", "Khi thanh ghi EAX bằng 0", "A"),
        ],
    },
    {
        "title": "Kiến trúc máy tính: Cơ chế Ngắt (Interrupts) & I/O",
        "description": "Ngắt phần cứng (Hardware Interrupts), bộ điều khiển PIC, DMA (Direct Memory Access).",
        "cards": [
            ("Hardware Interrupt", "Tín hiệu điện tử từ thiết bị ngoại vi (bàn phím, chuột, card mạng) báo cho CPU tạm dừng xử lý sự kiện khẩn."),
            ("Interrupt Service Routine", "Chương trình con phục vụ ngắt (ISR) được CPU kích hoạt để xử lý tín hiệu ngắt tương ứng."),
            ("Direct Memory Access (DMA)", "Cơ chế cho phép thiết bị ngoại vi đọc ghi trực tiếp với RAM mà không cần qua CPU, giải phóng tải CPU."),
            ("Polling vs Interrupt", "Polling: CPU liên tục kiểm tra trạng thái thiết bị (tốn chu kỳ); Interrupt: thiết bị chủ động báo khi sẵn sàng."),
        ],
        "quiz": [
            ("Khi bạn gõ một phím trên bàn phím, tín hiệu nào được gửi tới CPU để thông báo có ký tự mới?", "System Call", "Hardware Interrupt (Ngắt phần cứng)", "DMA Request", "Polling signal", "B"),
            ("Cơ chế cho phép card mạng hoặc ổ cứng truyền dữ liệu trực tiếp vào RAM mà không cần CPU trung chuyển gọi là gì?", "DMA (Direct Memory Access)", "Interrupt Handler", "Bus Snooping", "Virtual Memory", "A"),
            ("Đoạn mã được CPU thực thi ngay lập tức để xử lý một tín hiệu ngắt cụ thể gọi là gì?", "ISR (Interrupt Service Routine)", "Bootloader", "Kernel Thread", "BIOS", "A"),
            ("So với phương pháp Thăm dò (Polling), cơ chế Ngắt (Interrupt) có ưu điểm vượt trội nào?", "Không lãng phí chu kỳ CPU khi thiết bị đang ở trạng thái nhàn rỗi", "Dễ viết code hơn", "Không cần phần cứng", "Tăng dung lượng lưu trữ", "A"),
        ],
    },

    # --- 81-90: Mạng máy tính & An toàn thông tin ---
    {
        "title": "Mạng máy tính: Mô hình OSI & TCP/IP",
        "description": "7 tầng mô hình OSI, so sánh giao thức TCP (tin cậy, bắt tay 3 bước) và UDP (tốc độ cao).",
        "cards": [
            ("7 Layers of OSI", "Vật lý (1) -> Liên kết dữ liệu (2) -> Mạng (3) -> Giao vận (4) -> Phiên (5) -> Trình diễn (6) -> Ứng dụng (7)."),
            ("TCP 3-Way Handshake", "Bắt tay 3 bước thiết lập kết nối tin cậy: SYN -> SYN-ACK -> ACK."),
            ("TCP vs UDP", "TCP: hướng kết nối, đảm bảo toàn vẹn dữ liệu, truyền đúng thứ tự; UDP: phi kết nối, tốc độ cao, chấp nhận mất gói."),
            ("IP Protocol", "Giao thức tầng Mạng (Layer 3) chịu trách nhiệm định tuyến và đánh địa chỉ logic cho các gói tin."),
        ],
        "quiz": [
            ("Mô hình tham chiếu OSI chuẩn bao gồm tổng cộng bao nhiêu tầng?", "4 tầng", "5 tầng", "7 tầng", "9 tầng", "C"),
            ("Giao thức nào hoạt động tại tầng Giao vận (Transport) cung cấp kết nối tin cậy và đảm bảo đúng thứ tự gói tin?", "UDP", "TCP", "IP", "ICMP", "B"),
            ("Quy trình thiết lập kết nối của giao thức TCP được gọi là gì?", "2-Way Handshake", "3-Way Handshake (SYN, SYN-ACK, ACK)", "SSL Handshake", "Ping Request", "B"),
            ("Ứng dụng nào sau đây ưu tiên sử dụng giao thức UDP thay vì TCP vì cần độ trễ cực thấp?", "Tải file văn bản FTP", "Gửi email SMTP", "Livestream video và Game online thời gian thực", "Truy cập web thương mại", "C"),
        ],
    },
    {
        "title": "Mạng máy tính: Giao thức HTTP, HTTPS & WebSockets",
        "description": "Giao thức truyền siêu văn bản, mã hóa SSL/TLS, kết nối song công toàn phần (Full-duplex).",
        "cards": [
            ("HTTP Request Structure", "Cấu trúc gồm Request Line (Method, URI, Version), Headers (Metadata) và Body (Payload)."),
            ("HTTPS Encryption", "HTTPS = HTTP + TLS/SSL, mã hóa toàn bộ dữ liệu đường truyền ngăn chặn nghe lén và giả mạo."),
            ("WebSocket Protocol", "Giao thức kết nối 2 chiều liên tục (Full-duplex) qua một kết nối TCP duy nhất, độ trễ cực thấp."),
            ("HTTP/2 Multiplexing", "HTTP/2 truyền đồng thời nhiều luồng request/response trên cùng một kết nối TCP (Multiplexing)."),
        ],
        "quiz": [
            ("Cổng kết nối (Port) mặc định của giao thức HTTPS là bao nhiêu?", "80", "8080", "443", "22", "C"),
            ("Giao thức nào cho phép máy chủ chủ động đẩy dữ liệu thời gian thực về trình duyệt mà không cần client gửi request liên tục?", "HTTP/1.1", "WebSockets", "FTP", "DNS", "B"),
            ("Tính năng nổi bật nào của HTTP/2 giúp giải quyết hiện tượng nghẽn đầu hàng (Head-of-Line Blocking) ở tầng ứng dụng?", "Multiplexing (Đa hợp luồng)", "Plain text header", "Bỏ qua cookie", "Không cần mã hóa", "A"),
            ("Header nào trong HTTP Request cho máy chủ biết kiểu dữ liệu của nội dung body được gửi lên?", "Authorization", "Content-Type", "User-Agent", "Accept-Language", "B"),
        ],
    },
    {
        "title": "Mạng máy tính: Phân giải Tên miền DNS & DHCP",
        "description": "Hệ thống tên miền DNS, cấu trúc phân cấp (Root, TLD, Authoritative) và cấp phát IP động với DHCP.",
        "cards": [
            ("DNS Hierarchy", "Cây phân cấp tên miền: Root (.) -> TLD (.com, .vn) -> Second-level domain -> Subdomain."),
            ("DNS Records", "Bản ghi A (tên miền sang IPv4), AAAA (sang IPv6), CNAME (tên miền bí danh), MX (máy chủ thư điện tử)."),
            ("DHCP DORA Process", "Quy trình cấp IP động 4 bước: Discover (Tìm) -> Offer (Đề xuất) -> Request (Yêu cầu) -> Acknowledge (Xác nhận)."),
            ("DNS Caching", "Lưu tạm kết quả phân giải IP tại máy tính cục bộ hoặc router trong khoảng thời gian TTL để giảm tải truy vấn."),
        ],
        "quiz": [
            ("Bản ghi DNS nào dùng để ánh xạ một tên miền sang một địa chỉ IPv4 cụ thể?", "Bản ghi A", "Bản ghi CNAME", "Bản ghi MX", "Bản ghi TXT", "A"),
            ("Quy trình 4 bước của giao thức cấp phát địa chỉ IP động DHCP viết tắt là gì?", "ACID", "DORA (Discover, Offer, Request, Acknowledge)", "CRUD", "REST", "B"),
            ("Thông số TTL (Time-To-Live) trong bản ghi DNS có ý nghĩa gì?", "Thời gian tồn tại của tên miền", "Thời gian bản ghi được phép lưu cache trước khi cần truy vấn lại", "Số lượng IP tối đa", "Tốc độ đường truyền", "B"),
            ("Cổng mặc định mà máy chủ DNS lắng nghe các truy vấn UDP là cổng nào?", "21", "53", "80", "110", "B"),
        ],
    },
    {
        "title": "Mạng máy tính: Địa chỉ IPv4, IPv6 & Chia Subnet",
        "description": "Cấu trúc địa chỉ IP 32-bit vs 128-bit, Subnet Mask, ký hiệu CIDR và kỹ thuật chia mạng con.",
        "cards": [
            ("IPv4 Structure", "Gồm 32 bit nhị phân chia thành 4 octet (ví dụ 192.168.1.1), tối đa khoảng 4.3 tỷ địa chỉ."),
            ("IPv6 Superiority", "Gồm 128 bit biểu diễn dưới dạng hexa, giải quyết triệt để tình trạng cạn kiệt địa chỉ IPv4."),
            ("CIDR Notation", "Ký hiệu tiền tố mạng /prefix (ví dụ /24 biểu thị 24 bit đầu là NetID và 8 bit sau là HostID)."),
            ("Private IP Ranges", "Dải IP dùng cho mạng nội bộ: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (không định tuyến trên Internet)."),
        ],
        "quiz": [
            ("Địa chỉ IPv4 có độ dài bao nhiêu bit?", "16 bit", "32 bit", "64 bit", "128 bit", "B"),
            ("Một mạng con có ký hiệu CIDR /24 có thể gán tối đa cho bao nhiêu thiết bị máy trạm (khả dụng)?", "256 thiết bị", "254 thiết bị (trừ địa chỉ mạng và broadcast)", "128 thiết bị", "65534 thiết bị", "B"),
            ("Dải địa chỉ IP nào sau đây thuộc về IP riêng nội bộ (Private IP)?", "8.8.8.8", "192.168.1.1", "1.1.1.1", "172.217.0.1", "B"),
            ("Địa chỉ Loopback chuẩn dùng để tự kết nối lại chính máy tính của mình trong IPv4 là gì?", "192.168.0.1", "127.0.0.1 (localhost)", "255.255.255.255", "0.0.0.0", "B"),
        ],
    },
    {
        "title": "An toàn thông tin: Mật mã học Cơ bản",
        "description": "Mã hóa đối xứng (AES), bất đối xứng (RSA), hàm băm một chiều (SHA-256) và chữ ký số.",
        "cards": [
            ("Symmetric Encryption", "Mã hóa đối xứng: dùng chung một khóa bí mật duy nhất để cả mã hóa và giải mã (AES, DES)."),
            ("Asymmetric Encryption", "Mã hóa bất đối xứng: dùng cặp khóa Public Key (công khai để mã hóa) và Private Key (bí mật để giải mã) (RSA, ECC)."),
            ("Cryptographic Hash Function", "Hàm băm một chiều (SHA-256): chuyển dữ liệu thành chuỗi băm cố định, không thể đảo ngược, chống va chạm."),
            ("Digital Signature", "Chữ ký số: người gửi mã hóa giá trị băm bằng Private Key để người nhận xác thực nguồn gốc và tính toàn vẹn."),
        ],
        "quiz": [
            ("Thuật toán nào sau đây là thuật toán mã hóa ĐỐI XỨNG phổ biến nhất thế giới?", "RSA", "AES (Advanced Encryption Standard)", "ECC", "Diffie-Hellman", "B"),
            ("Trong mã hóa bất đối xứng, bạn nên gửi khóa nào cho đối tác để họ mã hóa dữ liệu gửi cho bạn?", "Private Key (Khóa bí mật)", "Public Key (Khóa công khai)", "Cả hai khóa", "Không gửi khóa nào", "B"),
            ("Đặc tính cốt lõi của hàm băm mật mã học (như SHA-256) là gì?", "Có thể giải mã ngược lại bản gốc dễ dàng", "Là hàm một chiều, không thể suy ngược ra bản gốc", "Luôn tạo chuỗi có độ dài thay đổi", "Chỉ băm được số", "B"),
            ("Chữ ký số (Digital Signature) đảm bảo được hai yếu tố bảo mật quan trọng nào?", "Nén dung lượng và tăng tốc độ", "Tính xác thực nguồn gốc và tính toàn vẹn dữ liệu", "Bảo vệ màn hình", "Ẩn địa chỉ IP", "B"),
        ],
    },
    {
        "title": "An toàn thông tin: Top 10 Lỗ hổng OWASP",
        "description": "Các cuộc tấn công Web nguy hiểm: SQL Injection, XSS, CSRF, Broken Authentication.",
        "cards": [
            ("SQL Injection", "Kẻ tấn công chèn mã lệnh SQL độc hại vào ô input để thao túng cơ sở dữ liệu (phòng chống bằng Parameterized Queries)."),
            ("Cross-Site Scripting (XSS)", "Chèn mã JavaScript độc hại vào trang web khiến người dùng khác bị đánh cắp Cookie hoặc thông tin cá nhân."),
            ("Cross-Site Request Forgery (CSRF)", "Lừa trình duyệt của nạn nhân thực thi các hành động không mong muốn trên trang web mà họ đã đăng nhập."),
            ("Broken Authentication", "Lỗ hổng liên quan đến xác thực và quản lý phiên làm việc yếu kém khiến tài khoản bị chiếm đoạt."),
        ],
        "quiz": [
            ("Biện pháp hiệu quả nhất để phòng chống triệt để lỗ hổng SQL Injection là gì?", "Sử dụng Parameterized Queries (Prepared Statements)", "Chỉ dùng chữ hoa trong input", "Khóa máy chủ", "Tắt mạng", "A"),
            ("Lỗ hổng Cross-Site Scripting (XSS) cho phép kẻ tấn công làm điều gì?", "Chèn và thực thi mã JavaScript độc hại trên trình duyệt của nạn nhân", "Xóa toàn bộ ổ cứng máy chủ", "Đổi mật khẩu BIOS", "Cắt đứt cáp quang", "A"),
            ("Để chống tấn công CSRF, các framework web hiện đại thường thêm yếu tố bảo vệ nào vào Form?", "CSRF Token bí mật cho mỗi phiên", "Đổi tên form", "Xóa hết nút submit", "Bắt nhập lại mật khẩu 10 lần", "A"),
            ("OWASP là từ viết tắt của tổ chức bảo mật web phi lợi nhuận nào?", "Open Web Application Security Project", "Online Web Attack Security Protocol", "Official World Anti-Spam Project", "Optimum Windows Application System Protection", "A"),
        ],
    },
    {
        "title": "An ninh mạng: Tường lửa & Reverse Proxy",
        "description": "Tường lửa Packet Filtering, Web Application Firewall (WAF), Cân bằng tải (Load Balancing) với NGINX.",
        "cards": [
            ("Firewall Filtering", "Tường lửa kiểm soát lưu lượng mạng ra vào dựa trên bộ quy tắc (địa chỉ IP, cổng Port, giao thức)."),
            ("Web Application Firewall", "WAF kiểm tra lưu lượng ở tầng ứng dụng (Layer 7) để phát hiện và ngăn chặn các cuộc tấn công HTTP/HTTPS."),
            ("Reverse Proxy", "Máy chủ trung gian đứng trước cụm backend để định tuyến request, ẩn IP thật và cân bằng tải (NGINX, HAProxy)."),
            ("Load Balancing Algorithms", "Các thuật toán cân bằng tải: Round Robin (luân phiên), Least Connections (ưu tiên ít kết nối), IP Hash."),
        ],
        "quiz": [
            ("Phần mềm NGINX thường được cấu hình đóng vai trò gì trước các máy chủ ứng dụng?", "Hệ điều hành", "Reverse Proxy và Load Balancer", "Trình duyệt web", "Trình biên dịch C", "B"),
            ("Tường lửa ứng dụng web (WAF) hoạt động chủ yếu ở tầng nào trong mô hình OSI?", "Tầng Vật lý (Layer 1)", "Tầng Mạng (Layer 3)", "Tầng Ứng dụng (Layer 7)", "Tầng Giao vận (Layer 4)", "C"),
            ("Thuật toán cân bằng tải nào phân phối các request lần lượt tuần tự theo vòng tròn đến các máy chủ?", "Round Robin", "Random Drop", "Shortest Job First", "First In First Out", "A"),
            ("Lợi ích của việc đặt Reverse Proxy trước hệ thống backend là gì?", "Giấu IP máy chủ thật, cân bằng tải và hỗ trợ nén SSL Termination", "Tự động viết code backend", "Tăng dung lượng pin", "Miễn phí tiền điện", "A"),
        ],
    },
    {
        "title": "An toàn thông tin: Bắt tay bảo mật SSL/TLS",
        "description": "Chứng chỉ số X.509, Certificate Authority (CA), chuỗi xác thực và quy trình TLS Handshake.",
        "cards": [
            ("TLS Handshake", "Quá trình máy khách và máy chủ chào nhau, xác minh danh tính và thỏa thuận khóa phiên bí mật."),
            ("Certificate Authority (CA)", "Tổ chức trung gian uy tín cấp chứng chỉ số (Let's Encrypt, DigiCert) chứng minh tính xác thực của website."),
            ("Session Key", "Khóa đối xứng tạm thời được sinh ra trong quá trình bắt tay dùng để mã hóa toàn bộ phiên làm việc tốc độ cao."),
            ("Man-in-the-Middle Attack", "Tấn công đứng giữa: kẻ gian can thiệp vào đường truyền mạng để giả mạo nội dung (bị TLS ngăn chặn)."),
        ],
        "quiz": [
            ("Tổ chức uy tín chịu trách nhiệm ký và phát hành chứng chỉ số SSL/TLS cho các website gọi là gì?", "DNS", "CA (Certificate Authority)", "DHCP", "ISP", "B"),
            ("Sau khi hoàn tất quá trình bắt tay TLS Handshake, dữ liệu thực tế giữa trình duyệt và máy chủ được mã hóa bằng gì?", "Khóa đối xứng (Symmetric Session Key) tốc độ cao", "Mã Morse", "Khóa công khai của Google", "Không mã hóa nữa", "A"),
            ("Nếu chứng chỉ SSL của một website bị hết hạn hoặc không do CA uy tín cấp, trình duyệt sẽ hiển thị gì?", "Cảnh báo bảo mật màu đỏ (Security Warning)", "Tự động tắt máy tính", "Không hiển thị gì", "Chạy nhanh hơn", "A"),
            ("Giao thức TLS là phiên bản hiện đại và an toàn hơn thay thế cho giao thức tiền thân nào?", "SSL (Secure Sockets Layer)", "FTP", "Telnet", "HTTP", "A"),
        ],
    },
    {
        "title": "An ninh mạng: Mạng riêng ảo VPN & Đường hầm SSH",
        "description": "Giao thức IPsec, OpenVPN, WireGuard, giao thức SSH bảo mật và đường hầm mã hóa.",
        "cards": [
            ("Virtual Private Network", "VPN thiết lập một đường hầm mã hóa an toàn qua Internet công cộng, bảo vệ lưu lượng dữ liệu và ẩn IP."),
            ("VPN Tunneling", "Kỹ thuật đóng gói toàn bộ gói tin bên trong một gói tin mã hóa khác trước khi truyền qua mạng công cộng."),
            ("Secure Shell (SSH)", "Giao thức điều khiển máy chủ từ xa an toàn qua dòng lệnh (CLI), thay thế giao thức không mã hóa Telnet."),
            ("SSH Key-based Auth", "Xác thực SSH bằng cặp khóa công khai/bí mật an toàn hơn rất nhiều so với dùng mật khẩu thông thường."),
        ],
        "quiz": [
            ("Cổng kết nối mặc định của giao thức điều khiển từ xa SSH là gì?", "Port 21", "Port 22", "Port 80", "Port 443", "B"),
            ("Cơ chế chính mà mạng riêng ảo (VPN) sử dụng để bảo vệ dữ liệu trên mạng công cộng là gì?", "Tạo đường hầm mã hóa (Tunneling & Encryption)", "Tăng tốc độ mạng lên 10Gbps", "Chặn mọi trang web", "Tự động đổi mật khẩu máy tính", "A"),
            ("Giao thức VPN hiện đại nào có mã nguồn gọn nhẹ, hiệu năng cực cao và đang dần thay thế OpenVPN?", "WireGuard", "PPTP", "Telnet", "FTP", "A"),
            ("Tại sao giao thức Telnet cũ kỹ lại bị cấm sử dụng trong quản trị máy chủ hiện đại?", "Telnet truyền mật khẩu và dữ liệu dưới dạng văn bản thuần túy (Plaintext) không mã hóa", "Telnet chỉ chạy trên máy in", "Telnet tốn quá nhiều RAM", "Telnet không hỗ trợ bàn phím", "A"),
        ],
    },
    {
        "title": "Xác thực & Cấp quyền: OAuth2 & JSON Web Token",
        "description": "Cơ chế phân quyền OAuth 2.0, đăng nhập bên thứ ba, cấu trúc 3 phần của JWT Token.",
        "cards": [
            ("Authentication vs Authorization", "Authentication (Xác thực: bạn là ai?); Authorization (Cấp quyền: bạn được phép làm gì?)."),
            ("OAuth 2.0 Framework", "Khung ủy quyền cho phép ứng dụng truy cập tài nguyên của người dùng trên dịch vụ khác (Google, Facebook) mà không cần biết mật khẩu."),
            ("JWT Structure", "JSON Web Token gồm 3 phần nối bằng dấu chấm: Header (thuật toán) . Payload (dữ liệu claims) . Signature (chữ ký)."),
            ("Stateless Tokens", "Máy chủ không cần lưu trạng thái đăng nhập vào session CSDL vì chữ ký số trong JWT đã tự chứng minh tính hợp lệ."),
        ],
        "quiz": [
            ("Một chuỗi JSON Web Token (JWT) tiêu chuẩn bao gồm bao nhiêu phần được ngăn cách bằng dấu chấm?", "2 phần", "3 phần (Header, Payload, Signature)", "4 phần", "5 phần", "B"),
            ("Khung giao thức nào thường được các ứng dụng sử dụng để triển khai nút 'Đăng nhập bằng tài khoản Google'?", "FTP", "OAuth 2.0", "POP3", "SNMP", "B"),
            ("Phần nào trong JWT chứa thông tin người dùng (user_id, role, thời gian hết hạn exp)?", "Header", "Payload", "Signature", "Footer", "B"),
            ("Sự khác biệt cốt lõi giữa Authentication và Authorization là gì?", "Authentication xác định danh tính người dùng, Authorization xác định quyền hạn của người đó", "Cả hai là một", "Authentication là phân quyền", "Authorization không cần mật khẩu", "A"),
        ],
    },

    # --- 91-100: Toán học, Trí tuệ Nhân tạo & Khoa học Tổng hợp ---
    {
        "title": "Toán học: Toán rời rạc & Đại số Boole",
        "description": "Lý thuyết tập hợp, phép toán logic (AND, OR, XOR), bảng chân trị và quan hệ tương đương.",
        "cards": [
            ("Boolean Algebra", "Đại số logic hoạt động trên hai giá trị chân lý: Đúng (True/1) và Sai (False/0)."),
            ("XOR Operation", "Phép toán Tuyển loại trừ (XOR): chỉ trả về 1 khi hai đầu vào có giá trị khác nhau."),
            ("De Morgan's Laws", "Định luật De Morgan: NOT(A AND B) = (NOT A) OR (NOT B); NOT(A OR B) = (NOT A) AND (NOT B)."),
            ("Pigeonhole Principle", "Nguyên lý chuồng bồ câu: Nếu có N+1 con bồ câu nhốt vào N chuồng, chắc chắn có ít nhất 1 chuồng chứa từ 2 con trở lên."),
        ],
        "quiz": [
            ("Kết quả của phép toán logic '1 XOR 1' là bao nhiêu?", "1", "0", "2", "Không xác định", "B"),
            ("Theo định luật De Morgan, phủ định của mệnh đề '(A AND B)' tương đương với biểu thức nào?", "(NOT A) OR (NOT B)", "(NOT A) AND (NOT B)", "A OR B", "NOT (A OR B)", "A"),
            ("Nếu có 13 người trong một căn phòng, ta có thể khẳng định chắc chắn điều gì theo nguyên lý chuồng bồ câu?", "Tất cả sinh cùng năm", "Có ít nhất 2 người có cùng tháng sinh", "Không ai cùng tuổi", "Có 3 người sinh cùng ngày", "B"),
            ("Bảng chân trị (Truth Table) dùng để biểu diễn điều gì?", "Giá trị đầu ra của biểu thức logic với mọi tổ hợp giá trị đầu vào", "Giá cả cổ phiếu", "Tốc độ mạng", "Dung lượng bộ nhớ", "A"),
        ],
    },
    {
        "title": "Toán học: Đại số tuyến tính cho Machine Learning",
        "description": "Vector, Ma trận, Phép nhân ma trận, Ma trận chuyển vị và Định thức (Determinant).",
        "cards": [
            ("Vector and Matrix", "Vector là mảng một chiều biểu diễn tọa độ/đặc trưng; Ma trận là bảng hai chiều biểu diễn phép biến đổi tuyến tính."),
            ("Matrix Multiplication", "Phép nhân ma trận A(m x k) với B(k x n) tạo thành ma trận C(m x n); điều kiện là số cột của A phải bằng số dòng của B."),
            ("Transpose Matrix", "Ma trận chuyển vị A^T thu được bằng cách đổi các dòng của A thành các cột tương ứng."),
            ("Eigenvalues & Eigenvectors", "Trị riêng và Vector riêng: Ax = lambda * x, phản ánh các trục phương hướng bất biến trong không gian vector."),
        ],
        "quiz": [
            ("Điều kiện bắt buộc để có thể nhân ma trận A kích thước (m x k) với ma trận B kích thước (p x n) là gì?", "m phải bằng n", "k phải bằng p", "A và B phải là ma trận vuông", "m phải bằng p", "B"),
            ("Ma trận đơn vị (Identity Matrix) có tính chất đặc biệt nào?", "Toàn bộ phần tử đều bằng 0", "Các phần tử trên đường chéo chính bằng 1, các phần tử khác bằng 0", "Định thức bằng 0", "Không có ma trận nghịch đảo", "B"),
            ("Phép biến đổi đổi các dòng của ma trận thành các cột gọi là phép toán gì?", "Chuyển vị (Transpose)", "Nghịch đảo (Inverse)", "Khử Gauss", "Định thức", "A"),
            ("Đại số tuyến tính đóng vai trò nền tảng trong lĩnh vực công nghệ nào sau đây?", "Mạng nơ-ron và Xử lý dữ liệu đa chiều trong AI", "Hệ thống làm mát quạt gió", "Dây cáp mạng", "In ấn tài liệu", "A"),
        ],
    },
    {
        "title": "Toán học: Xác suất Thống kê cho Data Science",
        "description": "Biến ngẫu nhiên, Kỳ vọng (Mean), Phương sai (Variance), Định lý Bayes và Phân phối chuẩn.",
        "cards": [
            ("Normal Distribution", "Phân phối chuẩn hình chuông đối xứng đặc trưng bởi kỳ vọng mu và độ lệch chuẩn sigma (quy tắc 68-95-99.7)."),
            ("Bayes' Theorem", "Định lý Bayes: P(A|B) = [P(B|A) * P(A)] / P(B), cập nhật xác suất của giả thuyết khi có bằng chứng mới."),
            ("Variance & Standard Deviation", "Phương sai và Độ lệch chuẩn đo lường mức độ phân tán hoặc biến thiên của dữ liệu quanh giá trị trung bình."),
            ("Correlation vs Causation", "Tương quan không đồng nghĩa với Nhân quả: hai biến số biến thiên cùng nhau không có nghĩa biến này sinh ra biến kia."),
        ],
        "quiz": [
            ("Quy tắc nào trong thống kê dùng để cập nhật xác suất của một sự kiện khi có thêm thông tin mới?", "Định lý Pytago", "Định lý Bayes", "Quy tắc L'Hopital", "Định luật Newton", "B"),
            ("Đại lượng nào dùng để đo lường độ phân tán của các điểm dữ liệu so với giá trị trung bình?", "Kỳ vọng (Mean)", "Trung vị (Median)", "Độ lệch chuẩn (Standard Deviation)", "Mốt (Mode)", "C"),
            ("Trong phân phối chuẩn chuẩn hóa, giá trị trung bình (Mean) và phương sai (Variance) bằng bao nhiêu?", "Mean = 0, Variance = 1", "Mean = 1, Variance = 0", "Mean = 100, Variance = 15", "Mean = 0, Variance = 0", "A"),
            ("Câu châm ngôn kinh điển trong phân tích dữ liệu là gì?", "Correlation implies Causation", "Correlation does not imply Causation (Tương quan không chứng minh nhân quả)", "Data never lies", "Mean is always best", "B"),
        ],
    },
    {
        "title": "Trí tuệ nhân tạo: Học máy căn bản (Machine Learning)",
        "description": "Học có giám sát (Supervised), Học không giám sát (Unsupervised) và Overfitting/Underfitting.",
        "cards": [
            ("Supervised Learning", "Học có giám sát: mô hình học từ tập dữ liệu có sẵn nhãn (Hồi quy Linear Regression, Phân lớp SVM)."),
            ("Unsupervised Learning", "Học không giám sát: mô hình tự tìm cấu trúc ẩn trong dữ liệu không có nhãn (Phân cụm K-Means, Giảm chiều PCA)."),
            ("Overfitting", "Hiện tượng học vẹt: mô hình ghi nhớ quá mức chi tiết tập train, dẫn đến dự đoán rất kém trên tập dữ liệu mới."),
            ("Train-Validation-Test Split", "Chia dữ liệu thành 3 tập để huấn luyện, tinh chỉnh siêu tham số và đánh giá khách quan độ chính xác."),
        ],
        "quiz": [
            ("Thuật toán phân cụm K-Means thuộc vào nhóm học máy nào?", "Học có giám sát (Supervised)", "Học không giám sát (Unsupervised)", "Học tăng cường (Reinforcement)", "Học bán giám sát", "B"),
            ("Hiện tượng mô hình đạt độ chính xác 100% trên tập huấn luyện nhưng dự đoán rất tệ trên dữ liệu thực tế gọi là gì?", "Underfitting", "Overfitting (Hiện tượng quá khớp)", "Convergence", "Regularization", "B"),
            ("Thuật toán Hồi quy tuyến tính (Linear Regression) dùng để dự đoán kiểu dữ liệu nào?", "Dữ liệu nhãn phân loại (Có/Không)", "Giá trị số liên tục (như giá nhà, nhiệt độ)", "Ảnh chụp", "Tập hợp file", "B"),
            ("Kỹ thuật Cross-Validation (K-Fold) thường được áp dụng nhằm mục đích gì?", "Tăng kích thước ổ cứng", "Đánh giá mô hình khách quan và giảm thiểu rủi ro overfitting", "Viết code ngắn hơn", "Tự động gắn nhãn", "B"),
        ],
    },
    {
        "title": "Trí tuệ nhân tạo: Mạng Nơ-ron & Deep Learning",
        "description": "Perceptron, Hàm kích hoạt (ReLU, Sigmoid), Lan truyền ngược (Backpropagation) và Gradient Descent.",
        "cards": [
            ("Artificial Neuron", "Nơ-ron nhân tạo: tính tổng có trọng số sum(w*x + b) rồi đưa qua hàm kích hoạt phi tuyến."),
            ("Activation Function", "Hàm kích hoạt (ReLU, Sigmoid, Softmax) mang lại tính phi tuyến tính, giúp mạng học được các hàm phức tạp."),
            ("Backpropagation", "Thuật toán lan truyền ngược: tính đạo hàm riêng của hàm mất mát để cập nhật trọng số bằng Gradient Descent."),
            ("Learning Rate", "Tốc độ học: siêu tham số quy định độ lớn của bước nhảy điều chỉnh trọng số ở mỗi vòng lặp tối ưu."),
        ],
        "quiz": [
            ("Hàm kích hoạt (Activation Function) phổ biến nhất trong các tầng ẩn của mạng Deep Learning hiện đại là gì?", "Sigmoid", "ReLU (Rectified Linear Unit)", "Step Function", "Linear", "B"),
            ("Thuật toán cốt lõi dùng để tính gradient và truyền ngược lỗi qua các tầng mạng để cập nhật trọng số là gì?", "Dijkstra", "Backpropagation (Lan truyền ngược)", "Binary Search", "Breadth-First Search", "B"),
            ("Nếu siêu tham số Tốc độ học (Learning Rate) được đặt quá lớn, điều gì sẽ xảy ra?", "Mô hình hội tụ cực nhanh", "Quá trình huấn luyện bị mất ổn định và hàm mất mát có thể phân kỳ", "Mạng ngừng hoạt động", "Mất kết nối mạng", "B"),
            ("Hàm kích hoạt nào thường được sử dụng ở tầng đầu ra cuối cùng của bài toán phân loại đa lớp (Multi-class)?", "ReLU", "Softmax", "Tanh", "Step", "B"),
        ],
    },
    {
        "title": "Trí tuệ nhân tạo: Xử lý Ngôn ngữ Tự nhiên (NLP)",
        "description": "Tokenization, Word Embeddings (Word2Vec), Cơ chế Attention và Kiến trúc Transformer.",
        "cards": [
            ("Tokenization", "Quá trình phân tách đoạn văn bản dài thành các đơn vị từ hoặc cụm từ nhỏ hơn gọi là Token."),
            ("Word Embeddings", "Biểu diễn ngữ nghĩa của từ dưới dạng vector số nhiều chiều (các từ có nghĩa gần nhau sẽ có vector gần nhau)."),
            ("Self-Attention Mechanism", "Cơ chế tự chú ý: cho phép mô hình đánh giá mức độ liên quan giữa mọi từ trong câu mà không phụ thuộc khoảng cách."),
            ("Transformer Architecture", "Kiến trúc nền tảng của các mô hình ngôn ngữ lớn (LLM như GPT, BERT) loại bỏ mạng hồi quy RNN."),
        ],
        "quiz": [
            ("Kiến trúc mạng nơ-ron mang tính cách mạng là nền tảng của các mô hình ngôn ngữ lớn (như GPT, Gemini) là gì?", "RNN", "Transformer", "LSTM", "Perceptron", "B"),
            ("Kỹ thuật mã hóa ngữ nghĩa của từ vựng thành vector trong không gian toán học nhiều chiều gọi là gì?", "Word Embeddings", "Parsing", "Compiling", "Hashing", "A"),
            ("Thao tác cắt một câu văn thành danh sách các từ hoặc cụm từ nhỏ hơn gọi là gì?", "Stemming", "Tokenization", "Lemmatization", "Translation", "B"),
            ("Cơ chế cốt lõi trong Transformer cho phép các từ trong câu 'nhìn' và hiểu ngữ cảnh của nhau gọi là gì?", "Attention / Self-Attention", "Pooling", "Dropout", "Convolution", "A"),
        ],
    },
    {
        "title": "Trí tuệ nhân tạo: Thị giác máy tính (Computer Vision)",
        "description": "Biểu diễn ảnh số, Mạng nơ-ron tích chập (CNN), Convolutional Kernel và Pooling Layer.",
        "cards": [
            ("Digital Image Representation", "Ảnh kỹ thuật số được biểu diễn dưới dạng ma trận điểm ảnh (Pixel) với các kênh màu RGB (Red, Green, Blue)."),
            ("Convolutional Layer", "Tầng tích chập: dùng các bộ lọc (Filter/Kernel) trượt trên ảnh để trích xuất các đặc trưng biên cạnh, hoa văn."),
            ("Pooling Layer", "Tầng giảm mẫu (Max-Pooling): giảm kích thước không gian của ma trận đặc trưng, tăng tốc độ tính toán."),
            ("Object Detection", "Bài toán phát hiện đối tượng: xác định vị trí hộp bao (Bounding Box) và phân loại nhãn của các vật thể trong ảnh."),
        ],
        "quiz": [
            ("Kiến trúc mạng nơ-ron chuyên dụng và thành công nhất trong các tác vụ xử lý hình ảnh là gì?", "RNN", "CNN (Convolutional Neural Network)", "GAN", "Decision Tree", "B"),
            ("Tầng Max-Pooling trong mạng CNN có tác dụng chính là gì?", "Tăng gấp đôi kích thước ảnh", "Giảm chiều không gian của bản đồ đặc trưng và giảm tải tính toán", "Đổi ảnh màu thành ảnh đen trắng", "Xóa nhiễu âm thanh", "B"),
            ("Bộ lọc (Kernel/Filter) trong tầng tích chập trượt qua ảnh nhằm mục đích gì?", "Trích xuất các đặc trưng hình học như góc cạnh, đường viền", "Nén dung lượng file JPEG", "In ảnh ra giấy", "Đổi tên file ảnh", "A"),
            ("Một bức ảnh màu chuẩn RGB thông thường được biểu diễn bằng tensor có bao nhiêu kênh màu?", "1 kênh", "2 kênh", "3 kênh (Red, Green, Blue)", "4 kênh", "C"),
        ],
    },
    {
        "title": "Lịch sử Điện toán: Các Cột mốc & Danh nhân",
        "description": "Alan Turing, Ada Lovelace, ENIAC, Transistor và sự ra đời của mạng Internet.",
        "cards": [
            ("Ada Lovelace", "Được công nhận là lập trình viên máy tính đầu tiên trong lịch sử với thuật toán tính số Bernoulli trên máy Babbage."),
            ("Alan Turing", "Cha đẻ của khoa học máy tính hiện đại và trí tuệ nhân tạo, tác giả cỗ máy giải mã Enigma và phép thử Turing Test."),
            ("Invention of Transistor", "Bóng bán dẫn ra đời năm 1947 tại Bell Labs thay thế đèn chân không cồng kềnh, mở ra cuộc cách mạng vi mạch."),
            ("ARPANET", "Mạng máy tính chuyển mạch gói do Bộ Quốc phòng Mỹ phát triển năm 1969, tiền thân trực tiếp của Internet ngày nay."),
        ],
        "quiz": [
            ("Ai được lịch sử tôn vinh là lập trình viên máy tính đầu tiên trên thế giới?", "Alan Turing", "Ada Lovelace", "Charles Babbage", "Bill Gates", "B"),
            ("Nhà khoa học nào được coi là cha đẻ của ngành Khoa học Máy tính và Trí tuệ Nhân tạo?", "Alan Turing", "Albert Einstein", "Isaac Newton", "Nikola Tesla", "A"),
            ("Linh kiện điện tử bán dẫn ra đời năm 1947 thay thế đèn điện tử chân không mở ra kỷ nguyên máy tính hiện đại là gì?", "Transistor (Bóng bán dẫn)", "Điện trở", "Tụ điện", "Cuộn cảm", "A"),
            ("Mạng máy tính nào ra đời năm 1969 được coi là tiền thân trực tiếp của mạng Internet toàn cầu?", "Ethernet", "ARPANET", "Intranet", "Usenet", "B"),
        ],
    },
    {
        "title": "Khoa học Tự nhiên: Vật lý Hiện đại",
        "description": "Thuyết tương đối hẹp của Einstein, Lưỡng tính sóng-hạt và Cơ học lượng tử.",
        "cards": [
            ("Speed of Light Constant", "Vận tốc ánh sáng trong chân không c = 299,792,458 m/s là tốc độ tối đa không vật thể nào có thể vượt qua."),
            ("Mass-Energy Equivalence", "Phương trình nổi tiếng E = mc^2 thể hiện sự tương đương giữa khối lượng và năng lượng của vật chất."),
            ("Wave-Particle Duality", "Lưỡng tính sóng - hạt: ánh sáng và các hạt vi mô vừa có tính chất của sóng, vừa có tính chất của hạt photon."),
            ("Uncertainty Principle", "Nguyên lý bất định Heisenberg: không thể đo đồng thời chính xác tuyệt đối cả vị trí và động lượng của một hạt."),
        ],
        "quiz": [
            ("Phương trình vật lý nổi tiếng nào của Albert Einstein khẳng định khối lượng có thể chuyển đổi thành năng lượng?", "F = ma", "E = mc^2", "v = s / t", "P = U * I", "B"),
            ("Vận tốc ánh sáng truyền trong môi trường chân không xấp xỉ bằng bao nhiêu?", "300 km/s", "300,000 km/s", "3,000,000 km/s", "30,000 km/s", "B"),
            ("Nguyên lý bất định trong cơ học lượng tử gắn liền với tên tuổi của nhà vật lý nào?", "Werner Heisenberg", "Niels Bohr", "Max Planck", "Marie Curie", "A"),
            ("Hiện tượng ánh sáng vừa có tính chất lan truyền như sóng, vừa có tính hạt được gọi là gì?", "Giao thoa ánh sáng", "Lưỡng tính sóng - hạt", "Khúc xạ ánh sáng", "Hiện tượng quang điện", "B"),
        ],
    },
    {
        "title": "Khoa học Vũ trụ: Hệ Mặt Trời & Các Thiên thể",
        "description": "8 hành tinh trong Hệ Mặt Trời, Hố đen vũ trụ (Black Hole) và Dải Ngân Hà (Milky Way).",
        "cards": [
            ("Solar System Planets", "8 hành tinh theo thứ tự từ Mặt Trời: Sao Thủy, Sao Kim, Trái Đất, Sao Hỏa, Sao Mộc, Sao Thổ, Sao Thiên Vương, Sao Hải Vương."),
            ("Jupiter Dominance", "Sao Mộc (Jupiter) là hành tinh lớn nhất trong Hệ Mặt Trời với khối lượng gấp 2.5 lần tất cả các hành tinh khác cộng lại."),
            ("Black Hole Event Horizon", "Chân trời sự kiện (Event Horizon) là ranh giới quanh hố đen mà ngay cả ánh sáng cũng không thể thoát ra ngoài."),
            ("Milky Way Galaxy", "Dải Ngân Hà là một thiên hà xoắn ốc chứa từ 100 đến 400 tỷ ngôi sao, trong đó có Hệ Mặt Trời của chúng ta."),
        ],
        "quiz": [
            ("Hành tinh nào có kích thước và khối lượng lớn nhất trong Hệ Mặt Trời của chúng ta?", "Sao Hỏa", "Sao Kim", "Sao Mộc (Jupiter)", "Sao Thổ", "C"),
            ("Ranh giới vô hình xung quanh hố đen mà vật chất hay ánh sáng khi lọt vào đều không thể thoát ra gọi là gì?", "Vành đai bức xạ", "Chân trời sự kiện (Event Horizon)", "Quỹ đạo dừng", "Tâm hố đen", "B"),
            ("Hệ Mặt Trời của chúng ta nằm trong thiên hà xoắn ốc nào?", "Thiên hà Tiên Nữ (Andromeda)", "Dải Ngân Hà (Milky Way)", "Thiên hà Tam Giác", "Đám mây Magellan", "B"),
            ("Hành tinh nào trong Hệ Mặt Trời được mệnh danh là 'Hành tinh Đỏ' do bề mặt chứa nhiều oxit sắt?", "Sao Thủy", "Sao Hỏa (Mars)", "Sao Hải Vương", "Sao Thổ", "B"),
        ],
    },
]


def generate_seed_data() -> None:
    """Tạo sinh dữ liệu 100 Deck, ~400 Cards, 100 Quizzes, ~400 Questions và lịch sử thi."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    base_time = datetime(2026, 10, 1, 8, 0, 0)

    # 1. Chuẩn bị danh sách Decks & Cards
    decks_rows = []
    cards_rows = []
    quizzes_rows = []
    questions_rows = []

    card_counter = 1
    question_counter = 1

    for idx, item in enumerate(RAW_DATA, start=1):
        deck_id = idx
        quiz_id = idx
        created_time = (base_time + timedelta(hours=idx * 3)).strftime("%Y-%m-%d %H:%M:%S")

        cards_list = item["cards"]
        total_cards = len(cards_list)

        # Decks row
        decks_rows.append({
            "deck_id": deck_id,
            "title": item["title"],
            "description": item["description"],
            "total_cards": total_cards,
            "is_studied": "1" if idx <= 10 else "0",
            "is_deleted": "0",
            "created_at": created_time,
            "updated_at": created_time,
        })

        # Cards rows
        for pos, (front, back) in enumerate(cards_list, start=1):
            cards_rows.append({
                "card_id": card_counter,
                "deck_id": deck_id,
                "front_text": front,
                "back_text": back,
                "position": pos,
            })
            card_counter += 1

        # Quizzes row
        time_limit = 15 if idx % 2 == 0 else 10
        quizzes_rows.append({
            "quiz_id": quiz_id,
            "source_deck_id": str(deck_id),
            "title": f"Quiz: {item['title']}",
            "description": f"Bài kiểm tra trắc nghiệm đánh giá kiến thức chủ đề '{item['title']}'.",
            "time_limit_minutes": str(time_limit),
            "is_deleted": "0",
            "created_at": created_time,
            "updated_at": created_time,
        })

        # Questions rows
        for pos, q in enumerate(item["quiz"], start=1):
            q_text, opt_a, opt_b, opt_c, opt_d, ans = q
            questions_rows.append({
                "question_id": question_counter,
                "quiz_id": quiz_id,
                "question_text": q_text,
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_answer": ans,
                "position": pos,
                "points": "1.00",
                "is_deleted": "0",
            })
            question_counter += 1

    # 2. Tạo lịch sử thi mẫu (Quiz Attempts & Answers) cho 10 bài thi đầu tiên
    attempts_rows = []
    answers_rows = []
    answer_counter = 1

    for attempt_idx in range(1, 11):
        q_id = attempt_idx
        q_item = RAW_DATA[attempt_idx - 1]
        started = (base_time + timedelta(days=attempt_idx, hours=10)).strftime("%Y-%m-%d %H:%M:%S")
        submitted = (base_time + timedelta(days=attempt_idx, hours=10, minutes=8)).strftime("%Y-%m-%d %H:%M:%S")
        total_q = len(q_item["quiz"])
        # Giả lập làm đúng 3 hoặc 4 câu
        correct_count = total_q if attempt_idx % 3 != 0 else (total_q - 1)
        score_percent = f"{(correct_count / total_q) * 100:.2f}"

        attempts_rows.append({
            "attempt_id": attempt_idx,
            "quiz_id": q_id,
            "quiz_title_snapshot": f"Quiz: {q_item['title']}",
            "attempt_status": "COMPLETED",
            "started_at": started,
            "submitted_at": submitted,
            "total_questions": total_q,
            "correct_count": correct_count,
            "score_percent": score_percent,
        })

        for pos, q in enumerate(q_item["quiz"], start=1):
            q_text, opt_a, opt_b, opt_c, opt_d, correct_ans = q
            opts = {"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d}
            # Giả định nếu câu cuối của quiz số 3, 6, 9 thì chọn sai
            if attempt_idx % 3 == 0 and pos == total_q:
                selected_ans = "D" if correct_ans != "D" else "C"
                is_correct = "0"
                pts = "0.00"
            else:
                selected_ans = correct_ans
                is_correct = "1"
                pts = "1.00"

            answers_rows.append({
                "answer_id": answer_counter,
                "attempt_id": attempt_idx,
                "selected_answer": selected_ans,
                "correct_answer_snapshot": correct_ans,
                "is_correct": is_correct,
                "points_earned": pts,
                "question_text_snapshot": q_text,
                "selected_option_text_snapshot": opts.get(selected_ans, ""),
                "correct_option_text_snapshot": opts.get(correct_ans, ""),
            })
            answer_counter += 1

    # 3. Ghi dữ liệu ra các file CSV với encoding utf-8-sig
    files_to_write = [
        (
            DATA_DIR / "decks.csv",
            ["deck_id", "title", "description", "total_cards", "is_studied", "is_deleted", "created_at", "updated_at"],
            decks_rows,
        ),
        (
            DATA_DIR / "cards.csv",
            ["card_id", "deck_id", "front_text", "back_text", "position"],
            cards_rows,
        ),
        (
            DATA_DIR / "quizzes.csv",
            ["quiz_id", "source_deck_id", "title", "description", "time_limit_minutes", "is_deleted", "created_at", "updated_at"],
            quizzes_rows,
        ),
        (
            DATA_DIR / "questions.csv",
            ["question_id", "quiz_id", "question_text", "option_a", "option_b", "option_c", "option_d", "correct_answer", "position", "points", "is_deleted"],
            questions_rows,
        ),
        (
            DATA_DIR / "quiz_attempts.csv",
            ["attempt_id", "quiz_id", "quiz_title_snapshot", "attempt_status", "started_at", "submitted_at", "total_questions", "correct_count", "score_percent"],
            attempts_rows,
        ),
        (
            DATA_DIR / "quiz_answers.csv",
            ["answer_id", "attempt_id", "selected_answer", "correct_answer_snapshot", "is_correct", "points_earned", "question_text_snapshot", "selected_option_text_snapshot", "correct_option_text_snapshot"],
            answers_rows,
        ),
    ]

    for filepath, fieldnames, rows in files_to_write:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Đã ghi thành công {len(rows)} bản ghi vào {filepath.name}")

    print("\n--- HOÀN TẤT KHỞI TẠO DỮ LIỆU ---")
    print(f"Tổng số Decks: {len(decks_rows)}")
    print(f"Tổng số Cards: {len(cards_rows)}")
    print(f"Tổng số Quizzes: {len(quizzes_rows)}")
    print(f"Tổng số Questions: {len(questions_rows)}")
    print(f"Tổng số Quiz Attempts: {len(attempts_rows)}")
    print(f"Tổng số Quiz Answers: {len(answers_rows)}")


if __name__ == "__main__":
    generate_seed_data()
