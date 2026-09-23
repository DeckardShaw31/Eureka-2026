# Maritime Connectivity and Merchandise Export Performance in ASEAN, 2010–2025: Evidence from PPML and an Extended Gravity Model

**Đề tài:** Kết nối vận tải biển và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN giai đoạn 2010–2025: Bằng chứng từ PPML và mô hình trọng lực mở rộng.

---

## 1. Giới thiệu tổng quan

Kho lưu trữ mã nguồn và dữ liệu thực nghiệm phục vụ bài nghiên cứu định lượng mối quan hệ giữa năng lực kết nối vận tải biển (Liner Shipping Connectivity Index - LSCI, Bilateral Liner Shipping Connectivity Index - LSBCI) và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN ven biển giai đoạn 2010–2025.

Nghiên cứu áp dụng phương pháp hồi quy Poisson Pseudo-Maximum Likelihood (PPML) theo chuẩn Santos Silva & Tenreyro (2006) và mô hình Trọng lực cấu trúc mở rộng (Yotov et al., 2016), xử lý triệt để hiện tượng phương sai thay đổi và giá trị thương mại bằng 0 (Zero Trade).

---

## 2. Kết quả kiểm định các giả thuyết cốt lõi

| Giả thuyết | Đặc tả thực nghiệm | Hệ số ước lượng | Ý nghĩa thống kê | Kết luận |
|---|---|---|---|---|
| **H1: LSCI tác động dương tới tổng xuất khẩu** | M1 & M2 PPML (Tầng A) | \(\beta_1 = 1.192^{***}\) | \(p = 0.0017\) | **Chấp nhận** (Tăng 1% LSCI gắn với mức tăng 1.19% xuất khẩu) |
| **H2: LSBCI thúc đẩy xuất khẩu song phương** | G1 Gravity PPML (Tầng B) | \(\beta_1 = 0.580^{**}\) | \(p = 0.0103\) | **Chấp nhận** (Tăng 1% LSBCI gắn với mức tăng 0.58% thương mại cặp nước) |
| **H3: Hiệu ứng biên lớn hơn ở CLMV** | M5 Tương tác (Tầng A) | \(\beta_{CLMV} = +0.660^{**}\) | \(p = 0.0387\) | **Chấp nhận** (CLMV có độ co giãn biên vượt trội so với ASEAN-6) |
| **H4: Tác động mạnh hơn với hàng chế tạo** | Robustness 7 & 8 | Chế tạo: \(1.134^{***}\)<br>Nông sản: \(0.124\) | Chế tạo: \(p = 0.0000\)<br>Nông sản: \(p = 0.658\) | **Chấp nhận** (Hàng công nghiệp phụ thuộc chặt chẽ vào vận tải container) |

---

## 3. Cấu trúc kho mã nguồn

```text
.
├── config/                      # Cấu hình danh mục quốc gia & đối tác
│   ├── countries.csv            # 9 nước ASEAN ven biển làm mẫu chính
│   ├── partners.csv             # 24 đối tác xuất khẩu lớn toàn cầu
│   └── project_config.json      # Tham số chạy mô hình và ngưỡng dữ liệu
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
│   ├── clean_common.py          # Tiện ích chuẩn hóa ISO3 và kiểm tra schema
│   ├── import_unctad.py         # Tiền xử lý chỉ số UNCTADstat
│   ├── import_trade.py          # Tiền xử lý xuất khẩu ASEANstats & Comtrade
│   ├── build_country_panel.py   # Xây dựng bảng panel_country_year
│   ├── build_bilateral_panel.py # Xây dựng bảng panel_bilateral_year
│   ├── validate_data.py         # Kiểm định hợp đồng dữ liệu & xuất báo cáo
│   ├── descriptive_analysis.py  # Thống kê mô tả & vẽ 5 biểu đồ 300 DPI
│   ├── model_country_panel.py   # Ước lượng OLS TWFE và PPML Tầng A
│   ├── model_gravity_ppml.py    # Ước lượng Gravity PPML Tầng B
│   ├── robustness.py            # 9 kiểm định độ bền và độ nhạy
│   └── export_results.py        # Xuất bản tóm tắt kết quả JSON/LaTeX
├── outputs/
│   ├── tables/                  # Bảng kết quả định dạng CSV & LaTeX (.tex)
│   ├── figures/                 # Biểu đồ học thuật chuẩn 300 DPI (.png)
│   └── diagnostics/             # Báo cáo kiểm toán ghép dữ liệu & tỷ lệ khuyết
├── tests/
│   └── test_data_contracts.py   # Bộ unit test tự động (Pytest)
├── design.md                    # Bản thiết kế nghiên cứu chi tiết
└── README.md
```

---

## 4. Hướng dẫn chạy tái lập (Reproducibility)

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

## 5. Giấy phép
Dự án được phân phối dưới giấy phép GNU General Public License v3.0 (GPL-3.0). Xem [LICENSE](LICENSE) để biết thêm chi tiết.
