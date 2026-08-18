# WMS 系统接口文档

## 1. 文档说明

本文档基于当前 WMS 系统后端实现整理，适用于前端联调、接口测试和后续维护。

- 后端框架：Django + Django REST Framework + SimpleJWT
- 前端请求基准路径：`/api`
- 默认本地服务地址：`http://127.0.0.1:8000`
- 完整接口前缀：`http://127.0.0.1:8000/api`
- 数据格式：`application/json; charset=utf-8`
- 时间时区：`Asia/Shanghai`
- 认证方式：JWT Bearer Token

除登录接口外，业务接口均需要在请求头中携带登录后返回的访问令牌。

```http
Authorization: Bearer <token>
Content-Type: application/json
```

## 2. 通用规范

### 2.1 通用响应结构

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败响应：

```json
{
  "code": 400,
  "message": "参数错误"
}
```

说明：

- 当前后端多数业务错误通过响应体 `code` 表示，HTTP 状态码通常仍为 `200`。
- 前端应以响应体 `code === 200` 判断业务成功。
- `code=401` 表示未登录、Token 缺失或 Token 失效。

### 2.2 通用分页参数

适用于列表查询接口。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | number | 否 | `1` | 当前页码，从 1 开始 |
| `pageSize` | number | 否 | `10` | 每页条数，最大 200 |
| `keyword` | string | 否 | - | 关键词查询，支持的字段由接口决定 |

分页响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],
    "total": 0,
    "page": 1,
    "pageSize": 10
  }
}
```

### 2.3 通用删除参数

删除接口统一使用 JSON 请求体传递主键。

```json
{
  "id": 1
}
```

### 2.4 单据状态

入库单状态：

| 状态 | 说明 |
| :--- | :--- |
| `草稿` | 单据新建，可编辑 |
| `待审核` | 已提交，等待审核 |
| `已审核` | 审核通过，可执行收货 |
| `部分收货` | 部分明细已收货 |
| `已收货` | 收货完成，可执行上架 |
| `部分上架` | 部分明细已上架 |
| `已完成` | 入库流程完成 |
| `已驳回` | 审核驳回 |
| `已取消` | 单据取消 |

出库单状态：

| 状态 | 说明 |
| :--- | :--- |
| `草稿` | 单据新建，可编辑 |
| `待审核` | 已提交，等待审核 |
| `已审核` | 审核通过，并锁定库存 |
| `拣货中` | 已开始拣货 |
| `已发货` | 发货状态，当前实现发货后会自动置为 `已完成` |
| `已完成` | 出库流程完成 |
| `已驳回` | 审核驳回 |
| `已取消` | 单据取消 |

## 3. 认证接口

### 3.1 登录

```http
POST /api/auth/login
```

请求参数：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `username` | string | 是 | 登录账号 |
| `password` | string | 是 | 登录密码 |

请求示例：

```json
{
  "username": "root",
  "password": "123456"
}
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "jwt-access-token",
    "user": {
      "id": 1,
      "username": "root",
      "role": "admin",
      "name": "超级管理员",
      "avatar": "https://example.com/avatar.png"
    }
  }
}
```

### 3.2 登出

```http
POST /api/auth/logout
```

说明：JWT 为无状态认证，后端不保存会话。前端调用成功后清理本地 Token。

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

### 3.3 获取当前用户信息

```http
GET /api/auth/profile
```

响应字段：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | number | 用户 ID |
| `username` | string | 用户名 |
| `role` | string | 角色 |
| `name` | string | 显示名称 |
| `avatar` | string | 头像地址 |

## 4. 工作台接口

### 4.1 工作台统计

```http
GET /api/dashboard/stats
```

响应字段：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `inbound_today` | number | 今日入库商品数量 |
| `outbound_today` | number | 今日出库商品数量 |
| `sku_count` | number | 启用商品数 |
| `trend_7d` | array | 近 7 天入库/出库趋势 |
| `inbound_tasks` | array | 待处理入库任务 |
| `picking_tasks` | array | 待处理出库拣货任务 |

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "inbound_today": 120,
    "outbound_today": 85,
    "sku_count": 7,
    "trend_7d": [
      {
        "date": "2026-07-01",
        "inbound": 10,
        "outbound": 8
      }
    ],
    "inbound_tasks": [
      {
        "id": "IN-20260707-ABC123",
        "supplier": "全球科技电子有限公司",
        "status": "已审核"
      }
    ],
    "picking_tasks": [
      {
        "id": "OUT-20260707-DEF456",
        "customer": "电商平台B",
        "status": "已审核"
      }
    ]
  }
}
```

