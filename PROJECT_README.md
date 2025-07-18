# Extended Attendance System for Odoo 17

A comprehensive multi-location attendance tracking system built as an Odoo 17 module with Docker Compose deployment.

## 🚀 Quick Start

1. **Clone and Start**:
   ```bash
   git clone <repository-url>
   cd odoo-17-docker-compose
   docker-compose up -d
   ```

2. **Install the Module**:
   ```bash
   python3 scripts/setup/update_module_list.py
   ```

3. **Test Installation**:
   ```bash
   python3 scripts/testing/test_simple_module.py
   ```

4. **Access Odoo**: http://localhost:10017/web

## 📦 What's Included

### Extended Attendance Module
- **Multi-Location Tracking**: Track attendance across different locations
- **Person Type Management**: Admin, Employee, Student, Guest, Owner types
- **Device Integration**: Support for RFID, biometric, QR codes
- **Custom Fields**: Extensible person data
- **Operating Hours**: Location-specific time restrictions
- **HTTP API**: Simple REST-like endpoints

### Demo Data
- 5 Person Types (Admin, Owner, Employee, Student, Guest)
- 5 Locations (Main Entrance, Reception, Office, Library, Hall A)
- Sample devices and configurations

## 🏗️ Project Structure

```
├── addons/
│   └── extended_attendance/     # Main module
├── scripts/
│   ├── setup/                   # Installation scripts
│   ├── testing/                 # Test scripts
│   └── utils/                   # Utility scripts
├── docker-compose.yml           # Docker configuration
└── README.md                    # This file
```

## 🔧 Configuration

### Default Credentials
- **URL**: http://localhost:10017
- **Database**: extended_attendance
- **Username**: admin@demo.com
- **Password**: admin

### Services
- **Odoo 17**: Port 10017
- **PostgreSQL 13**: Port 5432 (internal)

## 📡 API Endpoints

- `GET /api/status` - API status and available endpoints
- `GET /api/person-types` - List all person types
- `GET /api/locations` - List all locations

## 🧪 Testing

Run the test suite:
```bash
python3 scripts/testing/test_simple_module.py
```

## 📚 Documentation

- [Scripts Documentation](scripts/README.md)
- [Module Documentation](addons/extended_attendance/README.md)

## 🛠️ Development

The module is designed for easy extension and customization:
- Clean model structure
- Simple HTTP controllers
- Comprehensive demo data
- Well-documented code

## 📋 Features

✅ **Multi-Location Attendance**  
✅ **Person Type Management**  
✅ **Device Integration Support**  
✅ **Custom Fields**  
✅ **Operating Hours**  
✅ **HTTP API**  
✅ **Demo Data**  
✅ **Docker Deployment**  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
