# Maritime Connectivity and Merchandise Export Performance in ASEAN, 2010–2025: Evidence from PPML and an Extended Gravity Model

**Đề tài:** Kết nối vận tải biển và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN giai đoạn 2010–2025: Bằng chứng từ PPML và mô hình trọng lực mở rộng.

---

## 1. Giới thiệu tổng quan

Kho lưu trữ mã nguồn và dữ liệu thực nghiệm phục vụ bài nghiên cứu định lượng mối quan hệ giữa năng lực kết nối vận tải biển (Liner Shipping Connectivity Index - LSCI, Bilateral Liner Shipping Connectivity Index - LSBCI) và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN ven biển giai đoạn 2010–2025.

Nghiên cứu áp dụng phương pháp hồi quy Poisson Pseudo-Maximum Likelihood (PPML) theo chuẩn Santos Silva & Tenreyro (2006) và mô hình Trọng lực cấu trúc mở rộng (Yotov et al., 2016), xử lý triệt để hiện tượng phương sai thay đổi và giá trị thương mại bằng 0 (Zero Trade). Toàn bộ quy trình suy diễn thống kê sử dụng sai số chuẩn phân cụm (Clustered SE) kết hợp hiệu chỉnh mẫu nhỏ Student-t (Cameron & Miller, 2015).

---

## 2. Kết quả kiểm định các giả thuyết cốt lõi

| Giả thuyết | Đặc tả thực nghiệm | Hệ số ước lượng | Ý nghĩa thống kê | Kết luận thực nghiệm chuẩn mực |
|---|---|---|---|---|
| **H1: LSCI tác động dương tới tổng xuất khẩu** | M1 & M2 PPML (Tầng A) | M1: \(\beta = 1.192^{**}\)<br>M2: \(\beta = 1.039^{***}\) | M1: \(p = 0.014\)<br>M2: \(p = 0.006\) | **Ủng hộ (Mối quan hệ đồng biến bền vững)**: Tăng 1% LSCI gắn liền với mức tăng 1.04% xuất khẩu khi kiểm soát GDP và dân số; do biến trễ và lead phản ánh quán tính vĩ mô cao nên được diễn giải là mối quan hệ đồng biến bền vững thay vì ngoại sinh nhân quả thuần túy. |
| **H2: LSBCI thúc đẩy xuất khẩu song phương** | G1 Cấu trúc ưu tiên (Cặp + XK-Năm + NK-Năm FE)<br>G2 Trọng lực chuẩn (Cặp FE + Năm FE) | G1: \(\beta = -0.195\)<br>G2: \(\beta = 0.770^{***}\) | G1: \(p = 0.422\)<br>G2: \(p = 0.004\) | **Không được ủng hộ trong mô hình cấu trúc ưu tiên**: Tác động dương chỉ xuất hiện trong mô hình G2 ít khắt khe; trong mô hình cấu trúc đầy đủ G1 (kiểm soát toàn diện sức cản đa phương thời gian), hệ số mang dấu âm và không có ý nghĩa thống kê. |
| **H3: Hiệu ứng biên lớn hơn ở nhóm CLMV** | M5 PPML Tương tác & Tổ hợp tuyến tính (Tầng A) | Chênh lệch tương tác: \(+0.660^{*}\)<br>Tổng tác động CLMV: \(1.186^{***}\) | Tương tác: \(p = 0.073\)<br>Tổng CLMV: \(p = 0.002\) | **Bằng chứng yếu ở mức 10% (Chưa đủ cơ sở ở mức 5%)**: Tổng tác động lên CLMV khác 0 rất mạnh (\(1.186^{***}\)), nhưng chênh lệch giữa CLMV và ASEAN-6 chỉ có ý nghĩa thống kê ở mức 10% (\(p = 0.073\)) và không đạt mức ý nghĩa 5%. |
| **H4: Tác động mạnh hơn với hàng chế tạo** | Bảng gộp đa ngành (Pooled Product PPML) & Hồi quy phân tách | Chênh lệch Chế tạo vs Nông sản: \(+0.614^{*}\)<br>Chế tạo (HS 28–96): \(1.118^{***}\)<br>Nông sản (HS 01–24): \(0.124\) | Chênh lệch: \(p = 0.074\)<br>Chế tạo: \(p = 0.005\)<br>Nông sản: \(p = 0.669\) | **Bằng chứng gợi ý ở mức 10% (Chưa đủ cơ sở ở mức 5%)**: Dù LSCI chỉ có ý nghĩa với chế tạo trong hồi quy riêng, kiểm định trực tiếp chênh lệch hệ số (Pooled difference test) cho thấy mức chênh \(+0.614\) chỉ đạt ý nghĩa ở mức 10% (\(p = 0.074\)), chưa đạt mức 5%. |

