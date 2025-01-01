# Surge 配置指南

[English](README.md) | 简体中文

## 安装步骤

### 1. 生成代理组

使用 `diy.py` 脚本生成代理组配置：

```bash
python3 "./diy.py" '/Users/{你的用户名}/Library/Application Support/Surge/Profiles/{你的配置文件名}.conf'
```

> 注意：请将 `{你的用户名}` 和 `{你的配置文件名}` 替换为你的实际用户名和配置文件名。

### 2. 添加规则集

将以下规则集添加到你的 Surge 配置文件的 `[Rule]` 部分：

```text
# AI 服务
RULE-SET,https://raw.githubusercontent.com/lin-youxiang/funnysurge/refs/heads/main/rules/AI.txt,AI

# 直接访问
RULE-SET,SYSTEM,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/private.txt,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/icloud.txt,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/apple.txt,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/google.txt,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/direct.txt,DIRECT
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/cncidr.txt,DIRECT
RULE-SET,LAN,DIRECT

# 代理规则
DOMAIN-KEYWORD,githubusercontent,Proxy
DOMAIN-KEYWORD,googleadservices,Proxy
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/proxy.txt,Proxy
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/telegramcidr.txt,Proxy

# 广告拦截
RULE-SET,https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset/reject.txt,REJECT
```

## 规则集说明

- `AI`：AI 相关服务的专用路由规则
- `DIRECT`：国内网站直连规则
- `Proxy`：需要 VPN 访问的国外网站代理规则
- `REJECT`：广告和追踪器拦截规则

## 功能特点

- 自动生成代理组
- 预定义不同场景的规则集
- 易于维护的配置结构
- 规则集定期更新

## 系统要求

- Python 3.x
- Surge for macOS
- 有效的 Surge 订阅

## 项目结构

```
.
├── README.md
├── diy.py
└── rules/
    ├── AI.txt
    ├── DIRECT.txt
    ├── PROXY.txt
    └── REJECT.txt
```

## 参与贡献

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/很棒的功能`)
3. 提交你的更改 (`git commit -m '添加一些很棒的功能'`)
4. 推送到分支 (`git push origin feature/很棒的功能`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢所有为规则做出贡献的贡献者
- 特别感谢 Surge 社区