### 4.2 库存分布图

```http
GET /api/dashboard/inventory-pie
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `warehouse_code` | string | 否 | 仓库编码，传入后按仓库过滤 |
| `product_sku` | string | 否 | 商品 SKU，传入后返回该 SKU 在各仓库的分布 |

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "name": "无线人体工学鼠标",
      "value": 120
    }
  ]
}
```

## 5. 基础资料接口

### 5.1 商品管理

```http
GET    /api/products
POST   /api/products
PUT    /api/products
PATCH  /api/products
DELETE /api/products
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `keyword` | string | 否 | 按 `sku_code`、`spu_name` 模糊查询 |

新增/更新字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 商品 ID |
| `sku_code` | string | 新增必填 | SKU 编码，唯一 |
| `spu_name` | string | 新增必填 | 商品名称 |
| `category` | string | 否 | 商品分类 |
| `unit` | string | 否 | 单位 |
| `safety_stock` | number | 否 | 安全库存，默认 0 |
| `barcode` | string | 否 | 条码 |
| `is_active` | boolean | 否 | 是否启用，默认 true |

新增示例：

```json
{
  "sku_code": "ELEC-001",
  "spu_name": "无线人体工学鼠标",
  "category": "电子产品",
  "unit": "个",
  "safety_stock": 50,
  "barcode": "6900000000001",
  "is_active": true
}
```

列表响应单项：

```json
{
  "id": 1,
  "sku_code": "ELEC-001",
  "spu_name": "无线人体工学鼠标",
  "category": "电子产品",
  "unit": "个",
  "safety_stock": 50,
  "barcode": "6900000000001",
  "is_active": true,
  "created_at": "2026-07-07T10:00:00+08:00",
  "updated_at": "2026-07-07T10:00:00+08:00"
}
```

### 5.2 仓库管理

```http
GET    /api/warehouses
POST   /api/warehouses
PUT    /api/warehouses
PATCH  /api/warehouses
DELETE /api/warehouses
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 按 `name`、`code` 模糊查询 |

字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 仓库 ID |
| `name` | string | 是 | 仓库名称 |
| `code` | string | 是 | 仓库编码，唯一 |
| `address` | string | 否 | 地址 |
| `contact` | string | 否 | 联系人 |
| `phone` | string | 否 | 联系电话 |
| `is_active` | boolean | 否 | 是否启用 |

### 5.3 供应商管理

```http
GET    /api/suppliers
POST   /api/suppliers
PUT    /api/suppliers
PATCH  /api/suppliers
DELETE /api/suppliers
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 按 `name`、`contact`、`phone` 模糊查询 |

字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 供应商 ID |
| `name` | string | 是 | 供应商名称 |
| `contact` | string | 否 | 联系人 |
| `phone` | string | 否 | 联系电话 |
| `rating` | number | 否 | 评级 |
| `is_active` | boolean | 否 | 是否启用 |

### 5.4 客户管理

```http
GET    /api/customers
POST   /api/customers
PUT    /api/customers
PATCH  /api/customers
DELETE /api/customers
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 按 `name`、`contact`、`phone` 模糊查询 |

字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 客户 ID |
| `name` | string | 是 | 客户名称 |
| `contact` | string | 否 | 联系人 |
| `phone` | string | 否 | 联系电话 |
| `address` | string | 否 | 地址 |
| `credit_limit` | number | 否 | 信用额度 |

## 6. 入库接口

### 6.1 查询入库单列表