---

## 3. Các cải tiến kinh tế lượng chuẩn mực (Manuscript-Ready)

1. **Chuẩn hóa dữ liệu thương mại song phương**: Dữ liệu xuất khẩu của Việt Nam năm 2024 chưa báo cáo trên UN Comtrade được bảo lưu chính xác dưới dạng `NaN` (không điền số 0 giả mạo), loại bỏ 24 quan sát sai lệch làm méo mó mô hình trọng lực; mẫu ước lượng song phương đạt chính xác **3.082 quan sát, 207 cặp nước và 142 quan sát 0 thực tế**.
2. **Ước lượng Trọng lực cấu trúc đầy đủ (Full Structural Gravity)**: Triển khai thành công mô hình G1 với đồng thời Cặp quốc gia FE, Nước xuất khẩu-Năm FE và Nước nhập khẩu-Năm FE thông qua thuật toán phân rã QR có hoán vị cột (QR with pivoting) để khử 45 biến giả đa cộng tuyến hoàn hảo.
3. **Kiểm định trực tiếp khác biệt hệ số ngành hàng (Pooled Product PPML)**: Xây dựng bảng gộp 405 quan sát (9 nước x 15 năm x 3 nhóm hàng) để kiểm định trực tiếp chênh lệch giữa Chế tạo, Nông sản và Nhiên liệu, tránh lỗi ngụy biện so sánh chéo hệ số.
4. **Phân loại ngành hàng chuẩn xác (Bóc tách Dầu khí Brunei)**: Tách riêng nhóm Nhiên liệu & Khoáng sản (HS 25–27, chiếm 78% xuất khẩu Brunei) khỏi Công nghiệp Chế biến - Chế tạo thuần túy (HS 28–96), giải quyết triệt để biến dạng mẫu.
5. **Suy diễn thống kê mẫu nhỏ**: Toàn bộ mô hình áp dụng Clustered SE kèm phân phối Student-t với bậc tự do mẫu nhỏ (`use_t=True`, \(df = G - 1\)), không phóng đại giá trị p đối với 9 cụm quốc gia.
6. **Kiểm định xu hướng thời gian riêng của từng nước**: Hiệu ứng của LSCI vẫn giữ vững ý nghĩa thống kê dương (\(\beta = 0.328^{**}, p = 0.017\)) sau khi đưa vào xu hướng tuyến tính riêng của từng nước (`iso3:trend`).
7. **Kiểm định VIF tập trung và biến đổi cố định**: Bổ sung hằng số vào tính toán VIF, kết quả VIF tập trung đều dưới 12 và VIF sau khi trừ bình quân nhóm (Within-country) đều dưới 3.70, khẳng định không tồn tại vấn đề đa cộng tuyến nghiêm trọng.
8. **Tự động hóa hoàn toàn không hard-code**: Toàn bộ kết luận, bảng biểu, số liệu trong `summary_findings.json` và README được cập nhật động trực tiếp từ kết quả ước lượng mô hình theo đúng tiêu chí kiểm định thống kê khắt khe.

---

## 4. Cấu trúc kho mã nguồn

