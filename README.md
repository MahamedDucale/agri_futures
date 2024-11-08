<div align="center">
  <img src="agri_futures_logo.png" alt="AgriFutures Logo" width="100" height="100" style="margin-right: 20px"/>
  <h1>AgriFutures</h1>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Stellar](https://img.shields.io/badge/Stellar-Blockchain-blue)](https://www.stellar.org/)

## 🚀 Empowering Rural Women Farmers Through Financial Innovation

AgriFutures is a revolutionary micro-futures platform that empowers rural women farmers to protect themselves against crop price fluctuations. Using simple SMS technology, mobile money, and blockchain, we're making financial protection accessible to those who need it most.

### ✨ Key Features

- 📱 **SMS-Based Interface**: No smartphone required
- 💰 **Mobile Money Integration**: Easy payments via M-PESA and other local providers
- ⛓️ **Blockchain Security**: Powered by Stellar for transparent and secure contracts
- 🌍 **Multi-Language Support**: Available in Swahili, English, and more
- 📊 **Real-Time Pricing**: Live crop price updates and market data
- 🤝 **Fair Premiums**: Affordable price protection for small-scale farmers

## 🛠️ Quick Start

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/agrifutures.git
cd agrifutures
```

2. **Set Up Environment**

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**

```bash
cp .env.example .env
```

4. **Run the Application**

```bash
python manage.py runserver
python manage.py initdb
python manage.py create_stellar_account
```