```http
GET /api/inbound/orders
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `keyword` | string | 否 | 按 `order_no`、`supplier_name` 模糊查询 |
| `status` | string | 否 | 按入库状态精确过滤 |

响应单项：

```json
{
  "id": 1,
  "order_no": "IN-20260707-ABC123",
  "status": "草稿",
  "planned_date": "2026-07-08",
  "warehouse_code": "WH-SH-01",
  "remark": "计划入库",
  "reject_reason": null,
  "supplier_name": "全球科技电子有限公司",
  "items": [
    {
      "id": 10,
      "product_sku": "ELEC-001",
      "quantity": 100,
      "received_qty": 0,
      "putaway_qty": 0,
      "location_code": null,
      "status": "草稿"
    }
  ]
}
```

### 6.2 创建入库单

```http
POST /api/inbound/orders
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `supplier_name` | string | 否 | 供应商名称 |
| `warehouse_code` | string | 是 | 入库仓库编码 |
| `planned_date` | string | 否 | 计划日期，格式 `YYYY-MM-DD` |
| `status` | string | 否 | 默认 `草稿` |
| `remark` | string | 否 | 备注 |
| `items` | array | 是 | 入库明细，不能为空 |

明细字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `product_sku` | string | 是 | 商品 SKU |
| `quantity` | number | 是 | 计划入库数量，必须大于 0 |
| `location_code` | string | 否 | 期望库位 |

请求示例：

```json
{
  "supplier_name": "全球科技电子有限公司",
  "warehouse_code": "WH-SH-01",
  "planned_date": "2026-07-08",
  "remark": "新品到货",
  "items": [
    {
      "product_sku": "ELEC-001",
      "quantity": 100
    }
  ]
}
```

业务规则：

- 单号由后端自动生成，格式为 `IN-YYYYMMDD-随机码`。
- 每个商品在单仓库总容量上限为 1000 件。
- 明细数量必须为正整数。

### 6.3 更新入库单/执行入库动作

```http
PUT /api/inbound/orders
```

通用字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 是 | 入库单 ID |
| `action` | string | 否 | 业务动作 |
| `status` | string | 否 | 目标状态，通常由 `action` 推导 |
| `supplier_name` | string | 否 | 供应商名称 |
| `warehouse_code` | string | 否 | 仓库编码 |
| `planned_date` | string | 否 | 计划日期 |
| `remark` | string | 否 | 备注 |
| `items` | array | 否 | 明细，非收货/上架动作时可替换明细 |

支持动作：

| `action` | 状态变化 | 说明 |
| :--- | :--- | :--- |
| `submit` | `草稿/已驳回` -> `待审核` | 提交审核 |
| `approve` | `待审核` -> `已审核` | 审核通过 |
| `reject` | `待审核` -> `已驳回` | 审核驳回，需传 `reject_reason` |
| `cancel` | 允许状态 -> `已取消` | 取消单据 |
| `receive` | `已审核/部分收货` -> `已收货/部分收货` | 收货确认 |
| `putaway` | `已收货/部分上架` -> `已完成/部分上架` | 上架入库 |

提交审核示例：

```json
{
  "id": 1,
  "action": "submit"
}
```

驳回示例：

```json
{
  "id": 1,
  "action": "reject",
  "reject_reason": "数量与采购计划不一致"
}
```

收货请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `receive_items` | array | `action=receive` 必填 | 收货明细 |

`receive_items` 明细：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 是 | 入库单明细 ID |
| `received_qty` | number | 是 | 实收数量，不能小于 0，不能超过计划数量 |
| `completion_status` | string | 否 | `completed` 或 `partial` |
| `reason` | string | 否 | 差异原因 |

收货示例：

```json
{
  "id": 1,
  "action": "receive",
  "receive_items": [
    {
      "id": 10,
      "received_qty": 80,
      "completion_status": "partial",
      "reason": "供应商短发"
    }
  ]
}
```

上架请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `putaway_items` | array | `action=putaway` 必填 | 上架明细 |

`putaway_items` 明细：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 是 | 入库单明细 ID |
| `putaway_qty` | number | 是 | 累计上架数量，不能小于 0，不能超过实收数量，不能回退 |
| `location_code` | string | 否 | 上架库位 |
| `completion_status` | string | 否 | `completed` 或 `partial` |
| `reason` | string | 否 | 差异原因 |

上架示例：

```json
{
  "id": 1,
  "action": "putaway",
  "putaway_items": [
    {
      "id": 10,
      "putaway_qty": 80,
      "location_code": "A-01-01",
      "completion_status": "completed"
    }
  ]
}
```

上架业务规则：

- 单库位容量上限为 100 件。
- 商品在单仓库会按专属库位自动分配，最多 10 个库位，总容量 1000 件。
- 当目标库位已有其他商品且数量大于 0 时，不允许混放。

