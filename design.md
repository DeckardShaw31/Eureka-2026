# Thiết kế nghiên cứu và hệ thống dữ liệu

## 1. Tên đề tài đề xuất

**Kết nối vận tải biển và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN giai đoạn 2010--2025: Bằng chứng từ PPML và mô hình trọng lực mở rộng**

Tên tiếng Anh:

**Maritime Connectivity and Merchandise Export Performance in ASEAN, 2010--2025: Evidence from PPML and an Extended Gravity Model**

### Lưu ý về cách diễn đạt

- Chỉ gọi mô hình là **mô hình trọng lực** khi đơn vị quan sát là cặp nước xuất khẩu--nhập khẩu--năm (`exporter-importer-year`).
- Mô hình dùng tổng xuất khẩu của từng nước theo năm (`country-year`) là mô hình dữ liệu bảng, không phải mô hình trọng lực đúng nghĩa.
- Khi chưa giải quyết đầy đủ nội sinh, tiêu đề và kết luận nên dùng “mối quan hệ”, “liên hệ” hoặc “bằng chứng về tác động”, tránh khẳng định quan hệ nhân quả tuyệt đối.
- Năm 2025 chỉ được giữ trong tiêu đề nếu các biến chính có độ phủ đủ tốt. Nếu GDP, FDI hoặc thương mại năm 2025 còn thiếu nhiều, mô hình chính sẽ dùng 2010--2024; số liệu 2025 chỉ dùng cho phân tích mô tả/phụ lục và tên đề tài cần đổi tương ứng.

## 2. Mục tiêu và câu hỏi nghiên cứu

### 2.1. Mục tiêu tổng quát

Định lượng mối quan hệ giữa năng lực kết nối vận tải biển và hiệu quả xuất khẩu hàng hóa của các quốc gia ASEAN; đồng thời kiểm tra liệu mối quan hệ này khác nhau giữa các nhóm quốc gia và nhóm sản phẩm hay không.

### 2.2. Câu hỏi nghiên cứu

1. LSCI tăng có gắn với sự gia tăng tổng giá trị xuất khẩu hàng hóa của các quốc gia ASEAN không?
2. Kết nối vận tải biển song phương (LSBCI) có gắn với dòng thương mại song phương lớn hơn không?
3. Mối quan hệ có khác nhau giữa ASEAN-6 và nhóm CLMV không?
4. Kết nối vận tải biển có liên hệ mạnh hơn với xuất khẩu hàng chế biến, chế tạo so với nông--thủy sản không?
5. Kết quả có bền vững khi thay đổi cách đo biến, dùng biến trễ và loại các năm COVID-19 không?

### 2.3. Giả thuyết

- **H1:** LSCI cao hơn có quan hệ dương với giá trị xuất khẩu hàng hóa.
- **H2:** LSBCI song phương cao hơn có quan hệ dương với xuất khẩu song phương.
- **H3:** Tác động cận biên của kết nối vận tải biển khác nhau giữa ASEAN-6 và CLMV.
- **H4:** Kết nối vận tải biển có tác động lớn hơn đối với hàng chế biến, chế tạo.

## 3. Phạm vi nghiên cứu

### 3.1. Không gian

Mẫu cơ sở gồm 9 nền kinh tế ASEAN có biển và có thể quan sát LSCI:

| Mã ISO3 | Quốc gia |
|---|---|
| BRN | Brunei Darussalam |
| KHM | Cambodia |
| IDN | Indonesia |
| MYS | Malaysia |
| MMR | Myanmar |
| PHL | Philippines |
| SGP | Singapore |
| THA | Thailand |
| VNM | Viet Nam |

- Lào được loại khỏi mẫu chính vì không có đường bờ biển và không có LSCI tương đương.
- Timor-Leste được trình bày trong phần phạm vi nghiên cứu nhưng không đưa vào mẫu cơ sở do thay đổi tư cách thành viên ASEAN vào cuối kỳ nghiên cứu và nguy cơ thiếu dữ liệu chuỗi thời gian. Có thể bổ sung trong kiểm định độ nhạy nếu dữ liệu đầy đủ.
- Với mô hình trọng lực, đối tác nhập khẩu nên gồm các nước ASEAN còn lại và khoảng 15--20 thị trường xuất khẩu lớn, được chọn theo **tổng kim ngạch của toàn giai đoạn**, không chọn riêng theo từng năm để tránh thiên lệch hậu nghiệm.

