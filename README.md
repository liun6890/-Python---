# 基于 Python 的仓储物流管理系统

## 毕业设计课题

本项目是一个面向中小型仓储企业的仓储物流管理系统，毕业设计课题名称为**基于 Python 的仓储物流管理系统**。系统采用前后端分离架构，实现商品、仓库、库位、供应商、客户以及入库、出库、库存和报表等业务的数字化管理，帮助仓储人员减少人工登记，提高库存数据的准确性和业务处理效率。

## 课题目标

- 分析仓储物流业务流程，建立清晰的业务模型和数据库模型。
- 使用 Python 和 Django REST Framework 实现稳定、可扩展的后端接口。
- 使用 Vue 3 构建直观的管理端界面，覆盖仓储业务的主要操作流程。
- 实现库存数量、库位分配和出入库状态的自动校验，降低库存差错风险。
- 提供统计报表和操作日志，为仓储运营分析和系统审计提供依据。

## 主要功能

### 基础资料

- 用户、角色和权限管理
- 仓库与库位管理
- 商品、供应商和客户管理
- 用户登录、退出和个人资料维护

### 入库管理

- 入库单创建、审核和收货
- 商品上架和库位分配
- 入库单状态跟踪与审核备注

### 出库管理

- 出库单创建、审核和拣货
- 出库执行与发货确认
- 出库明细和业务状态跟踪

### 库存管理

- 库存查询和库存预警
- 库存盘点与盘点差异记录
- 库存调拨和库位库存维护
- 库位容量及商品库存上限校验

### 数据统计

- 工作台库存、入库和出库概览
- 库存分布与趋势图表
- 日报和业务统计报表
- 系统操作日志查询

## 技术栈

### 后端

- Python 3
- Django 4.1
- Django REST Framework
- Simple JWT
- drf-yasg（接口文档）
- SQLite（默认开发数据库）或 MySQL

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- Element Plus
- Axios
- ECharts
- Playwright（端到端测试）

## 项目结构

```text
.
├── backend/                 # Django 后端与 REST API
│   ├── api/                 # 业务模型、接口、迁移和初始化数据
│   ├── app/                 # Django 项目配置
│   ├── requirements.txt     # Python 依赖
│   └── wms_db_dump.sql      # 数据库结构及示例数据导出
├── frontend/                # Vue 3 前端管理端
│   ├── src/                 # 页面、组件、路由、状态和 API 封装
│   ├── package.json         # 前端依赖和脚本
│   └── tests/               # Playwright 测试
├── docs/                    # 需求、架构、接口和业务说明
├── start-dev.ps1            # Windows 一键启动脚本
└── STARTUP.md               # 启动说明
```

## 本地运行

### 1. 启动后端（SQLite 开发模式）

```powershell
cd backend
python -m venv .venv
\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

首次运行可以使用初始化脚本生成演示数据：

```powershell
python rebuild_data.py
```

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端默认地址为 `http://127.0.0.1:5173`，后端 API 地址为 `http://127.0.0.1:8000/api`。

### 3. Windows 一键启动

如果本机已准备好 Python 虚拟环境、Node.js 和 MySQL，可运行：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

脚本默认启动后端 `8000` 端口和前端 `5173` 端口，并使用 `127.0.0.1:3307` 上的 MySQL 数据库 `wms`。详细说明见 [STARTUP.md](STARTUP.md)。

## 测试

后端测试脚本位于项目根目录，可在后端环境配置完成后运行：

```powershell
python test_reports.py
python test_stats.py
```

前端端到端测试：

```powershell
cd frontend
npx playwright test
```

## 默认演示账号

执行 `backend/rebuild_data.py` 后会创建演示管理员账号：

- 用户名：`admin`
- 密码：`123456`

正式部署时请立即修改默认密码，并通过环境变量配置 Django 密钥、数据库账号和跨域策略。

## 相关文档

- [系统架构](docs/architecture.md)
- [业务说明](docs/index.md)
- [API 接口文档](docs/api.md)
- [基础数据设计](docs/base_data.md)
- [入库管理](docs/inbound.md)
- [出库管理](docs/outbound.md)
- [库存管理](docs/inventory.md)
- [报表看板](docs/reports_dashboard.md)

## 课题说明

本项目用于毕业设计的系统分析、数据库设计、接口开发、前端实现和测试验证。项目中的示例数据仅用于学习和演示，不包含真实企业业务数据。