### 6.4 删除入库单

```http
DELETE /api/inbound/orders
```

请求示例：

```json
{
  "id": 1
}
```

### 6.5 入库上架预览

```http
GET /api/inbound/orders?action=putaway_preview
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `action` | string | 是 | 固定为 `putaway_preview` |
| `warehouse_code` | string | 是 | 仓库编码 |
| `product_sku` | string | 是 | 商品 SKU |
| `quantity` | number | 是 | 待上架数量 |
| `location_code` | string | 否 | 期望库位 |

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allocations": [
      {
        "location_code": "A-01-01",
        "quantity": 80
      }
    ]
  }
}
```

### 6.6 批量入库上架预览

```http
GET /api/inbound/orders?action=putaway_preview_batch
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `action` | string | 是 | 固定为 `putaway_preview_batch` |
| `items` | string | 是 | JSON 字符串，内容为明细数组 |

`items` 示例：

```json
[
  {
    "warehouse_code": "WH-SH-01",
    "product_sku": "ELEC-001",
    "quantity": 80,
    "location_code": "A-01-01"
  }
]
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "allocations": [
      {
        "product_sku": "ELEC-001",
        "location_code": "A-01-01",
        "quantity": 80
      }
    ]
  }
}
```

## 7. 出库接口

### 7.1 查询出库单列表

```http
GET /api/outbound/orders
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `keyword` | string | 否 | 按 `order_no`、`customer_name` 模糊查询 |
| `status` | string | 否 | 按出库状态精确过滤 |

响应单项：

```json
{
  "id": 1,
  "order_no": "OUT-20260707-ABC123",
  "status": "草稿",
  "planned_date": "2026-07-08",
  "warehouse_code": "WH-SH-01",
  "remark": "计划出库",
  "reject_reason": null,
  "customer_name": "电商平台B",
  "items": [
    {
      "id": 20,
      "product_sku": "ELEC-001",
      "quantity": 10
    }
  ]
}
```

### 7.2 创建出库单

```http
POST /api/outbound/orders
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `customer_name` | string | 否 | 客户名称 |
| `warehouse_code` | string | 是 | 出库仓库编码 |
| `planned_date` | string | 否 | 计划日期，格式 `YYYY-MM-DD` |
| `status` | string | 否 | 默认 `草稿` |
| `remark` | string | 否 | 备注 |
| `items` | array | 是 | 出库明细，不能为空 |

明细字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `product_sku` | string | 是 | 商品 SKU |
| `quantity` | number | 是 | 出库数量，必须大于 0 |

请求示例：

```json
{
  "customer_name": "电商平台B",
  "warehouse_code": "WH-SH-01",
  "planned_date": "2026-07-08",
  "remark": "客户订单出库",
  "items": [
    {
      "product_sku": "ELEC-001",
      "quantity": 10
    }
  ]
}
```

业务规则：

- 单号由后端自动生成，格式为 `OUT-YYYYMMDD-随机码`。
- 出库单审核通过时会锁定库存。
- 发货时扣减库存，并释放对应锁定数量。

### 7.3 更新出库单/执行出库动作

```http
PUT /api/outbound/orders
```

通用字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 是 | 出库单 ID |
| `action` | string | 否 | 业务动作 |
| `status` | string | 否 | 目标状态 |
| `customer_name` | string | 否 | 客户名称 |
| `warehouse_code` | string | 否 | 仓库编码 |
| `planned_date` | string | 否 | 计划日期 |
| `remark` | string | 否 | 备注 |
| `items` | array | 否 | 出库明细 |

支持动作：

| `action` | 状态变化 | 说明 |
| :--- | :--- | :--- |
| `submit` | `草稿/已驳回` -> `待审核` | 提交审核 |
| `approve` | `待审核` -> `已审核` | 审核通过并锁定库存 |
| `reject` | `待审核` -> `已驳回` | 审核驳回，需传 `reject_reason` |
| `cancel` | 允许状态 -> `已取消` | 取消单据，必要时释放锁定库存 |

说明：前端拣货和发货动作通过传入 `status` 实现。

开始拣货示例：

```json
{
  "id": 1,
  "action": "start_pick",
  "status": "拣货中"
}
```

发货示例：

```json
{
  "id": 1,
  "action": "ship",
  "status": "已发货"
}
```

注意：当前后端没有单独识别 `start_pick`、`ship` 的动作名称，而是根据 `status` 执行状态流转和库存处理。

### 7.4 删除出库单

```http
DELETE /api/outbound/orders
```

请求示例：

```json
{
  "id": 1
}
```

## 8. 库存接口

### 8.1 库存查询

```http
GET /api/inventory/items
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `product_sku` | string | 否 | SKU 模糊查询 |
| `warehouse_code` | string | 否 | 仓库编码模糊查询 |
| `location_code` | string | 否 | 库位编码模糊查询 |