### 3.2. Thời gian

- Mục tiêu: 2010--2025.
- Mẫu hồi quy an toàn dự kiến: 2010--2024.
- Năm 2025: chỉ đưa vào mô hình khi có dữ liệu đủ cho ít nhất 80% quan sát của các biến bắt buộc.
- Dữ liệu quý LSCI/LSBCI được chuyển thành dữ liệu năm bằng trung bình số học của các quý có sẵn; một năm cần tối thiểu 3 quý để được giữ lại.

## 4. Chiến lược thực nghiệm hai tầng

## 4.1. Tầng A -- mô hình quốc gia--năm

Đây là mô hình tối thiểu khả thi để hoàn thành bài trong thời gian ngắn.

Đơn vị quan sát: quốc gia (i), năm (t).

### Mô hình tham chiếu OLS hai chiều

\[
\ln(Export_{it}) = \beta_1\ln(LSCI_{it})
+ \beta_2\ln(GDP_{it})
+ \beta_3\ln(POP_{it})
+ \beta_4 REER_{it}
+ \beta_5 FDI_{it}
+ \mu_i + \lambda_t + \varepsilon_{it}.
\]

Trong đó, \(\mu_i\) là hiệu ứng cố định quốc gia và \(\lambda_t\) là hiệu ứng cố định năm.

### Mô hình PPML chính

\[
E(Export_{it}\mid X_{it}) =
\exp\left[
\beta_1\ln(LSCI_{it}) + \gamma'Z_{it} + \mu_i + \lambda_t
\right].
\]

PPML được dùng dù tổng xuất khẩu hiếm khi bằng 0, vì mô hình không yêu cầu log biến phụ thuộc và thường phù hợp hơn OLS log-tuyến tính khi phương sai thay đổi. Sai số chuẩn cần robust và nên phân cụm theo quốc gia; tuy nhiên chỉ có khoảng 9 cụm nên p-value phải được diễn giải thận trọng.

### Cấu hình mô hình

1. M1: chỉ có `ln_lsci`, hiệu ứng cố định quốc gia và năm.
2. M2: thêm `ln_gdp` và `ln_population`.
3. M3: thêm `reer` và `fdi_gdp`.
4. M4: thay `ln_lsci` bằng `ln_lsci_lag1` để giảm nguy cơ quan hệ đồng thời.
5. M5: thêm tương tác `ln_lsci × clmv`.

Không đưa tất cả biến kiểm soát vào một cách máy móc. Với mẫu nhỏ, GDP và dân số có thể đồng biến mạnh; VIF và ma trận tương quan phải được kiểm tra trước.

## 4.2. Tầng B -- mô hình trọng lực song phương

Đây là phần nâng cấp có giá trị học thuật cao hơn.

Đơn vị quan sát: nước xuất khẩu (i), nước nhập khẩu (j), năm (t).

\[
E(X_{ijt}\mid Z_{ijt}) =
\exp\left[
\beta_1\ln(LSBCI_{ijt})
+ \delta_{ij}
+ \alpha_{it}
+ \gamma_{jt}
\right].
\]

Trong đó:

- \(X_{ijt}\): giá trị xuất khẩu hàng hóa từ (i) sang (j).
- \(LSBCI_{ijt}\): chỉ số kết nối vận tải biển song phương.
- \(\delta_{ij}\): hiệu ứng cố định cặp quốc gia.
- \(\alpha_{it}\): hiệu ứng cố định nước xuất khẩu--năm.
- \(\gamma_{jt}\): hiệu ứng cố định nước nhập khẩu--năm.

Mô hình này hấp thụ các yếu tố không đổi theo cặp nước và các cú sốc riêng của nước xuất khẩu/nhập khẩu theo năm. Khi đã dùng hiệu ứng cố định xuất khẩu--năm và nhập khẩu--năm, GDP, dân số, tỷ giá và LSCI đơn phương bị hấp thụ; không đưa chúng vào cùng mô hình.

