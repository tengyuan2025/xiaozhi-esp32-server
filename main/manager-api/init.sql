-- 小智ESP32服务器数据库初始化脚本
-- 确保数据库存在并设置正确的字符集

CREATE DATABASE IF NOT EXISTS xiaozhi_esp32_server 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- 切换到目标数据库
USE xiaozhi_esp32_server;

-- 创建应用程序用户（如果不存在）
CREATE USER IF NOT EXISTS 'xiaozhi'@'%' IDENTIFIED BY 'xiaozhi123';

-- 授予权限
GRANT ALL PRIVILEGES ON xiaozhi_esp32_server.* TO 'xiaozhi'@'%';
GRANT ALL PRIVILEGES ON xiaozhi_esp32_server.* TO 'root'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 显示数据库信息
SELECT 'Database xiaozhi_esp32_server created successfully!' as status;