🎓 Akademik Yordamchi Bot
Production-ready Telegram bot for academic document generation with APA, Harvard, and Uzbek style templates.
📋 Features
✅ Document Types
📝 Referat (Essay)
📚 Kurs Ishi (Coursework)
📄 Maqola (Article)
🎯 Slide Presentation
✅ Styles
🎯 APA Style
🎯 Harvard Style
🎯 Uzbek Standard
✅ Payment
💳 Click.uz integration
💳 Payme integration
🎁 Free first document
💰 2,000 UZS / 0.17 USD for next documents
✅ Features
📄 Automatic PDF generation
🔗 QR code embedding
👤 User authentication
💾 Database storage
📊 Statistics
🚀 Quick Start
Prerequisites
Python 3.9+
Telegram Bot Token from @BotFather
Railway account (for deployment)
Local Development
Clone and install
Bash
Setup environment
Bash
Run locally
Bash
Railway Deployment
Push to GitHub
Bash
Connect to Railway
Go to railway.app
Create new project
Connect your GitHub repository
Set environment variables in Railway dashboard:
BOT_TOKEN
ADMIN_ID
PAYME_MERCHANT_ID
CLICK_SERVICE_ID
etc.
Deploy
Railway automatically deploys when you push to main
📁 Project Structure
Code
🔧 Configuration
Environment Variables (.env)
Code
💰 Pricing
Item
Price
First Document
🎁 FREE
Next Documents
2,000 UZS / 0.17 USD
🔐 Payment Integration
Click.uz
Service ID: Your Click service ID
Merchant ID: Your Click merchant ID
API Key: Your Click API key
Payme
Merchant ID: Your Payme merchant ID
API Key: Your Payme API key
📊 Bot Commands
Command
Description
/start
Start bot
/help
Get help
/admin
Admin panel
🤖 Bot Features Explained
Document Generation
User selects document type
Chooses formatting style
Enters title and content
Bot generates PDF with:
Proper formatting
QR code
Metadata
Payment Flow
First document is FREE
Next documents require payment
User selects payment gateway
Payment processed
Document generated
Database
SQLite for local development
PostgreSQL for production (Railway)
Stores users, documents, payments
🐛 Troubleshooting
Bot not responding
Check BOT_TOKEN is correct
Ensure bot.py is running
Check logs for errors
Payment not working
Verify Click/Payme credentials
Check test mode settings
Review payment logs
PDF not generating
Ensure reportlab is installed
Check documents folder permissions
Verify content is not too large
📝 Development
Running tests
Bash
Building documentation
Bash
🚀 Deployment Checklist
[ ] Get bot token from @BotFather
[ ] Get admin Telegram ID
[ ] Setup Payme merchant account
[ ] Setup Click.uz merchant account
[ ] Create GitHub repository
[ ] Setup Railway account
[ ] Configure environment variables
[ ] Test locally
[ ] Push to GitHub
[ ] Deploy to Railway
[ ] Verify bot is working
[ ] Monitor logs
📈 Monitoring
Logs
Check logs in Railway dashboard or locally:
Bash
Database
Check database:
Bash
🤝 Contributing
Contributions welcome! Please:
Fork repository
Create feature branch
Make changes
Submit pull request
📞 Support
Telegram Bot: @akadem_yordamchi_bot
Email: support@akadem.uz
GitHub Issues: [Link to issues]
📄 License
MIT License - see LICENSE file
🙏 Acknowledgments
aiogram for Telegram bot library
ReportLab for PDF generation
SQLAlchemy for database ORM
Made with ❤️ for students
Quick Links
Telegram Bot
GitHub Repository
Railway App
Last Updated: 2024
Version: 1.0.0
Status: ✅ Production Ready