### Vì sao dùng LSBCI thay cho LSCI trong mô hình trọng lực đầy đủ?

LSCI chỉ thay đổi theo nước--năm. Hiệu ứng cố định nước xuất khẩu--năm sẽ hấp thụ hoàn toàn LSCI của nước xuất khẩu, khiến hệ số không thể được nhận dạng. LSBCI thay đổi theo cặp nước--năm nên vẫn có thể ước lượng trong đặc tả trọng lực có hiệu ứng cố định đầy đủ.

### Phương án rút gọn nếu không lấy kịp LSBCI

Ước lượng PPML với hiệu ứng cố định cặp nước và năm:

\[
E(X_{ijt}\mid Z_{ijt}) =
\exp\left[
\beta_1\ln(LSCI_{it})
+ \beta_2\ln(GDP_{it})
+ \beta_3\ln(GDP_{jt})
+ \delta_{ij} + \lambda_t
\right].
\]

Đây chỉ là mô hình trọng lực mở rộng rút gọn, không kiểm soát đầy đủ sức cản đa phương. Phải trình bày nó như kiểm định bổ sung, không phải đặc tả chuẩn mạnh nhất.

## 4.3. Không ưu tiên System GMM

System GMM phù hợp hơn với bảng có số đơn vị chéo lớn và số kỳ nhỏ. Mẫu hiện tại chỉ có khoảng 9 nước nhưng 15--16 năm, nên GMM dễ gặp vấn đề quá nhiều công cụ, kiểm định Hansen yếu và kết quả không ổn định. Vì vậy:

- Không dùng System GMM làm kết quả chính.
- Dùng PPML, hiệu ứng cố định, biến trễ và các kiểm định độ nhạy.
- Chỉ bổ sung GMM nếu sau này mở rộng được mẫu ra nhiều quốc gia ngoài ASEAN và có lý do nhận dạng rõ ràng.

## 5. Danh mục dữ liệu

## 5.1. Kết nối vận tải biển

| Trường chuẩn | Nội dung | Tần suất gốc | Xử lý |
|---|---|---:|---|
| `iso3` | Mã quốc gia | -- | Chuẩn ISO3 |
| `year`, `quarter` | Thời gian | Quý/tháng | Quy đổi về năm |
| `lsci` | Liner Shipping Connectivity Index | Quý/tháng | Trung bình năm |
| `exporter_iso3` | Nước xuất khẩu | -- | Mô hình song phương |
| `importer_iso3` | Nước nhập khẩu | -- | Mô hình song phương |
| `lsbci` | Bilateral Liner Shipping Connectivity Index | Quý | Trung bình năm |

Nguồn ưu tiên:

