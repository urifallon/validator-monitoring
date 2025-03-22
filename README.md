# Validator Monitoring API

Hệ thống API giám sát máy chủ VPS.

## Cấu trúc dự án

```
validator-monitoring/
├── api/                  # Package API
│   ├── __init__.py       # Factory app 
│   └── routes/           # Các route API
│       ├── __init__.py   # API Blueprint
│       ├── user_routes.py # API người dùng
│       └── vps_routes.py # API VPS
├── config/               # Cấu hình ứng dụng
│   └── __init__.py       # Cài đặt cấu hình
├── models/               # Mô hình dữ liệu
│   ├── __init__.py       # Cài đặt database
│   ├── user.py           # Mô hình User
│   └── vps.py            # Mô hình VPS
├── services/             # Các dịch vụ nghiệp vụ
│   ├── __init__.py
│   └── vps_service.py    # Dịch vụ VPS
├── app.py                # Entry point chính
├── create_database.py    # Script tạo dữ liệu mẫu
└── requirements.txt      # Các thư viện cần thiết
```

## Cài đặt

1. Tạo môi trường ảo Python:
   ```
   python -m venv venv
   ```

2. Kích hoạt môi trường ảo:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Cài đặt các gói phụ thuộc:
   ```
   pip install -r requirements.txt
   ```

4. Tạo dữ liệu mẫu:
   ```
   python create_database.py
   ```

5. Chạy ứng dụng:
   ```
   python app.py
   ```

## API Endpoints

### User API

- `POST /api/users/register`: Đăng ký người dùng mới
- `POST /api/users/login`: Đăng nhập
- `POST /api/users/logout`: Đăng xuất
- `GET /api/users/profile`: Lấy thông tin hồ sơ
- `PUT /api/users/profile`: Cập nhật hồ sơ

### VPS API

- `GET /api/vps`: Lấy danh sách VPS
- `GET /api/vps/<vps_id>`: Lấy thông tin chi tiết VPS
- `POST /api/vps`: Tạo VPS mới
- `PUT /api/vps/<vps_id>`: Cập nhật thông tin VPS
- `DELETE /api/vps/<vps_id>`: Xóa VPS
- `GET /api/vps/<vps_id>/status`: Kiểm tra trạng thái VPS

## Tài khoản mặc định

- Admin:
  - Username: admin
  - Password: admin123

- Test User:
  - Username: testuser
  - Password: password123