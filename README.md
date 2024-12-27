# Surge Configuration Guide

## Installation Steps

### 1. Generate Proxy Groups

Use `diy.py` script to generate proxy group configuration:

```bash
python3 "./diy.py" '/Users/{YOUR_USERNAME}/Library/Application Support/Surge/Profiles/{YOUR_CONFIG}.conf'
```

> Note: Replace `{YOUR_USERNAME}` and `{YOUR_CONFIG}` with your actual username and configuration filename.

### 2. Add Rule Sets

Add the following rule sets to the `[Rule]` section of your Surge configuration file:

```text
# AI Services
RULE-SET,https://raw.githubusercontent.com/lin-youxiang/funnysurge/refs/heads/main/rules/AI.txt,AI

# Direct Access
RULE-SET,https://raw.githubusercontent.com/lin-youxiang/funnysurge/refs/heads/main/rules/DIRECT.txt,DIRECT

# Proxy Rules
DOMAIN-KEYWORD,githubusercontent,Proxy
RULE-SET,https://raw.githubusercontent.com/lin-youxiang/funnysurge/refs/heads/main/rules/PROXY.txt,Proxy

# Ad Blocking
RULE-SET,https://raw.githubusercontent.com/lin-youxiang/funnysurge/refs/heads/main/rules/REJECT.txt,REJECT
```

## Rule Set Description

- `AI`: Dedicated routing rules for AI-related services
- `DIRECT`: Direct connection rules for domestic websites
- `Proxy`: Proxy rules for foreign websites requiring VPN access
- `REJECT`: Rules for blocking ads and trackers

## Features

- Automated proxy group generation
- Predefined rule sets for different scenarios
- Easy-to-maintain configuration structure
- Regular updates for rule sets

## Requirements

- Python 3.x
- Surge for macOS
- Valid Surge subscription

## Project Structure

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped with the rules
- Special thanks to the Surge community