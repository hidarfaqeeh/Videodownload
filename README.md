# 🎬 Telegram Video Downloader Bot

بوت تليجرام متطور لتحميل مقاطع الفيديو من منصات التواصل الاجتماعي المختلفة مع واجهة عربية تفاعلية.

## ✨ المميزات

- 🌐 **دعم منصات متعددة**: YouTube, Twitter, Instagram, Facebook, TikTok, Snapchat
- 📋 **تحميل قوائم التشغيل**: اختيار فيديوهات محددة من قوائم YouTube
- 🎵 **تحويل إلى MP3**: استخراج الصوت من أي فيديو
- 📊 **نظام إحصائيات**: تتبع التحميلات وترتيب المستخدمين
- 🖼️ **معاينة مصغرة**: عرض الصور المصغرة قبل التحميل
- 🎯 **جودات متعددة**: من 360p إلى 4K
- 🔄 **تقدم متحرك**: رسائل تقدم مفصلة أثناء التحميل
- 🇸🇦 **واجهة عربية**: تصميم باللغة العربية مع الرموز التعبيرية

## 🚀 التنصيب السريع على Northflank

### 1. رفع الكود
```bash
git clone <your-repo-url>
cd telegram-video-downloader-bot
```

### 2. إعداد المتغيرات البيئية
قم بتعيين متغير البيئة التالي في Northflank:
- `BOT_TOKEN`: رمز البوت من @BotFather على تليجرام

#### (اختياري) المصادقة باستخدام الكوكيز في حال فشل التحميل أو تطلب تسجيل دخول
فعّل استخدام الكوكيز لجميع المنصات عبر متغيرات البيئة التالية. يتم استخدام الكوكيز تلقائياً فقط عند فشل المحاولة الأولى أو طلب تسجيل الدخول (يمكن تعديل هذا السلوك):

- `COOKIES_ENABLED` = `true` لتفعيل الميزة
- اختر إحدى طرق تزويد الكوكيز (الأولوية: ملف > Base64 > قيمة نصية):
  - `COOKIES_FILE_PATH` مسار ملف بصيغة Netscape cookies.txt داخل الحاوية (مثال: `/app/cookies.txt`)
  - `COOKIES_B64` محتوى ملف cookies.txt مشفر Base64 (سيتم حفظه تلقائياً في `/tmp/ytdlp_cookies_env.txt`)
  - `COOKIES_RAW` سلسلة ترويسة Cookie كاملة (مثال: `name=value; name2=value2`)
- `COOKIES_APPLY_ON_FAILURE_ONLY` = `true` (افتراضي) لاستخدام الكوكيز فقط عند فشل المحاولة الأولى، أو `false` لاستخدامها دائماً

أمثلة إعداد:

```bash
# استخدام ملف كوكيز جاهز داخل الحاوية
COOKIES_ENABLED=true
COOKIES_FILE_PATH=/app/cookies.txt
COOKIES_APPLY_ON_FAILURE_ONLY=true
```

```bash
# تمرير الكوكيز عبر Base64 (مثالي للنشر بدون ملفات إضافية)
COOKIES_ENABLED=true
COOKIES_B64=PASTE_BASE64_CONTENT_HERE
```

```bash
# تمرير ترويسة Cookie مباشرة
COOKIES_ENABLED=true
COOKIES_RAW="name=value; name2=value2"
```

ملاحظات:
- تنسيق الملف يجب أن يكون Netscape cookies.txt القياسي (كما يصدره المتصفح عبر إضافة cookies.txt أو عبر yt-dlp).
- في منصات مثل Northflank/Heroku/Railway يمكنك ضبط هذه المتغيرات من لوحة التحكم.
- لا تضع الكوكيز في المستودع. استخدم متغيرات البيئة فقط.

### 3. النشر التلقائي
1. اربط مستودع GitHub/GitLab بـ Northflank
2. اختر Dockerfile للبناء
3. حدد المتغيرات البيئية
4. انقر على Deploy

## 📁 هيكل المشروع

```
├── bot.py                 # الملف الرئيسي للبوت
├── downloader.py          # وحدة تحميل الفيديوهات
├── config.py             # إعدادات البوت
├── stats.py              # نظام الإحصائيات
├── user_stats.py         # إحصائيات المستخدمين
├── utils.py              # وظائف مساعدة
├── animated_responses.py  # الردود المتحركة
├── Dockerfile            # ملف Docker
├── docker-compose.yml    # إعداد Docker Compose
├── northflank.json      # إعداد Northflank
└── pyproject.toml       # تبعيات Python
```

## 🔧 متطلبات النظام

- Python 3.11+
- FFmpeg (للتحويل الصوتي)
- yt-dlp (لتحميل الفيديوهات)
- python-telegram-bot (للتفاعل مع تليجرام)

## 🌟 كيفية الاستخدام

1. ابدأ المحادثة مع البوت: `/start`
2. أرسل رابط فيديو من أي منصة مدعومة
3. اختر الجودة المطلوبة من القائمة
4. احصل على الفيديو أو الصوت فوراً!

### قوائم التشغيل
- أرسل رابط قائمة تشغيل YouTube
- اختر "اختيار فيديوهات محددة"
- انقر على الفيديوهات المطلوبة
- حمل كل فيديو بالجودة المطلوبة

## 📊 الإحصائيات

البوت يتتبع:
- إجمالي التحميلات لكل مستخدم
- المنصات الأكثر استخداماً
- ترتيب المستخدمين الأكثر نشاطاً
- إحصائيات يومية وأسبوعية

## 🔒 الأمان والخصوصية

- لا يتم حفظ الفيديوهات على الخادم
- حذف تلقائي للملفات المؤقتة
- تشفير البيانات الحساسة
- عدم تتبع المحتوى الشخصي

## 🛠️ التطوير المحلي

```bash
# استنساخ المشروع
git clone <repo-url>
cd telegram-video-downloader-bot

# تثبيت التبعيات
pip install -e .

# تعيين متغير البوت
export BOT_TOKEN="your_bot_token_here"

# تشغيل البوت
python bot.py
```

## 🚀 النشر على منصات أخرى

### Heroku
```bash
heroku create your-bot-name
heroku config:set BOT_TOKEN=your_token
git push heroku main
```

### Railway
```bash
railway login
railway new
railway add
railway up
```

### DigitalOcean Apps
استخدم `docker-compose.yml` للنشر المباشر.

## 📝 التحديثات المستقبلية

- [ ] دعم المزيد من المنصات
- [ ] تحميل جماعي للقوائم
- [ ] جدولة التحميلات
- [ ] ضغط الفيديوهات
- [ ] إشعارات التحديث

## 🤝 المساهمة

نرحب بالمساهمات! يرجى إنشاء Issue أو Pull Request.

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT.

## 📞 التواصل

للدعم التقني: @docamir
قناة البوت: @yedevlepver

---

**تم التطوير بواسطة د. حيدر** 👨‍⚕️💻