```text
.
├── config/                      # Cấu hình danh mục quốc gia & đối tác
│   ├── countries.csv            # 9 nước ASEAN ven biển làm mẫu chính
│   ├── partners.csv             # 24 đối tác xuất khẩu lớn toàn cầu
│   └── project_config.json      # Tham số chạy mô hình và phân định năm
├── data/
│   ├── raw/                     # Dữ liệu gốc bất biến (Immutable)
│   │   ├── unctad/              # LSCI và LSBCI từ UNCTADstat
│   │   ├── aseanstats/          # Kim ngạch xuất khẩu HS2 từ ASEANstats
│   │   ├── comtrade/            # Dòng xuất khẩu song phương UN Comtrade
│   │   ├── world_bank/          # GDP, Dân số, FDI, FX, REER từ WDI API
│   │   └── manifest.csv         # Bảng kiểm kê mã băm SHA-256 và nguồn gốc
│   ├── interim/                 # Dữ liệu trung gian sau chuẩn hóa
│   └── processed/               # Bảng phân tích hoàn chỉnh
│       ├── panel_country_year.csv      # Bảng Quốc gia - Năm (144 dòng)
│       └── panel_bilateral_year.csv    # Bảng Song phương (3.240 dòng)
├── src/                         # Toàn bộ pipeline xử lý & mô hình hóa
│   ├── clean_common.py          # Tiện ích chuẩn hóa ISO3, định dạng số p-val
│   ├── import_unctad.py         # Tiền xử lý chỉ số UNCTADstat
│   ├── import_trade.py          # Tiền xử lý xuất khẩu ASEANstats & Comtrade
│   ├── build_country_panel.py   # Xây dựng bảng panel_country_year
│   ├── build_bilateral_panel.py # Xây dựng bảng panel_bilateral_year
│   ├── validate_data.py         # Kiểm định hợp đồng dữ liệu & xuất báo cáo
│   ├── descriptive_analysis.py  # Thống kê mô tả & vẽ 5 biểu đồ 300 DPI
│   ├── model_country_panel.py   # Ước lượng OLS TWFE và PPML Tầng A
│   ├── model_gravity_ppml.py    # Ước lượng Structural Gravity PPML Tầng B
│   ├── robustness.py            # 11 kiểm định độ bền và độ nhạy
│   └── export_results.py        # Xuất bản tóm tắt kết quả JSON động
├── outputs/
│   ├── tables/                  # Bảng kết quả định dạng CSV, LaTeX & JSON
│   ├── figures/                 # Biểu đồ học thuật chuẩn 300 DPI (.png)
│   └── diagnostics/             # Báo cáo kiểm toán ghép dữ liệu & tỷ lệ khuyết
├── tests/
│   └── test_data_contracts.py   # Bộ unit test tự động (Pytest)
├── design.md                    # Bản thiết kế nghiên cứu chi tiết
├── code_review.md               # Báo cáo rà soát và giải pháp khắc phục
└── README.md
```

---

## 5. Hướng dẫn chạy tái lập (Reproducibility)

### Yêu cầu môi trường
- Python >= 3.10
- Thư viện: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `pytest`

### Các bước thực thi từ đầu
```bash
# 1. Chuyển đổi và làm sạch dữ liệu thô sang data/interim/
python src/import_unctad.py
python src/import_trade.py

# 2. Xây dựng hai bảng dữ liệu phân tích chuẩn
python src/build_country_panel.py
python src/build_bilateral_panel.py

# 3. Kiểm định hợp đồng dữ liệu & chạy unit test
python src/validate_data.py
python -m pytest tests/test_data_contracts.py -v

# 4. Xuất thống kê mô tả & biểu đồ
python src/descriptive_analysis.py

# 5. Ước lượng các mô hình kinh tế lượng
python src/model_country_panel.py
python src/model_gravity_ppml.py

# 6. Kiểm định độ bền & xuất bảng tổng hợp
python src/robustness.py
python src/export_results.py
```

---

## 6. Giấy phép
Dự án được phân phối dưới giấy phép GNU General Public License v3.0 (GPL-3.0). Xem [LICENSE](LICENSE) để biết thêm chi tiết.