- [UNCTADstat Data Centre](https://unctadstat.unctad.org/)
- [UNCTAD Data Hub -- Transport and Trade Facilitation](https://unctadstat.unctad.org/datacentre/)
- [UNCTAD Liner shipping connectivity indicators](https://unctad.org/topic/transport-and-trade-logistics/transport-statistics)

Cách lấy:

1. Chọn bộ dữ liệu LSCI hoặc LSBCI trên UNCTADstat.
2. Chọn toàn bộ quốc gia/cặp quốc gia cần thiết và giai đoạn từ 2010.
3. Xuất CSV, không ưu tiên Excel để tránh phụ thuộc thư viện đọc `.xlsx`.
4. Lưu nguyên trạng với tên chứa ngày tải, ví dụ `lsci_2010_2025_download_2026-09-23.csv`.
5. Lưu kèm metadata hoặc ảnh chụp cấu hình bộ lọc nếu giao diện không tạo được URL cố định.

Kiểm tra đặc biệt:

- Đọc metadata để phát hiện thay đổi cơ sở chỉ số hoặc phương pháp tính.
- Kiểm tra Singapore không lấn át đồ thị và thống kê; báo cáo cả kết quả có và không có Singapore.
- Không nội suy LSCI nếu thiếu cả năm. Nếu chỉ thiếu một quý, có thể lấy trung bình các quý còn lại và gắn cờ `lsci_partial_year=1`.

## 5.2. Xuất khẩu hàng hóa

### Nguồn chính cho mô hình quốc gia--năm

- [ASEANstats Data Portal](https://data.aseanstats.org/)
- Nhóm dữ liệu: International Merchandise Trade Statistics / Trade in Goods.
- Chỉ tiêu: tổng xuất khẩu hàng hóa, giá trị danh nghĩa USD, theo nước và năm.

Trường cần lấy:

| Trường chuẩn | Nội dung |
|---|---|
| `iso3` | Nước báo cáo |
| `year` | Năm |
| `export_usd` | Tổng giá trị xuất khẩu hàng hóa, USD |
| `trade_source` | `ASEANstats` hoặc nguồn thay thế |
| `provisional` | Cờ dữ liệu sơ bộ |

### Nguồn chính cho mô hình song phương

- [UN Comtrade Data](https://comtradeplus.un.org/)
- [UN Comtrade API Portal](https://comtradeapi.un.org/)
- [UN Comtrade API documentation](https://uncomtrade.org/docs/)

Cấu hình tải đề xuất:

- Reporter: 9 nước ASEAN ven biển.
- Partner: các nước ASEAN và 15--20 thị trường lớn được chốt trước.
- Flow: Exports.
- Frequency: Annual.
- Classification: giữ một phiên bản phân loại nhất quán nếu phân tích sản phẩm.
- Commodity: `TOTAL` cho mô hình chính; nhóm sản phẩm cho phân tích mở rộng.
- Trade value: USD.

Quy tắc so sánh nguồn:

1. ASEANstats là nguồn chính cho tổng xuất khẩu quốc gia.
2. UN Comtrade là nguồn chính cho dòng thương mại song phương và sản phẩm.
3. Không ghép luân phiên hai nguồn trong cùng một chuỗi nếu chưa kiểm tra định nghĩa.
4. Tính tổng xuất khẩu từ dữ liệu song phương và so với tổng của ASEANstats. Nếu chênh quá 10%, lập bảng kiểm tra nguyên nhân.
5. Giữ nguyên giá trị thương mại bằng 0; không thay bằng giá trị rất nhỏ trước PPML.

## 5.3. Biến kiểm soát World Bank

Nguồn:

- [World Bank Open Data](https://data.worldbank.org/)
- [World Bank Indicators API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)
- API mẫu: `https://api.worldbank.org/v2/country/VNM/indicator/NY.GDP.MKTP.CD?format=json&per_page=100`

| Biến | Mã World Bank | Đơn vị/cách dùng |
|---|---|---|
| GDP | `NY.GDP.MKTP.CD` | USD hiện hành; dùng `ln_gdp` |
| Dân số | `SP.POP.TOTL` | Người; dùng `ln_population` |
| FDI ròng | `BX.KLT.DINV.WD.GD.ZS` | % GDP; ưu tiên vì so sánh được giữa nước |
| Tỷ giá danh nghĩa | `PA.NUS.FCRF` | Nội tệ/USD; chỉ dùng tốc độ thay đổi, không so sánh mức giữa nước |
| Tỷ giá thực hiệu lực | `PX.REX.REER` | Chỉ số; ưu tiên nếu độ phủ dữ liệu đủ |

Quy tắc:

- Không dùng trực tiếp mức tỷ giá nội tệ/USD để so sánh giữa các nước vì đơn vị tiền tệ khác nhau.
- Nếu REER thiếu nhiều, dùng phần trăm thay đổi tỷ giá chính thức hoặc loại tỷ giá khỏi mô hình cơ sở.
- GDP và xuất khẩu đều là USD hiện hành nên có thể chịu ảnh hưởng của lạm phát và tỷ giá. Kiểm định độ nhạy bằng xuất khẩu USD cố định nếu tìm được deflator phù hợp, hoặc thêm hiệu ứng cố định năm.
- Dữ liệu World Bank tải qua API và lưu phản hồi thô trước khi làm sạch.

## 5.4. Phân nhóm sản phẩm

Phân tích này là phần mở rộng, chỉ làm sau khi mô hình tổng đã chạy ổn định.

Phương án đơn giản:

- Nông--thủy sản và thực phẩm: HS 01--24.
- Hàng chế biến, chế tạo: HS 25--97, báo cáo riêng hoặc loại khoáng sản/nhiên liệu HS 25--27 trong một kiểm định độ nhạy.

Rủi ro:

- Phiên bản HS thay đổi theo thời gian.
- Cần dùng bảng concordance hoặc tải dữ liệu theo một phân loại nhất quán.
- Không tự động coi HS 25--97 là toàn bộ “manufacturing” mà không giải thích các chương khoáng sản, nhiên liệu và hàng đặc biệt.

## 5.5. Biến phân nhóm ASEAN-6 và CLMV

| Nhóm | Thành viên dùng trong nghiên cứu |
|---|---|
| ASEAN-6 | BRN, IDN, MYS, PHL, SGP, THA |
| CLMV | KHM, LAO, MMR, VNM |

Trong mẫu LSCI chính, Lào không có quan sát nên biến `clmv=1` áp dụng cho Cambodia, Myanmar và Viet Nam. Cần nêu rõ đây là “các nước CLMV có biển trong mẫu”, không diễn giải như toàn bộ CLMV.

## 6. Từ điển dữ liệu bảng phân tích

## 6.1. `panel_country_year.csv`

| Biến | Kiểu | Mô tả |
|---|---|---|
| `iso3` | string | Khóa quốc gia |
| `country` | string | Tên chuẩn |
| `year` | int | 2010--2025 |
| `export_usd` | float | Tổng xuất khẩu hàng hóa |
| `lsci` | float | LSCI trung bình năm |
| `gdp_usd` | float | GDP hiện hành |
| `population` | float | Dân số |
| `fdi_gdp` | float | FDI ròng, % GDP |
| `reer` | float | Tỷ giá thực hiệu lực |
| `official_fx` | float | Tỷ giá chính thức |
| `clmv` | int | 1 nếu thuộc nhóm CLMV có biển |
| `asean6` | int | 1 nếu thuộc ASEAN-6 |
| `covid` | int | 1 cho 2020--2021 |
| `ln_export` | float | Log tự nhiên của xuất khẩu dương |
| `ln_lsci` | float | `log(lsci)` |
| `ln_gdp` | float | `log(gdp_usd)` |
| `ln_population` | float | `log(population)` |
| `ln_lsci_lag1` | float | LSCI trễ một năm theo nước |
| `data_complete` | int | Đủ biến cho đặc tả đầy đủ |

## 6.2. `panel_bilateral_year.csv`

| Biến | Kiểu | Mô tả |
|---|---|---|
| `exporter_iso3` | string | Nước xuất khẩu |
| `importer_iso3` | string | Nước nhập khẩu |
| `year` | int | Năm |
| `trade_usd` | float | Xuất khẩu song phương; giữ số 0 |
| `lsbci` | float | Chỉ số kết nối song phương |
| `product_group` | string | `total`, `agri_food`, `manufacturing` |
| `pair_id` | string | `exporter_iso3-importer_iso3` |
| `exporter_year` | string | Khóa hiệu ứng cố định |
| `importer_year` | string | Khóa hiệu ứng cố định |
| `ln_lsbci` | float | `log(lsbci)` nếu dương |
| `source_flag` | string | Nguồn thương mại |

## 7. Quy trình xử lý dữ liệu

### Bước 1 -- đóng băng dữ liệu thô

- Không chỉnh sửa file tải về.
- Tên file chứa nguồn và ngày tải.
- Tạo `data/raw/manifest.csv` ghi URL, ngày tải, bộ lọc, đơn vị và checksum SHA-256.

### Bước 2 -- chuẩn hóa khóa

- Dùng ISO3 làm khóa quốc gia.
- Chuẩn hóa các tên đặc biệt như `Viet Nam`, `Brunei Darussalam`, `Lao PDR` và `Myanmar`.
- Kiểm tra mỗi bảng chỉ có một quan sát trên khóa dự kiến trước khi merge.

### Bước 3 -- chuẩn hóa thời gian

- Chuyển quý/tháng về năm.
- LSCI/LSBCI năm là trung bình các kỳ hợp lệ.
- Tạo cờ số kỳ quan sát trong mỗi năm.

### Bước 4 -- chuẩn hóa đơn vị

- Giá trị thương mại và GDP về USD.
- Không trộn nghìn USD và USD.
- Không chuyển giá trị 0 thành thiếu.
- Giá trị âm hoặc không hợp lệ được gắn cờ, không âm thầm xóa.

### Bước 5 -- ghép dữ liệu

1. Tạo khung đầy đủ `9 nước × 16 năm`.
2. Ghép xuất khẩu, LSCI và World Bank bằng `iso3-year`.
3. Xuất báo cáo `merge_audit.csv` ghi số dòng matched/unmatched theo nguồn.
4. Với dữ liệu song phương, tạo khung `exporter-importer-year` trước khi ghép để giữ quan sát thương mại bằng 0.

### Bước 6 -- biến đổi

- Log chỉ áp dụng cho biến dương.
- PPML dùng biến phụ thuộc ở mức, không dùng `ln_export` hoặc `ln_trade` làm biến phụ thuộc.
- Winsorize không phải mặc định. Nếu dùng, báo cáo cả kết quả gốc và kết quả winsorize.
- Tạo biến trễ sau khi sắp xếp theo quốc gia và năm; không để trễ nhảy qua năm bị thiếu.

### Bước 7 -- kiểm tra chất lượng

- Khóa dữ liệu không trùng.
- Không có năm ngoài phạm vi.
- Không có giá trị LSCI/LSBCI âm.
- Tỷ lệ thiếu theo biến, nước và năm.
- So sánh tổng xuất khẩu từ hai nguồn.
- Kiểm tra điểm ngoại lai bằng bảng percentile và đồ thị, không xóa tự động.
- Kiểm tra dữ liệu năm 2025 có phải provisional.

## 8. Thiết kế codebase

```text
.
├── main.tex
├── design.md
├── config/
│   ├── countries.csv
│   ├── partners.csv
│   └── project_config.json
├── data/
│   ├── raw/
│   │   ├── unctad/
│   │   ├── aseanstats/
│   │   ├── comtrade/
│   │   ├── world_bank/
│   │   └── manifest.csv
│   ├── interim/
│   └── processed/
│       ├── panel_country_year.csv
│       └── panel_bilateral_year.csv
├── src/
│   ├── download_world_bank.py
│   ├── import_unctad.py
│   ├── import_trade.py
│   ├── clean_common.py
│   ├── build_country_panel.py
│   ├── build_bilateral_panel.py
│   ├── validate_data.py
│   ├── descriptive_analysis.py
│   ├── model_country_panel.py
│   ├── model_gravity_ppml.py
│   ├── robustness.py
│   └── export_results.py
├── outputs/
│   ├── tables/
│   ├── figures/
│   ├── diagnostics/
│   └── logs/
└── tests/
    └── test_data_contracts.py
```

Không cần tạo môi trường Python mới hoặc cài thêm thư viện. Code có thể dùng `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib` và `seaborn` có sẵn. Ưu tiên CSV thay vì XLSX.

## 9. System design

```text
UNCTAD CSV ───────┐
ASEANstats CSV ───┼─> raw immutable files ─> cleaners ─> validated panels
Comtrade API/CSV ─┤                                      │
World Bank API ───┘                                      ├─> descriptive outputs
                                                         ├─> country PPML/TWFE
                                                         ├─> gravity PPML
                                                         └─> tables/figures for LaTeX
```

### Nguyên tắc

1. **Reproducible:** mọi bảng và hình trong bài phải tạo lại được từ script.
2. **Immutable raw data:** dữ liệu thô không bị sửa.
3. **Single source of truth:** mô hình chỉ đọc dữ liệu trong `data/processed/`.
4. **Fail loudly:** script dừng nếu khóa trùng, sai đơn vị hoặc merge mất quá nhiều dòng.
5. **Traceable:** mỗi kết quả lưu kèm thời gian chạy, công thức mô hình, số quan sát và mẫu sử dụng.

### Cấu hình `project_config.json`

```json
{
  "start_year": 2010,
  "end_year": 2025,
  "min_quarters_per_year": 3,
  "min_2025_coverage": 0.8,
  "main_trade_source": "ASEANstats",
  "bilateral_trade_source": "UNComtrade",
  "cluster_variable": "iso3",
  "exclude_countries_main": ["LAO", "TLS"]
}
```

## 10. Thiết kế script

### `download_world_bank.py`

- Gọi API theo mã chỉ tiêu và danh sách ISO3.
- Lưu JSON thô và CSV chuẩn hóa.
- Retry có giới hạn; log URL và mã trạng thái.
- Không ghi đè file thô cũ nếu nội dung thay đổi mà chưa lưu phiên bản.

### `import_unctad.py`

- Đọc CSV tải thủ công từ UNCTADstat.
- Ánh xạ tên nước sang ISO3.
- Chuyển dữ liệu dài/rộng về định dạng tidy.
- Tổng hợp quý thành năm và tạo cờ số quý.

### `import_trade.py`

- Đọc ASEANstats cho tổng xuất khẩu.
- Đọc hoặc tải UN Comtrade theo từng reporter/năm để tránh truy vấn quá lớn.
- Cache từng phản hồi, giữ số 0, chuẩn hóa USD.

### `validate_data.py`

Các assertion tối thiểu:

```text
unique(iso3, year)
unique(exporter_iso3, importer_iso3, year, product_group)
export_usd >= 0
trade_usd >= 0
lsci > 0 where observed
lsbci >= 0 where observed
year between 2010 and 2025
```

Xuất các báo cáo:

- `missingness.csv`
- `duplicate_keys.csv`
- `merge_audit.csv`
- `source_comparison.csv`
- `2025_coverage.csv`

### `model_country_panel.py`

- OLS log-tuyến tính với dummy quốc gia và năm.
- GLM Poisson/PPML với log link.
- Covariance robust và clustered theo nước khi khả thi.
- Lưu hệ số, sai số chuẩn, p-value, khoảng tin cậy, N và pseudo log-likelihood.

### `model_gravity_ppml.py`

- PPML với hiệu ứng cố định cặp, xuất khẩu--năm và nhập khẩu--năm.
- Bắt và báo hiện tượng perfect prediction/separation.
- Kiểm tra hội tụ; không xuất bảng nếu mô hình chưa hội tụ.
- Với `statsmodels`, có thể tạo categorical dummies vì quy mô mẫu ASEAN vẫn quản lý được. Nếu mô hình mở rộng quá lớn, giảm số đối tác thay vì cài thêm package.

## 11. Kế hoạch phân tích

### 11.1. Thống kê mô tả

- Bảng thống kê các biến.
- Độ phủ dữ liệu theo năm và quốc gia.
- Xu hướng LSCI và xuất khẩu của từng nước.
- Scatter plot LSCI--xuất khẩu, tô màu theo nhóm nước.
- So sánh trước COVID-19, giai đoạn 2020--2021 và sau 2021.

### 11.2. Kết quả chính

- Bảng OLS FE và PPML đặt cạnh nhau.
- Báo cáo hệ số dưới dạng semi-elasticity hoặc elasticity phù hợp với cách log biến.
- Không diễn giải chỉ dựa vào p-value; báo cáo độ lớn và khoảng tin cậy.

### 11.3. Kiểm định độ bền

1. LSCI hiện tại và LSCI trễ một năm.
2. Có và không có Singapore.
3. Mẫu 2010--2019, 2010--2024 và toàn bộ dữ liệu có thể dùng.
4. Loại năm 2020--2021.
5. ASEAN-6 so với các nước CLMV có biển.
6. Tổng hàng hóa so với nông--thủy sản và chế biến, chế tạo.
7. So sánh OLS FE và PPML.

### 11.4. Rủi ro nội sinh

Xuất khẩu tăng có thể thúc đẩy đầu tư cảng và làm LSCI tăng. Các bước giảm rủi ro:

- Dùng LSCI trễ một năm.
- Dùng hiệu ứng cố định quốc gia/cặp nước và năm.
- Thực hiện placebo: LSCI tương lai không nên “giải thích” xuất khẩu hiện tại.
- Viết kết luận thận trọng.

Các bước trên không tự động biến kết quả thành quan hệ nhân quả. Một thiết kế nhân quả mạnh hơn cần biến công cụ, cú sốc ngoại sinh hoặc thiết kế quasi-experimental có lập luận riêng.

## 12. Bảng và hình dự kiến cho bài

### Bảng

1. Định nghĩa biến và nguồn dữ liệu.
2. Thống kê mô tả.
3. Ma trận tương quan và VIF.
4. Kết quả country-year OLS FE/PPML.
5. Kết quả gravity PPML.
6. Phân tích dị biệt ASEAN-6/CLMV.
7. Kiểm định độ bền.

### Hình

1. LSCI trung bình theo quốc gia.
2. Xu hướng LSCI và xuất khẩu.
3. Scatter plot có đường xu hướng.
4. Hệ số và khoảng tin cậy từ các đặc tả.
5. Heatmap LSBCI hoặc mạng lưới kết nối hàng hải, nếu dữ liệu cho phép.

## 13. Tiêu chí quyết định phạm vi vào ngày 23--25/09/2026

### MVP bắt buộc

- Dữ liệu country-year 2010--2024.
- LSCI, xuất khẩu, GDP và dân số.
- Thống kê mô tả.
- OLS FE và PPML.
- Một kiểm định dùng LSCI trễ.
- Viết rõ hạn chế nội sinh.

### Phần nâng cấp nếu còn thời gian

1. REER và FDI.
2. Tương tác ASEAN-6/CLMV.
3. Gravity PPML với LSBCI.
4. Phân nhóm sản phẩm.

Không hy sinh độ chính xác của mô hình cơ sở để chạy quá nhiều phân tích mở rộng.

## 14. Lịch triển khai cấp tốc

### Ngày 23/09/2026

- Khóa tên đề tài và phạm vi.
- Tải LSCI, ASEANstats và World Bank.
- Tạo country-year panel.
- Kiểm tra độ phủ năm 2025.
- Chạy thống kê mô tả đầu tiên.

### Ngày 24/09/2026

- Chạy OLS FE và PPML.
- Làm kiểm định độ bền tối thiểu.
- Tạo bảng, hình và viết phương pháp/kết quả.
- Nếu dữ liệu thuận lợi, bắt đầu LSBCI và gravity PPML.

### Ngày 25/09/2026

- Kiểm tra toàn bộ con số giữa code, bảng và nội dung.
- Chốt tiêu đề theo năm dữ liệu thực sự dùng.
- Hoàn thiện tóm tắt, đóng góp, hạn chế và hàm ý chính sách.
- Nộp phiên bản có thể tái lập; không thêm mô hình chưa kiểm tra hội tụ.

## 15. Tiêu chí thành công

- Có một bộ dữ liệu sạch, truy xuất được nguồn.
- Mọi bảng/hình được tạo tự động từ code.
- Phân biệt rõ mô hình country-year và mô hình trọng lực song phương.
- PPML được dùng đúng với biến phụ thuộc ở mức.
- Không khẳng định nhân quả quá mức.
- Năm 2025 chỉ xuất hiện trong tiêu đề nếu dữ liệu thực sự hỗ trợ.
- Kết quả có ít nhất một hàm ý chính sách cụ thể cho Việt Nam.

## 16. Tài liệu phương pháp nền tảng cần trích dẫn

- Tinbergen, J. (1962), *Shaping the World Economy: Suggestions for an International Economic Policy*.
- Anderson, J. E. & van Wincoop, E. (2003), “Gravity with Gravitas: A Solution to the Border Puzzle”, *American Economic Review*, 93(1), 170--192. [DOI](https://doi.org/10.1257/000282803321455214)
- Santos Silva, J. M. C. & Tenreyro, S. (2006), “The Log of Gravity”, *The Review of Economics and Statistics*, 88(4), 641--658. [DOI](https://doi.org/10.1162/rest.88.4.641)
- Yotov, Y. V., Piermartini, R., Monteiro, J.-A. & Larch, M. (2016), *An Advanced Guide to Trade Policy Analysis: The Structural Gravity Model*. [WTO publication](https://www.wto.org/english/res_e/booksp_e/advancedwtounctad2016_e.pdf)

Các tài liệu này cung cấp nền tảng cho mô hình trọng lực và PPML; chúng không thay thế việc giải thích rõ giới hạn nhận dạng của bộ dữ liệu ASEAN đang sử dụng.