import { test, expect } from '@playwright/test';

test.describe('WMS 全流程自动化测试', () => {
  // 登录前置操作
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('.el-input__inner[type="text"]', 'admin');
    await page.fill('.el-input__inner[type="password"]', '123456');
    await page.click('.login-btn');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('入库流程测试', async ({ page }) => {
    // 1. 入库申请
    await page.click('div.el-sub-menu__title:has-text("入库管理")');
    await page.click('li.el-menu-item:has-text("入库申请")');
    await page.click('button:has-text("新增入库单")');
    
    // 填写表单
    // 等待下拉框加载数据
    await page.waitForTimeout(1000); 
    
    // 选择供应商
    await page.click('label:has-text("供应商") + div .el-select');
    await page.click('.el-select-dropdown__item:has-text("联想供应商")');
    
    // 选择仓库
    await page.click('label:has-text("入库仓库") + div .el-select');
    await page.click('.el-select-dropdown__item:has-text("上海一号库")');
    
    // 添加商品
    await page.click('button:has-text("+ 添加商品")');
    await page.click('.el-table__body .el-select');
    await page.click('.el-select-dropdown__item:has-text("测试商品")');
    
    // 保存
    await page.click('button:has-text("保存")');
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 提交
    await page.waitForTimeout(1000); // 等待列表刷新
    // 获取第一行数据的提交按钮
    await page.click('tr:first-child button:has-text("提交")');
    await expect(page.locator('.el-message--success')).toBeVisible();

    // 2. 入库审核
    await page.click('li.el-menu-item:has-text("入库审核")');
    await page.waitForTimeout(500);
    // 通过审核
    await page.click('tr:first-child button:has-text("通过")');
    await expect(page.locator('.el-message--success')).toBeVisible();

    // 3. 收货上架
    await page.click('li.el-menu-item:has-text("收货上架")');
    await page.waitForTimeout(500);
    
    // 收货
    await page.click('tr:first-child button:has-text("收货")');
    await page.click('button:has-text("确认收货")');
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 上架
    await page.waitForTimeout(500);
    await page.click('tr:first-child button:has-text("上架")');
    // 选择库位 (假设自动推荐或手动选择)
    // 这里简单起见，直接确认上架，依赖默认逻辑
    await page.click('button:has-text("确认上架")');
    await expect(page.locator('.el-message--success')).toBeVisible();
  });

  test('出库流程测试', async ({ page }) => {
    // 1. 出库申请
    await page.click('div.el-sub-menu__title:has-text("出库管理")');
    await page.click('li.el-menu-item:has-text("出库申请")');
    await page.click('button:has-text("新增出库单")');
    
    await page.waitForTimeout(1000);
    
    // 选择客户
    await page.click('label:has-text("客户") + div .el-select');
    await page.click('.el-select-dropdown__item:first-child'); // 选择第一个客户
    
    // 选择仓库 (必须选有货的)
    await page.click('label:has-text("出库仓库") + div .el-select');
    await page.click('.el-select-dropdown__item:has-text("上海一号库")');
    
    // 添加商品
    await page.click('button:has-text("+ 添加商品")');
    await page.click('.el-table__body .el-select');
    await page.click('.el-select-dropdown__item:first-child'); // 选择第一个可用商品
    
    // 保存
    await page.click('button:has-text("保存")');
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 提交
    await page.waitForTimeout(1000);
    await page.click('tr:first-child button:has-text("提交")');
    await expect(page.locator('.el-message--success')).toBeVisible();

    // 2. 出库审核
    await page.click('li.el-menu-item:has-text("出库审核")');
    await page.waitForTimeout(500);
    await page.click('tr:first-child button:has-text("通过")');
    await expect(page.locator('.el-message--success')).toBeVisible();

    // 3. 拣货发货
    await page.click('li.el-menu-item:has-text("拣货发货")');
    await page.waitForTimeout(500);
    
    // 开始拣货
    await page.click('tr:first-child button:has-text("开始拣货")');
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 发货
    await page.waitForTimeout(500);
    await page.click('tr:first-child button:has-text("发货")');
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 完成 (如果有)
    // await page.click('tr:first-child button:has-text("完成")');
  });
});
