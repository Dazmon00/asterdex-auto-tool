# AsterDex 对冲交易工具

这是一个基于 AsterDex 交易所的自动化对冲交易工具，通过同时在不同账户开立相反方向的仓位来获取资金费率收益。

## 功能特点

- 实时显示交易状态和账户信息
- 自动执行对冲交易策略
- 支持自定义交易参数
- 实时显示资金费率和盈亏情况
- 自动计算和显示交易统计信息
- 优雅的命令行界面，使用 rich 库实现

## 安装要求

- Python 3.7+
- 依赖包：
  ```
  requests
  rich
  ```

## 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/asterdex-auto-tool.git
   cd asterdex-auto-tool
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 config.json：
   ```json
   {
     "account1": {
       "api_key": "你的第一个账号API Key",
       "api_secret": "你的第一个账号API Secret"
     },
     "account2": {
       "api_key": "你的第二个账号API Key",
       "api_secret": "你的第二个账号API Secret"
     },
     "trading": {
       "symbol": "ETHUSDT",
       "position_side": "BOTH",
       "order_type": "MARKET",
       "wait_seconds": 300,
       "leverage": 10,
       "usdt_amount": 100
     }
   }
   ```

## 配置说明

在 `config.json` 中：

- `account1` 和 `account2`: 两个交易账号的 API 配置
- `trading` 部分：
  - `symbol`: 交易对（例如：ETHUSDT）
  - `position_side`: 持仓方向（BOTH）
  - `order_type`: 订单类型（MARKET）
  - `wait_seconds`: 持仓等待时间（秒）
  - `leverage`: 杠杆倍数
  - `usdt_amount`: 每次交易的 USDT 金额

## 使用方法

1. 确保已经正确配置 `config.json`

2. 运行程序：
   ```bash
   python hedge_trading.py
   ```

3. 程序会显示实时交易界面，包括：
   - 市场信息（价格、资金费率等）
   - 账户状态（持仓、盈亏等）
   - 交易统计（交易次数、总交易量等）

4. 按 Ctrl+C 可以安全退出程序，程序会自动清理所有持仓

## 界面说明

程序界面分为两个主要部分：

1. 市场信息面板：
   - 显示当前交易对、价格、资金费率
   - 显示交易统计信息
   - 显示账户余额和总盈亏

2. 账户状态面板：
   - 显示两个账户的持仓信息
   - 显示持仓方向、数量、开仓价格
   - 显示未实现盈亏、保证金和清算价格

## 注意事项

1. 请确保两个账户都有足够的保证金
2. 建议先用小资金测试
3. 请妥善保管 API 密钥
4. 程序会自动处理服务器时间同步
5. 建议在稳定的网络环境下运行

## 风险提示

- 加密货币交易具有高风险
- 请确保理解对冲交易策略的风险
- 建议在实盘交易前进行充分测试
- 本工具不构成投资建议

## 许可证

MIT License

# API Documentation for Aster Finance

[Aster Finance API Document](./aster-finance-api.md)

# Aster Finance API 文档

[Aster Finance API 文档](./aster-finance-api_CN.md)