响应单项：

```json
{
  "id": 1,
  "product_sku": "ELEC-001",
  "warehouse_code": "WH-SH-01",
  "location_code": "A-01-01",
  "quantity": 100,
  "locked_qty": 10,
  "batch_no": "BATCH-20260707-001",
  "available_qty": 90,
  "safety_stock": 50
}
```

字段说明：

| 字段 | 说明 |
| :--- | :--- |
| `quantity` | 当前账面库存 |
| `locked_qty` | 已被出库单锁定的库存 |
| `available_qty` | 可用库存，等于 `quantity - locked_qty` |
| `safety_stock` | 商品安全库存 |

### 8.2 库存预警

```http
GET /api/inventory/warning
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `product_sku` | string | 否 | SKU 模糊查询 |
| `warehouse_code` | string | 否 | 仓库编码模糊查询 |

响应单项：

```json
{
  "product_sku": "ELEC-001",
  "warehouse_code": "WH-SH-01",
  "quantity": 40,
  "locked_qty": 5,
  "available_qty": 35,
  "safety_stock": 50,
  "shortage": 15
}
```

预警规则：

- 以商品和仓库维度汇总库存。
- 当 `available_qty < safety_stock` 时进入预警列表。
- `shortage = safety_stock - available_qty`。

### 8.3 盘点记录查询

```http
GET /api/inventory/stocktaking
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `product_sku` | string | 否 | SKU 模糊查询 |
| `warehouse_code` | string | 否 | 仓库编码模糊查询 |

响应单项：

```json
{
  "id": 1,
  "product_sku": "ELEC-001",
  "warehouse_code": "WH-SH-01",
  "location_code": "A-01-01",
  "quantity_before": 100,
  "quantity_after": 98,
  "diff_qty": -2,
  "reason": "实物少件",
  "created_at": "2026-07-07T10:00:00+08:00"
}
```

### 8.4 提交库存盘点

```http
POST /api/inventory/stocktaking
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `product_sku` | string | 是 | 商品 SKU |
| `warehouse_code` | string | 是 | 仓库编码 |
| `location_code` | string | 是 | 库位编码 |
| `actual_qty` | number | 是 | 实盘数量 |
| `reason` | string | 否 | 差异原因 |

请求示例：

```json
{
  "product_sku": "ELEC-001",
  "warehouse_code": "WH-SH-01",
  "location_code": "A-01-01",
  "actual_qty": 98,
  "reason": "实物少件"
}
```

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "diff": -2
  }
}
```

业务规则：

- 若库存记录存在，则按实盘数量调整 `quantity`。
- 若库存记录不存在，则创建库存记录和盘点记录。
- `actual_qty` 不能小于当前锁定库存。
- 单库位容量上限为 100 件。

### 8.5 调拨库存查询

```http
GET /api/inventory/transfer
```

说明：返回库存列表，字段与 `/api/inventory/items` 基本一致，用于调拨页面选择可调库存。

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `product_sku` | string | 否 | SKU 模糊查询 |
| `warehouse_code` | string | 否 | 仓库编码模糊查询 |

### 8.6 提交库存调拨

```http
POST /api/inventory/transfer
```

请求字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `product_sku` | string | 是 | 商品 SKU |
| `from_wh` | string | 是 | 调出仓库 |
| `from_location` | string | 否 | 调出库位；传入后从指定库位扣减 |
| `to_wh` | string | 是 | 调入仓库 |
| `to_location` | string | 否 | 调入库位；不传时默认为 `调拨入库区` |
| `quantity` | number | 是 | 调拨数量，必须大于 0 |

请求示例：

