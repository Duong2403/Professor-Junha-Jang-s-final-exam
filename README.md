CPU Scheduler Simulator
1. Mục Đích
Chương trình mô phỏng các thuật toán lập lịch CPU, hỗ trợ người dùng:

Hiểu rõ cơ chế hoạt động của các thuật toán lập lịch CPU.
So sánh hiệu năng giữa các thuật toán qua các chỉ số:
Thời gian chờ trung bình (Average Waiting Time).
Thời gian quay vòng trung bình (Average Turnaround Time).
Số lần chuyển ngữ cảnh (Context Switches).
Hiệu suất sử dụng CPU (CPU Utilization).
Hỗ trợ các thuật toán:
FCFS (First Come First Serve).
SJF (Shortest Job First).
Round Robin.
Priority Scheduling (Preemptive & Non-Preemptive).
Multi-Level Feedback Queue.
Rate Monotonic (Real-time).
Earliest Deadline First (Real-time).
Ngoài ra, chương trình cung cấp các tiện ích:

Nhập dữ liệu thủ công, tạo dữ liệu ngẫu nhiên, hoặc nhập từ file (CSV, JSON).
Xuất kết quả và báo cáo.
2. Cách Cài Đặt
Yêu Cầu Hệ Thống
Python: Phiên bản >= 3.8.
Các thư viện cần thiết: Matplotlib, Numpy, Tkinter, v.v.
Các Bước Cài Đặt
Clone hoặc tải mã nguồn từ repository:
bash
Sao chép mã
git clone https://github.com/your-repository/cpu-scheduler-simulator.git
cd cpu-scheduler-simulator
Cài đặt các thư viện bằng lệnh:
bash
Sao chép mã
pip install -r requirements.txt
3. Cách Chạy Chương Trình
Khởi Động Chương Trình
Chạy lệnh sau trong thư mục gốc:
bash
Sao chép mã
python main.py
4. Hướng Dẫn Sử Dụng
Bước 1: Chọn Phương Thức Nhập Dữ Liệu
Nhập Thủ Công: Điền thông tin như ID, Arrival Time, Burst Time, Priority.
Tạo Dữ Liệu Ngẫu Nhiên: Đặt số lượng tiến trình và các thông số tối đa.
Nhập File: Sử dụng file CSV hoặc JSON với cấu trúc hợp lệ.
Bước 2: Chọn Thuật Toán Lập Lịch
Chọn thuật toán mong muốn từ danh sách:
FCFS, SJF, Round Robin, Priority Scheduling, v.v.
Tùy chỉnh thông số:
Quantum (cho Round Robin).
Số hàng đợi (cho Multi-Level Queue).
Bước 3: Mô Phỏng Lập Lịch
Nhấn Start để bắt đầu mô phỏng.
Theo dõi các thông tin:
Gantt Chart: Thứ tự thực thi tiến trình.
I/O Operations Log: Nhật ký hoạt động I/O.
Performance Metrics: Hiệu năng thuật toán.
Bước 4: Phân Tích và Xuất Kết Quả
Xem các chỉ số như thời gian chờ trung bình, throughput, số lần chuyển ngữ cảnh.
Xuất báo cáo chi tiết nếu cần.
5. Cấu Trúc Dự Án
plaintext
Sao chép mã
cpu-scheduler-simulator/
├── main.py               # File chính để chạy chương trình
├── requirements.txt      # Thư viện cần thiết
├── src/
│   ├── process/          # Định nghĩa cấu trúc tiến trình và trạng thái
│   ├── schedulers/       # Các thuật toán lập lịch
│   ├── utils/            # Tiện ích hỗ trợ tính toán và log
│   ├── visualization/    # Hiển thị biểu đồ Gantt
└── README.md             # Hướng dẫn sử dụng
6. Ví Dụ Về Input và Output
Input Mẫu (CSV)
csv
Sao chép mã
pid,arrival_time,burst_time,priority
1,0,5,1
2,1,3,2
3,2,8,1
Output Mẫu
Gantt Chart: Hiển thị biểu đồ thứ tự thực thi.
Performance Metrics:
Thời gian chờ trung bình: 2.67
Thời gian quay vòng trung bình: 9.33
Hiệu suất CPU: 85%
Số lần chuyển ngữ cảnh: 4
7. Báo Cáo Hiệu Năng
Chương trình tự động tạo báo cáo chi tiết, bao gồm:

Hiệu năng từng thuật toán.
So sánh giữa các thuật toán qua bảng và biểu đồ.
Nhận xét và đề xuất.
8. Liên Hệ
Nếu gặp vấn đề hoặc cần hỗ trợ:

Email: support@example.com
GitHub: GitHub Repository
less
Sao chép mã

---

### **Hướng Dẫn Đưa Vào `README.md`**
1. Mở file `README.md` bằng trình soạn thảo.
2. Sao chép nội dung trên và dán vào file.
3. Lưu file và đảm bảo định dạng Markdown được hiển thị đúng (ví dụ: trên GitHub). 

Bạn có thể chỉnh sửa các liên kết