```json
{
  "product_sku": "ELEC-001",
  "from_wh": "WH-SH-01",
  "from_location": "A-01-01",
  "to_wh": "WH-BJ-01",
  "to_location": "A-02-01",
  "quantity": 10
}
```

业务规则：

- 调出库位可用库存不足时拒绝调拨。
- 目标库位容量上限为 100 件。
- 调拨成功后写入系统日志和调拨记录。

## 9. 报表接口

### 9.1 报表看板

```http
GET /api/reports/dashboard
```

响应字段：

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `kpi.inbound_today` | number | 今日入库商品数量 |
| `kpi.outbound_today` | number | 今日出库商品数量 |
| `kpi.inventory_amount` | number | 当前库存总数量 |
| `kpi.sku_count` | number | 启用商品数 |
| `trend_7d` | array | 近 7 天趋势 |
| `top10` | array | 库存数量前 10 商品 |

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "kpi": {
      "inbound_today": 120,
      "outbound_today": 85,
      "inventory_amount": 1000,
      "sku_count": 7
    },
    "trend_7d": [
      {
        "date": "2026-07-01",
        "inbound": 10,
        "outbound": 8
      }
    ],
    "top10": [
      {
        "name": "无线人体工学鼠标",
        "qty": 200
      }
    ]
  }
}
```

### 9.2 日报表

```http
GET /api/reports/daily
```

说明：返回最近 30 天每日入库/出库商品数量。

响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "date": "2026-07-07",
        "inbound": 20,
        "outbound": 15
      }
    ],
    "total": 30
  }
}
```

## 10. 系统管理接口

### 10.1 用户管理

```http
GET    /api/system/users
POST   /api/system/users
PUT    /api/system/users
PATCH  /api/system/users
DELETE /api/system/users
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 按 `username`、`name`、`role` 模糊查询 |

字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 用户资料 ID |
| `username` | string | 是 | 用户名 |
| `role` | string | 是 | 角色 |
| `name` | string | 否 | 显示名称 |
| `avatar` | string | 否 | 头像地址 |

注意：该接口维护的是 WMS 用户资料表 `SystemUser`，不是 Django 认证用户密码表。登录账号仍依赖 Django `User`。

### 10.2 角色管理

```http
GET    /api/system/roles
POST   /api/system/roles
PUT    /api/system/roles
PATCH  /api/system/roles
DELETE /api/system/roles
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 按角色名称模糊查询 |

字段：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | number | 更新/删除必填 | 角色 ID |
| `name` | string | 是 | 角色名称，唯一 |

### 10.3 系统日志查询

```http
GET /api/system/logs
```

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页条数 |
| `operator` | string | 否 | 操作人模糊查询 |
| `action` | string | 否 | 操作类型模糊查询 |
| `detail` | string | 否 | 日志详情模糊查询 |

响应单项：

```json
{
  "id": 1,
  "operator": "root",
  "action": "入库单创建",
  "detail": "创建入库单 IN-20260707-ABC123，包含 1 个明细",
  "created_at": "2026-07-07T10:00:00+08:00"
}
```

## 11. 根路径健康检查

### 11.1 后端运行状态

```http
GET /
```

响应示例：

```json
{
  "code": 0,
  "message": "WMS backend is running",
  "apiBase": "/api/"
}
```

## 12. 常见错误码

| `code` | 含义 | 常见原因 |
| :--- | :--- | :--- |
| `200` | 成功 | 请求处理成功 |
| `400` | 请求参数错误 | 缺少必要参数、状态流转非法、库存不足、数量不合法 |
| `401` | 未认证 | 未传 Token、Token 无效或已过期 |
| `404` | 数据不存在 | 更新或删除时 ID 不存在 |
| `405` | 方法不允许 | 使用了接口不支持的 HTTP 方法 |
| `500` | 服务端错误 | 服务端内部异常 |

## 13. 调用示例

### 13.1 cURL 登录

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"root\",\"password\":\"123456\"}"
```

### 13.2 cURL 查询商品

```bash
curl -X GET "http://127.0.0.1:8000/api/products?page=1&pageSize=10" \
  -H "Authorization: Bearer <token>"
```

### 13.3 Axios 示例

```js
import request from '@/utils/request'

export function getProducts(params) {
  return request({
    url: '/products',
    method: 'get',
    params
  })
}
```

