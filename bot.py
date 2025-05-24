#!/usr/bin/env python3
"""
Telegram Video Downloader Bot
Downloads videos from YouTube, Twitter, Instagram, Facebook, and TikTok
"""

import logging
import os
import tempfile
import asyncio
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction
from downloader import VideoDownloader
from utils import is_valid_url, format_file_size, cleanup_temp_files
from config import BOT_TOKEN, SUPPORTED_PLATFORMS, MAX_FILE_SIZE
from animated_responses import AnimatedResponses
from stats import BotStats

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramVideoBot:
    def __init__(self):
        self.downloader = VideoDownloader()
        self.temp_dir = tempfile.mkdtemp(prefix="telegram_bot_")
        self.stats = BotStats()
        logger.info(f"Temporary directory created: {self.temp_dir}")
        # Developer chat ID - سيتم الحصول عليه تلقائياً عند أول رسالة
        self.developer_chat_id = None

    async def forward_support_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> None:
        """Log support message and confirm to user"""
        user = update.effective_user
        user_name = user.first_name if user else "مستخدم"
        username = f" (@{user.username})" if user and user.username else ""
        user_id = user.id if user else "غير معروف"
        
        # تسجيل الرسالة في السجلات
        logger.info(f"📨 رسالة دعم من {user_name}{username} (ID: {user_id}): {message_text}")
        
        # رسالة تأكيد للمستخدم
        confirmation_message = f"""
✅ *تم استلام رسالتك بنجاح!*

📨 *رسالتك:* _{message_text[:80]}{'...' if len(message_text) > 80 else ''}_

🔔 *سيتم الرد عليك عبر:*
• قناة البوت: @yedevlepver
• المطور مباشرة: @docamir

📞 *للمساعدة الفورية:*
• انضم لقناة البوت للحصول على آخر التحديثات
• راسل المطور مباشرة في التلجرام

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 اضغط /start للعودة للقائمة الرئيسية
        """
        
        try:
            await update.message.reply_text(
                confirmation_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال تأكيد الرسالة: {e}")
            await update.message.reply_text(
                "✅ تم استلام رسالتك!\n"
                "📞 للمساعدة راسل: @docamir\n"
                "🔄 /start للعودة"
            )

    async def show_download_progress(self, message, file_type: str, url: str) -> None:
        """Show animated download progress with detailed information"""
        import random
        import time
        
        # Get estimated file size (simulated for demonstration)
        estimated_sizes = {
            "audio": random.randint(3, 8),  # 3-8 MB for audio
            "video": random.randint(15, 120)  # 15-120 MB for video
        }
        
        total_size_mb = estimated_sizes.get(file_type, 25)
        total_size_bytes = total_size_mb * 1024 * 1024
        
        # Progress animation frames
        progress_chars = ["▱▱▱▱▱▱▱▱▱▱", "▰▱▱▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱▱▱", 
                         "▰▰▰▰▱▱▱▱▱▱", "▰▰▰▰▰▱▱▱▱▱", "▰▰▰▰▰▰▱▱▱▱", "▰▰▰▰▰▰▰▱▱▱",
                         "▰▰▰▰▰▰▰▰▱▱", "▰▰▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰▰▰"]
        
        spinning_icons = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        start_time = time.time()
        
        # Phase 1: Initialization
        for i in range(3):
            icon = spinning_icons[i % len(spinning_icons)]
            await message.edit_text(
                f"{icon} **جاري البدء في التحميل...**\n\n"
                f"📋 **تحليل الرابط والحصول على المعلومات**\n"
                f"🔍 **البحث عن أفضل جودة متاحة**\n"
                f"⏱ **الوقت المقدر:** ~{total_size_mb//5 + 10} ثانية\n\n"
                f"💡 **شكراً لصبرك، جاري التحضير...**",
                parse_mode='Markdown'
            )
            await asyncio.sleep(0.8)
        
        # Phase 2: Download progress simulation
        for progress_step in range(len(progress_chars)):
            icon = spinning_icons[progress_step % len(spinning_icons)]
            percentage = (progress_step * 100) // (len(progress_chars) - 1)
            downloaded_mb = (total_size_mb * percentage) // 100
            elapsed_time = time.time() - start_time
            
            if percentage > 0:
                speed_mbps = downloaded_mb / max(elapsed_time, 0.1)
                remaining_mb = total_size_mb - downloaded_mb
                eta_seconds = remaining_mb / max(speed_mbps, 0.1) if speed_mbps > 0 else 0
            else:
                speed_mbps = 0
                eta_seconds = total_size_mb // 2  # rough estimate
            
            # Different messages for different file types
            if file_type == "audio":
                type_emoji = "🎵"
                type_text = "الملف الصوتي"
                process_text = "استخراج وتحويل الصوت"
            else:
                type_emoji = "📹"
                type_text = "الفيديو"
                process_text = "تحميل ومعالجة الفيديو"
            
            progress_message = (
                f"{icon} **{type_emoji} جاري تحميل {type_text}...**\n\n"
                f"📊 **التقدم:** {percentage}%\n"
                f"{progress_chars[progress_step]}\n\n"
                f"📁 **تم التحميل:** {downloaded_mb:.1f} MB من {total_size_mb} MB\n"
                f"⚡ **السرعة:** {speed_mbps:.1f} MB/s\n"
                f"⏱ **الوقت المتبقي:** {eta_seconds:.0f} ثانية\n\n"
                f"🔄 **{process_text}**\n"
                f"💫 **نقدر صبرك، قريباً سننتهي!**"
            )
            
            await message.edit_text(progress_message, parse_mode='Markdown')
            await asyncio.sleep(1.2)  # Slower for more realistic feel
        
        # Phase 3: Upload to Telegram
        upload_frames = [
            "📤 **التحميل مكتمل! جاري الرفع إلى تلجرام...**",
            "🚀 **معالجة الملف للرفع السريع...**", 
            "⚡ **تحسين جودة الرفع...**",
            "✨ **اللمسات الأخيرة، تقريباً انتهينا...**"
        ]
        
        for i, frame in enumerate(upload_frames):
            icon = spinning_icons[i % len(spinning_icons)]
            total_elapsed = time.time() - start_time
            
            await message.edit_text(
                f"{icon} {frame}\n\n"
                f"📊 **التقدم:** 100% ✅\n"
                f"📁 **حجم الملف:** {total_size_mb} MB\n"
                f"⏱ **وقت التحميل:** {total_elapsed:.1f} ثانية\n"
                f"🚀 **سرعة متوسطة:** {total_size_mb/total_elapsed:.1f} MB/s\n\n"
                f"🎯 **جاري الرفع إلى تلجرام...**",
                parse_mode='Markdown'
            )
            await asyncio.sleep(1.0)

    async def send_thank_you_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, url: str = None) -> None:
        """Send thank you message with enhanced options after successful download"""
        share_keyboard = []
        
        # Add audio download option if URL is available
        if url:
            share_keyboard.append([InlineKeyboardButton("🎵 تحميل كصوت MP3", callback_data=f"download_audio_from_video_{url}")])
        
        share_keyboard.extend([
            [InlineKeyboardButton("🚀 شارك البوت مع أصدقائك", url="https://t.me/share/url?url=https://t.me/your_bot_username&text=🎥 بوت تحميل الفيديوهات الأفضل! يدعم يوتيوب، تيك توك، انستقرام، تويتر وأكثر مجاناً 💯")],
            [InlineKeyboardButton("📢 انضم لقناة البوت", url="https://t.me/yedevlepver")],
            [InlineKeyboardButton("🔄 تحميل فيديو آخر", callback_data="back_to_main")]
        ])
        share_reply_markup = InlineKeyboardMarkup(share_keyboard)
        
        thank_you_message = (
            "✅ *تم التحميل بنجاح!* ✅\n\n"
            "🙏 *شكراً لاستخدامك بوتنا*\n\n"
            "💖 إذا أعجبك البوت، ساعدنا في النشر:\n"
            "🔗 شارك البوت مع أصدقائك\n"
            "⭐ انضم لقناتنا للتحديثات\n"
            "📝 أرسل لنا ملاحظاتك\n\n"
            "🎯 استمتع بالملف المحمل!"
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=thank_you_message,
            parse_mode='Markdown',
            reply_markup=share_reply_markup
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command with beautiful welcome interface"""
        user_name = update.effective_user.first_name if update.effective_user.first_name else "صديقي العزيز"
        
        # Beautiful welcome message with transparent theme
        welcome_message = (
            f"🎭 *أهلاً وسهلاً {user_name}!* 🎭\n\n"
            "🌟 *مرحباً بك في عالم التحميل السحري*\n\n"
            "🚀 *البوت الأقوى لتحميل الفيديوهات*\n"
            "من جميع المنصات الشهيرة بجودة عالية\n\n"
            "✨ *ما يميزنا:*\n"
            "🔥 سرعة البرق في التحميل\n"
            "🎯 جودات متعددة حتى 4K\n"
            "🎵 تحويل لـ MP3 بنقرة واحدة\n"
            "🌐 دعم 6 منصات رئيسية\n"
            "💎 مجاني تماماً بلا قيود\n\n"
            "📋 *استخدم الأزرار الشفافة أدناه للتنقل*"
        )
        
        # Create transparent-style main menu keyboard
        keyboard = [
            [
                InlineKeyboardButton("🔥 المميزات الحصرية", callback_data="features"),
                InlineKeyboardButton("📚 دليل الاستخدام", callback_data="help")
            ],
            [
                InlineKeyboardButton("📢 قناة البوت", url="https://t.me/yedevlepver"),
                InlineKeyboardButton("👨‍💻 المطور", callback_data="developer")
            ],
            [
                InlineKeyboardButton("💡 أمثلة للروابط", callback_data="examples"),
                InlineKeyboardButton("🆘 الدعم الفني", callback_data="support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send typing action for realistic feel
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(1)
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        platform_list = '\n'.join([f'• {platform}' for platform in SUPPORTED_PLATFORMS])
        help_message = (
            "🔹 *كيفية الاستخدام:*\n"
            "1. أرسل لي رابط فيديو\n"
            "2. اختر الجودة أو نوع الملف\n"
            "3. انتظر التحميل\n"
            "4. احصل على ملفك!\n\n"
            
            "🔹 *المنصات المدعومة:*\n"
            f"{platform_list}\n\n"
            
            "🔹 *خيارات التحميل:*\n"
            "📹 فيديو بجودات مختلفة (720p, 1080p, إلخ)\n"
            "🎵 صوت MP3 بجودة عالية (192kbps)\n"
            "🎵 صوت MP3 بجودة متوسطة (128kbps)\n\n"
            
            "🔹 *القيود:*\n"
            f"• الحد الأقصى لحجم الملف: {format_file_size(MAX_FILE_SIZE)}\n"
            "• بعض المحتوى الخاص قد لا يكون متاحاً\n\n"
            
            "🔹 *الأوامر:*\n"
            "/start - بدء البوت\n"
            "/help - عرض هذه الرسالة\n\n"
            
            "💡 *نصيحة:* فقط أرسل أي رابط فيديو وسأتولى الباقي!"
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            help_text = (
                "📚 *دليل استخدام البوت الشامل*\n\n"
                "🌟 *كيفية الاستخدام:*\n"
                "1️⃣ انسخ رابط فيديو من أي منصة\n"
                "2️⃣ الصق الرابط في المحادثة\n"
                "3️⃣ اختر الجودة المطلوبة\n"
                "4️⃣ احصل على الملف فوراً!\n\n"
                "🎯 *أنواع التحميل:*\n"
                "🔥 1080p - جودة عالية جداً\n"
                "⭐ 720p - جودة عالية\n"
                "✅ 480p - جودة عادية\n"
                "📱 360p - للموبايل\n"
                "🎵 MP3 - صوت فقط\n\n"
                "💡 *نصائح مهمة:*\n"
                "• الروابط القصيرة مدعومة\n"
                "• يمكن تحميل الصوت من أي فيديو\n"
                "• جميع الملفات آمنة ونظيفة\n"
                "🆘 /start للعودة للقائمة"
            )
            await query.message.edit_text(help_text, parse_mode='Markdown')
        elif query.data == "features":
            features_message = (
                "🔥 *المميزات الحصرية للبوت:*\n\n"
                "⚡ *سرعة فائقة:* تحميل فوري بدون انتظار\n"
                "🎯 *جودات متعددة:* من 480p إلى 4K\n"
                "🎵 *تحويل صوتي:* MP3 بجودة عالية ومتوسطة\n"
                "📊 *معلومات شاملة:* الحجم، المدة، الدقة\n"
                "🌐 *دعم واسع:* 6 منصات رئيسية\n"
                "🚀 *واجهة ذكية:* تفاعلية وسهلة\n"
                "🛡️ *آمان تام:* حماية البيانات\n"
                "🔄 *تحديث مستمر:* دعم أحدث التقنيات\n\n"
                "💎 *كل هذا مجاناً بلا قيود!*"
            )
            await query.message.edit_text(features_message, parse_mode='Markdown')
        elif query.data == "contact":
            contact_message = (
                "👨‍⚕️ *عن المطور - حيدر:*\n\n"
                "🩺 *طبيب متخصص* مع شغف كبير بعالم البرمجة\n"
                "💻 يطور البوتات كهواية لخدمة المجتمع\n"
                "🎯 يسعى لتوفير أدوات مفيدة ومجانية للجميع\n\n"
                "📬 *للتواصل المباشر:*\n"
                "• تلجرام: @docamir\n"
                "• قناة البوت: @yedevlepver\n\n"
                "💡 *يمكنك مراسلته بخصوص:*\n"
                "📧 المقترحات والتحسينات\n"
                "🐛 الإبلاغ عن مشاكل\n"
                "💭 طلب ميزات جديدة\n"
                "❓ الاستفسارات العامة\n\n"
                "🙏 *شكراً لاستخدام البوت!*"
            )
            await query.message.edit_text(contact_message, parse_mode='Markdown')
        elif query.data == "examples":
            examples_message = (
                "💡 *أمثلة للروابط المدعومة:*\n\n"
                "🔴 *يوتيوب:*\n"
                "`https://www.youtube.com/watch?v=...`\n"
                "`https://youtu.be/...`\n\n"
                "🐦 *تويتر:*\n"
                "`https://twitter.com/user/status/...`\n"
                "`https://x.com/user/status/...`\n\n"
                "📸 *انستقرام:*\n"
                "`https://www.instagram.com/reel/...`\n"
                "`https://www.instagram.com/p/...`\n\n"
                "👥 *فيسبوك:*\n"
                "`https://www.facebook.com/watch/...`\n"
                "`https://fb.watch/...`\n\n"
                "🎵 *تيك توك:*\n"
                "`https://www.tiktok.com/@user/video/...`\n"
                "`https://vm.tiktok.com/...`\n\n"
                "👻 *سناب شات:*\n"
                "`https://www.snapchat.com/spotlight/...`\n"
                "`https://story.snapchat.com/...`\n\n"
                "📝 *فقط انسخ والصق أي رابط من هذه المنصات!*"
            )
            await query.message.edit_text(examples_message, parse_mode='Markdown')
        elif query.data == "developer":
            developer_keyboard = [
                [InlineKeyboardButton("💬 تواصل مع المطور", url="https://t.me/docamir")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
            ]
            developer_reply_markup = InlineKeyboardMarkup(developer_keyboard)
            
            developer_message = (
                "👨‍⚕️ *نبذة عن المطور - د. حيدر*\n\n"
                "🌟 *مرحباً، أنا حيدر - مطور هذا البوت*\n\n"
                "🩺 *طبيب متخصص* مع شغف كبير بعالم البرمجة\n"
                "💻 *أطور البوتات كهواية لخدمة المجتمع*\n\n"
                "💡 *تخصصاتي في البرمجة:*\n"
                "🔹 برمجة بوتات التليجرام المتقدمة\n"
                "🔹 تطوير أنظمة تحميل الوسائط\n"
                "🔹 معالجة الفيديوهات والصوتيات\n"
                "🔹 تصميم واجهات المستخدم التفاعلية\n\n"
                "🎯 *رؤيتي:*\n"
                "الجمع بين الطب والتكنولوجيا لخدمة المجتمع\n"
                "جعل التكنولوجيا في متناول الجميع مجاناً\n\n"
                "🚀 *أعمل على:*\n"
                "• تحسينات مستمرة للبوت\n"
                "• إضافة منصات جديدة\n"
                "• دمج التكنولوجيا مع الطب\n\n"
                "💝 *أحب التواصل مع المستخدمين والمساعدة*\n"
                "اضغط الزر أدناه للمحادثة المباشرة!"
            )
            await query.message.edit_text(developer_message, parse_mode='Markdown', reply_markup=developer_reply_markup)
        elif query.data == "support":
            support_keyboard = [
                [InlineKeyboardButton("📞 تواصل مباشر مع المطور", callback_data="contact_developer")],
                [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq")],
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
            ]
            support_reply_markup = InlineKeyboardMarkup(support_keyboard)
            
            support_message = (
                "🆘 *مركز الدعم الفني*\n\n"
                "🌟 مرحباً بك في مركز الدعم!\n"
                "اختر طريقة المساعدة المناسبة:\n\n"
                "📞 *تواصل مباشر:* أرسل رسالتك للمطور\n"
                "❓ *أسئلة شائعة:* حلول سريعة للمشاكل\n\n"
                "💡 نحن هنا لمساعدتك 24/7"
            )
            await query.message.edit_text(support_message, parse_mode='Markdown', reply_markup=support_reply_markup)
        elif query.data == "contact_developer":
            contact_message = (
                "📝 *التواصل المباشر مع المطور*\n\n"
                "💬 اكتب رسالتك وسيتم إرسالها مباشرة للمطور\n"
                "📨 ستصلك الإجابة في أقرب وقت ممكن\n\n"
                "✏️ *اكتب رسالتك الآن:*\n"
                "يمكنك كتابة:\n"
                "• مشكلة تقنية تواجهها\n"
                "• اقتراح لتحسين البوت\n"
                "• أي استفسار أو شكوى\n\n"
                "🔄 /start للعودة"
            )
            # Set user state to waiting for support message
            context.user_data['waiting_for_support_message'] = True
            await query.message.edit_text(contact_message, parse_mode='Markdown')
        elif query.data == "faq":
            faq_message = (
                "❓ *الأسئلة الشائعة والحلول*\n\n"
                "🔸 *الرابط لا يعمل؟*\n"
                "تأكد أن الرابط صحيح ومن منصة مدعومة\n\n"
                "🔸 *التحميل بطيء؟*\n"
                "جرب وقت آخر أو اختر جودة أقل\n\n"
                "🔸 *لا يظهر خيار MP3؟*\n"
                "بعض الفيديوهات قد لا تدعم التحويل\n\n"
                "🔸 *حجم الملف كبير؟*\n"
                "اختر جودة أقل أو تأكد من سرعة النت\n\n"
                "🔸 *البوت لا يستجيب؟*\n"
                "جرب إعادة تشغيل المحادثة بـ /start\n\n"
                "🔄 العودة: /start"
            )
            await query.message.edit_text(faq_message, parse_mode='Markdown')
        elif query.data == "stats":
            # Show global bot statistics
            global_stats = self.stats.get_global_stats()
            
            stats_message = (
                "📊 **إحصائيات البوت العامة**\n\n"
                f"📥 *إجمالي التحميلات:* {global_stats['total_downloads']:,}\n"
                f"👥 *إجمالي المستخدمين:* {global_stats['total_users']:,}\n"
                f"📈 *تحميلات الأسبوع الماضي:* {global_stats['last_week_downloads']:,}\n"
                f"🔥 *ذروة التحميلات اليومية:* {global_stats['peak_daily_downloads']:,}\n"
                f"📋 *قوائم التشغيل المحملة:* {global_stats['playlists_downloaded']:,}\n"
                f"💾 *إجمالي حجم الملفات:* {global_stats['total_size_gb']} GB\n\n"
                f"🏆 *المنصة الأكثر شعبية:* {global_stats['most_popular_platform'][0]} "
                f"({global_stats['most_popular_platform'][1]:,} تحميل)\n\n"
                "📈 *التوزيع حسب المنصة:*\n"
                f"🎥 YouTube: {global_stats['platform_breakdown']['youtube']:,}\n"
                f"📱 TikTok: {global_stats['platform_breakdown']['tiktok']:,}\n"
                f"📸 Instagram: {global_stats['platform_breakdown']['instagram']:,}\n"
                f"📘 Facebook: {global_stats['platform_breakdown']['facebook']:,}\n"
                f"🐦 Twitter: {global_stats['platform_breakdown']['twitter']:,}\n\n"
                "🎯 *التوزيع حسب النوع:*\n"
                f"📹 فيديو: {global_stats['type_breakdown']['video']:,}\n"
                f"🎵 صوت: {global_stats['type_breakdown']['audio']:,}"
            )
            await query.message.edit_text(stats_message, parse_mode='Markdown')
        elif query.data == "my_stats":
            # Show user's personal statistics
            user_id = str(query.from_user.id)
            user_stats = self.stats.get_user_stats(user_id)
            
            if user_stats['downloads'] == 0:
                my_stats_message = (
                    "👤 **إحصائياتك الشخصية**\n\n"
                    "🆕 *مرحباً! أنت مستخدم جديد*\n\n"
                    "💡 ابدأ بتحميل أول فيديو لك لرؤية إحصائياتك!\n"
                    "🎯 أرسل أي رابط فيديو للبدء"
                )
            else:
                my_stats_message = (
                    "👤 **إحصائياتك الشخصية**\n\n"
                    f"📥 *تحميلاتك:* {user_stats['downloads']:,}\n"
                    f"🏆 *ترتيبك:* #{user_stats['rank']:,} من بين جميع المستخدمين\n\n"
                    f"📅 *أول استخدام:* {user_stats['first_use'][:10] if user_stats.get('first_use') else 'غير محدد'}\n"
                    f"🕐 *آخر استخدام:* {user_stats['last_use'][:10] if user_stats.get('last_use') else 'اليوم'}\n\n"
                    "🎉 شكراً لك على استخدام البوت!"
                )
            await query.message.edit_text(my_stats_message, parse_mode='Markdown')
        elif query.data == "back_to_main":
            # Create a proper Update object for start command
            keyboard = [
                [InlineKeyboardButton("📚 دليل الاستخدام", callback_data="help"),
                 InlineKeyboardButton("⚡ المميزات", callback_data="features")],
                [InlineKeyboardButton("🌐 المنصات المدعومة", callback_data="platforms"),
                 InlineKeyboardButton("❓ أسئلة شائعة", callback_data="faq")],
                [InlineKeyboardButton("👨‍⚕️ نبذة عن المطور", callback_data="developer"),
                 InlineKeyboardButton("💬 دعم فني", callback_data="support")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_message = (
                "🎬 *مرحباً بك في بوت تحميل الفيديوهات المتطور!*\n\n"
                "✨ *أرسل أي رابط فيديو وسأحمله لك فوراً:*\n"
                "📱 TikTok • 📘 Facebook • 📸 Instagram\n"
                "🐦 Twitter • 🎥 YouTube • 👻 Snapchat\n\n"
                "🎯 *اختر من القائمة أدناه:*"
            )
            await query.message.edit_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
        elif query.data == "cancel":
            await query.message.edit_text(
                "❌ *تم إلغاء العملية*\n\n"
                "💡 أرسل رابط فيديو جديد للمتابعة\n"
                "🚀 أو اضغط /start للعودة للقائمة الرئيسية"
            )
        elif query.data.startswith("download_audio_from_video_"):
            # Handle audio download from video URL
            url = query.data.replace("download_audio_from_video_", "")
            await query.answer("🎵 جاري تحميل الملف الصوتي...")
            
            # Show download progress for audio
            await self.show_download_progress(query.message, "audio", url)
            
            # Download audio
            file_path = await self.downloader.download_audio(url, self.temp_dir, "best")
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                # Get video info for title
                video_info = await self.downloader.get_video_info(url)
                title = video_info.get('title', 'ملف صوتي') if video_info else 'ملف صوتي'
                duration = video_info.get('duration') if video_info else None
                
                # Final success message for audio
                success_message = (
                    f"✅ **تم تحويل الفيديو لصوت بنجاح!**\n\n"
                    f"🎵 **ملف MP3 عالي الجودة جاهز**\n"
                    f"📁 **حجم الملف:** {format_file_size(file_size)}\n"
                    f"🎶 **جودة الصوت:** 192kbps\n\n"
                    f"🎉 **استمتع بملفك الصوتي!**"
                )
                
                await query.message.edit_text(success_message, parse_mode='Markdown')
                await asyncio.sleep(2)
                
                with open(file_path, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=query.message.chat.id,
                        audio=audio_file,
                        title=title[:50],
                        duration=duration,
                        caption=f"🎵 *{title[:50]}*\n\n"
                               f"📊 الجودة: عالية (192kbps)\n"
                               f"📦 الحجم: {format_file_size(file_size)}",
                        parse_mode='Markdown'
                    )
                await query.message.delete()
                os.remove(file_path)
            else:
                await query.message.edit_text("❌ فشل في تحميل الملف الصوتي\n💡 جرب مرة أخرى لاحقاً")
        elif query.data.startswith("pl_"):
            # Handle playlist actions
            parts = query.data.split("_")
            if len(parts) >= 3:
                action = parts[1]  # all, select, audio
                playlist_id = parts[2]
                url = context.user_data.get(f'pl_{playlist_id}')
                playlist_info = context.user_data.get(f'playlist_{playlist_id}')
                
                if url and playlist_info:
                    if action == "all":
                        # Download all videos
                        await query.message.edit_text("🔄 بدء تحميل جميع الفيديوهات...")
                        # TODO: Implement bulk download
                        await query.message.edit_text("⚠️ ميزة تحميل الكل قيد التطوير\n💡 استخدم 'اختيار فيديوهات محددة' حالياً")
                    elif action == "select":
                        # Show video selection
                        await self.show_video_selection(query, url, context)
                    elif action == "audio":
                        # Download all as audio
                        await query.message.edit_text("🔄 بدء تحميل جميع الأصوات...")
                        # TODO: Implement bulk audio download
                        await query.message.edit_text("⚠️ ميزة تحميل الكل كصوت قيد التطوير\n💡 استخدم 'اختيار فيديوهات محددة' حالياً")
        elif query.data.startswith("vid_"):
            # Handle individual video selection from playlist
            parts = query.data.split("_")
            if len(parts) >= 3:
                video_index = parts[1]
                playlist_id = parts[2]
                
                # Get playlist info and individual video URL
                playlist_info = context.user_data.get(f'playlist_{playlist_id}')
                if playlist_info:
                    entries = playlist_info.get('entries', [])
                    video_entry = next((e for e in entries if str(e.get('index')) == video_index), None)
                    
                    if video_entry:
                        video_url = video_entry.get('url') or video_entry.get('webpage_url')
                        if video_url:
                            # Store current URL and show format selection
                            context.user_data['current_url'] = video_url
                            await query.message.edit_text("🔄 جاري جلب معلومات الفيديو...")
                            
                            # Get video info and show format selection
                            formats_info = await self.downloader.get_available_formats(video_url)
                            if formats_info:
                                await self.show_format_selection(query.message, formats_info)
                            else:
                                await query.message.edit_text("❌ فشل في جلب معلومات الفيديو")
                        else:
                            await query.message.edit_text("❌ لم يتم العثور على رابط الفيديو")
                    else:
                        await query.message.edit_text("❌ لم يتم العثور على الفيديو المحدد")
                else:
                    await query.message.edit_text("❌ انتهت صلاحية قائمة التشغيل")
        elif query.data.startswith("download_"):
            # Handle download format selection
            parts = query.data.split("_", 2)
            if len(parts) >= 3:
                format_type = parts[1]  # video or audio
                format_id = parts[2]
                url = context.user_data.get('current_url')
                
                if url:
                    await self.download_with_format(query, context, url, format_type, format_id)

    async def show_format_selection(self, message, formats_info):
        """Show format selection menu with thumbnail preview"""
        title = formats_info.get('title', 'Unknown')[:50]
        duration = formats_info.get('duration', 0)
        thumbnail = formats_info.get('thumbnail', None)
        
        # Send thumbnail if available
        if thumbnail:
            try:
                await message.reply_photo(
                    photo=thumbnail,
                    caption=f"🖼️ *معاينة الفيديو*\n📹 {title}",
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Could not send thumbnail: {e}")
        
        info_text = f"📹 *{title}*\n"
        if duration:
            minutes, seconds = divmod(duration, 60)
            info_text += f"⏱ المدة: {int(minutes)}:{int(seconds):02d}\n"
        info_text += "\n🎯 اختر الجودة والصيغة:\n\n"
        
        keyboard = []
        
        # Video formats
        video_formats = formats_info.get('video_formats', [])
        if video_formats:
            info_text += "*📹 خيارات الفيديو:*\n"
            for i, fmt in enumerate(video_formats[:6]):  # Limit to 6 options
                quality = fmt.get('quality', 'Unknown')
                size = fmt.get('filesize', 0)
                ext = fmt.get('ext', 'mp4')
                
                size_text = format_file_size(size) if size else "تقديري"
                
                # Add quality indicators
                if quality.startswith('1080'):
                    emoji = "🔥"
                elif quality.startswith('720'):
                    emoji = "⭐"
                elif quality.startswith('480'):
                    emoji = "✅"
                else:
                    emoji = "📱"
                
                button_text = f"{emoji} {quality} - {size_text}"
                
                keyboard.append([InlineKeyboardButton(
                    button_text, 
                    callback_data=f"download_video_{fmt.get('format_id', '')}"
                )])
        
        # Audio formats - always show for all platforms
        info_text += "\n*🎵 خيارات الصوت:*\n"
        keyboard.append([InlineKeyboardButton("🎵 MP3 جودة عالية (192kbps)", callback_data="download_audio_best")])
        keyboard.append([InlineKeyboardButton("🎵 MP3 جودة متوسطة (128kbps)", callback_data="download_audio_medium")])
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.edit_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)

    async def download_with_format(self, query, context, url, format_type, format_id):
        """Download video/audio with specific format"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if format_type == "audio":
                # Enhanced audio download animation with progress
                await self.show_download_progress(query.message, "audio", url)
                
                # Download audio
                file_path = await self.downloader.download_audio(url, self.temp_dir, format_id)
                if file_path and os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    download_time = int(asyncio.get_event_loop().time() - start_time)
                    
                    await query.message.edit_text("📤 جاري رفع الملف الصوتي...")
                    
                    # Get video info for title
                    video_info = await self.downloader.get_video_info(url)
                    title = video_info.get('title', 'ملف صوتي') if video_info else 'ملف صوتي'
                    duration = video_info.get('duration') if video_info else None
                    
                    quality_text = "عالية (192kbps)" if format_id == "best" else "متوسطة (128kbps)"
                    
                    with open(file_path, 'rb') as audio_file:
                        await context.bot.send_audio(
                            chat_id=query.message.chat.id,
                            audio=audio_file,
                            title=title[:50],
                            duration=duration,
                            caption=f"🎵 *{title[:50]}*\n\n"
                                   f"📊 الجودة: {quality_text}\n"
                                   f"📦 الحجم: {format_file_size(file_size)}\n"
                                   f"⏱ وقت التحميل: {download_time}s",
                            parse_mode='Markdown'
                        )
                    await query.message.delete()
                    os.remove(file_path)
                    
                    # Send thank you message with share button
                    await self.send_thank_you_message(context, query.message.chat.id)
                else:
                    await query.message.edit_text("❌ فشل تحميل الملف الصوتي\n💡 جرب رابطاً آخر أو اختر جودة مختلفة")
                    
            else:
                # Enhanced video download animation with progress
                await self.show_download_progress(query.message, "video", url)
                
                # Download video
                file_path = await self.downloader.download_video_format(url, self.temp_dir, format_id)
                if file_path and os.path.exists(file_path):
                    # Check file size
                    file_size = os.path.getsize(file_path)
                    if file_size > MAX_FILE_SIZE:
                        await query.message.edit_text(
                            f"❌ الملف كبير جداً!\n"
                            f"📦 حجم الملف: {format_file_size(file_size)}\n"
                            f"📏 الحد الأقصى: {format_file_size(MAX_FILE_SIZE)}\n\n"
                            f"💡 جرب جودة أقل أو حمل الصوت بدلاً من ذلك"
                        )
                        os.remove(file_path)
                        return
                    
                    download_time = int(asyncio.get_event_loop().time() - start_time)
                    await query.message.edit_text("📤 جاري رفع الفيديو...")
                    
                    # Get video info for better metadata
                    video_info = await self.downloader.get_video_info(url)
                    title = video_info.get('title', 'فيديو') if video_info else 'فيديو'
                    duration = video_info.get('duration') if video_info else None
                    width = video_info.get('width') if video_info else None
                    height = video_info.get('height') if video_info else None
                    thumbnail_url = video_info.get('thumbnail') if video_info else None
                    
                    # Create enhanced caption
                    caption = f"🎥 *{title[:50]}*\n\n"
                    if width and height:
                        caption += f"📺 الدقة: {width}x{height}\n"
                    if duration:
                        minutes, seconds = divmod(duration, 60)
                        caption += f"⏱ المدة: {int(minutes)}:{int(seconds):02d}\n"
                    caption += f"📦 الحجم: {format_file_size(file_size)}\n"
                    caption += f"⚡ وقت التحميل: {download_time}s"
                    
                    # Download thumbnail if available
                    thumbnail_file = None
                    if thumbnail_url:
                        try:
                            import requests
                            thumbnail_response = requests.get(thumbnail_url, timeout=10)
                            if thumbnail_response.status_code == 200:
                                thumbnail_file = thumbnail_response.content
                        except Exception as e:
                            logger.info(f"Could not download thumbnail: {e}")
                    
                    with open(file_path, 'rb') as video_file:
                        await context.bot.send_video(
                            chat_id=query.message.chat.id,
                            video=video_file,
                            thumbnail=thumbnail_file,
                            caption=caption,
                            supports_streaming=True,
                            duration=duration,
                            width=width,
                            height=height,
                            parse_mode='Markdown'
                        )
                    await query.message.delete()
                    os.remove(file_path)
                    
                    # Send thank you message with share button
                    await self.send_thank_you_message(context, query.message.chat.id)
                else:
                    await query.message.edit_text("❌ فشل تحميل الفيديو\n💡 جرب رابطاً آخر أو اختر جودة مختلفة")
                    
        except Exception as e:
            logger.error(f"Error downloading {format_type}: {str(e)}")
            await query.message.edit_text(
                f"❌ حدث خطأ أثناء التحميل\n"
                f"💡 جرب مرة أخرى أو استخدم رابطاً مختلفاً"
            )

    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle video URL messages and playlists"""
        url = update.message.text.strip()
        
        # Validate URL
        if not is_valid_url(url):
            platform_list = '\n'.join([f'• {platform}' for platform in SUPPORTED_PLATFORMS])
            await update.message.reply_text(
                f"❌ Please send a valid video URL from one of the supported platforms:\n{platform_list}"
            )
            return

        # Check if it's a playlist URL
        is_playlist = await self.downloader.is_playlist_url(url)
        
        if is_playlist:
            await self.handle_playlist_url(update, context, url)
            return

        # Special handling for Snapchat URLs
        if 'snapchat.com' in url.lower() or 'spotlight' in url.lower():
            await update.message.reply_text(
                "👻 *رابط Snapchat مكتشف!*\n\n"
                "⚠️ للأسف، Snapchat يحمي محتواه بحماية قوية\n"
                "🔒 معظم مقاطع Spotlight والقصص محمية\n"
                "💡 جرب هذه البدائل:\n\n"
                "📱 استخدم تطبيق Snapchat لحفظ المقطع\n"
                "🔄 أو شارك المحتوى من منصة أخرى\n"
                "📸 أو التقط سكرين ريكورد\n\n"
                "🌟 نعمل على تحسين دعم Snapchat قريباً!",
                parse_mode='Markdown'
            )
            return

        # Check if URL is from supported platform
        if not any(platform.lower() in url.lower() for platform in 
                  ['youtube.com', 'youtu.be', 'twitter.com', 'x.com', 'instagram.com', 
                   'facebook.com', 'fb.watch', 'tiktok.com']):
            platform_list = '\n'.join([f'• {platform}' for platform in SUPPORTED_PLATFORMS])
            await update.message.reply_text(
                f"❌ هذه المنصة غير مدعومة حالياً. الرجاء استخدام روابط من:\n{platform_list}"
            )
            return

        # Show typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Send enhanced processing message with animation
        processing_frames = [
            "🔄 جاري تحليل الرابط...",
            "🔍 البحث عن الفيديو...", 
            "📊 جمع المعلومات...",
            "🎬 تحضير المعاينة..."
        ]
        
        processing_msg = await update.message.reply_text(processing_frames[0])
        
        try:
            # Animate processing
            for i, frame in enumerate(processing_frames[1:], 1):
                await asyncio.sleep(0.8)
                await processing_msg.edit_text(frame)
            
            # Get video info and available formats
            formats_info = await self.downloader.get_available_formats(url)
            
            if not formats_info:
                await processing_msg.edit_text("❌ Could not get video information. Please check the URL and try again.")
                return
            
            # Store URL for callback handling
            context.user_data['current_url'] = url
            
            # Show format selection menu
            await self.show_format_selection(processing_msg, formats_info)
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            await processing_msg.edit_text(
                "❌ An error occurred while processing your request. "
                "Please check the URL and try again."
            )

    async def handle_playlist_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
        """Handle playlist/channel URLs with video selection"""
        try:
            # Show processing message
            processing_message = await update.message.reply_text(
                "📋 *جاري تحليل قائمة التشغيل...*\n"
                "⏳ *يرجى الانتظار قليلاً*",
                parse_mode='Markdown'
            )
            
            # Get playlist info
            playlist_info = await self.downloader.get_playlist_info(url)
            
            if not playlist_info:
                await processing_message.edit_text(
                    "❌ *عذراً، لم أتمكن من الحصول على معلومات قائمة التشغيل*\n\n"
                    "🔸 تأكد من صحة الرابط\n"
                    "🔸 تأكد أن القائمة متاحة للعامة\n"
                    "🔸 جرب رابط قائمة تشغيل أخرى",
                    parse_mode='Markdown'
                )
                return
            
            # Show playlist overview
            entries = playlist_info.get('entries', [])
            total_count = len(entries)
            
            if total_count == 0:
                await processing_message.edit_text(
                    "📋 *قائمة التشغيل فارغة*\n\n"
                    "💡 جرب رابط قائمة تشغيل أخرى تحتوي على فيديوهات",
                    parse_mode='Markdown'
                )
                return
            
            # Create selection interface with short callback data
            # Store URL with a simple key
            playlist_id = str(abs(hash(url)) % 9999)
            context.user_data[f'pl_{playlist_id}'] = url
            context.user_data[f'playlist_{playlist_id}'] = playlist_info
            
            keyboard = [
                [InlineKeyboardButton("📥 تحميل الكل", callback_data=f"pl_all_{playlist_id}")],
                [InlineKeyboardButton("🎯 اختيار فيديوهات محددة", callback_data=f"pl_select_{playlist_id}")],
                [InlineKeyboardButton("🎵 تحميل الكل كصوت", callback_data=f"pl_audio_{playlist_id}")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            playlist_message = (
                f"📋 **{playlist_info.get('title', 'قائمة تشغيل')}**\n\n"
                f"👤 *القناة:* {playlist_info.get('uploader', 'غير محدد')}\n"
                f"🎬 *عدد الفيديوهات:* {total_count}\n\n"
                f"🎯 *اختر طريقة التحميل:*"
            )
            
            await processing_message.edit_text(
                playlist_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Store playlist info in context for later use
            context.user_data[f'playlist_{url}'] = playlist_info
            
        except Exception as e:
            logger.error(f"Error handling playlist URL {url}: {e}")
            await update.message.reply_text(
                "❌ *خطأ في معالجة قائمة التشغيل*\n\n"
                "💡 *جرب مرة أخرى أو استخدم رابطاً مختلفاً*",
                parse_mode='Markdown'
            )

    async def show_video_selection(self, query, url: str, context) -> None:
        """Show video selection interface for playlist"""
        try:
            # Find playlist_id from stored data
            playlist_id = None
            for key in context.user_data:
                if key.startswith('pl_') and context.user_data[key] == url:
                    playlist_id = key.replace('pl_', '')
                    break
            
            if not playlist_id:
                await query.message.edit_text("❌ انتهت صلاحية قائمة التشغيل، يرجى إرسال الرابط مرة أخرى")
                return
                
            playlist_info = context.user_data.get(f'playlist_{playlist_id}')
            if not playlist_info:
                await query.message.edit_text("❌ انتهت صلاحية قائمة التشغيل، يرجى إرسال الرابط مرة أخرى")
                return
            
            entries = playlist_info.get('entries', [])
            page = 0
            videos_per_page = 10
            
            # Show first page of videos
            await self.show_video_page(query.message, entries, page, videos_per_page, playlist_id)
            
        except Exception as e:
            logger.error(f"Error showing video selection: {e}")
            await query.message.edit_text("❌ خطأ في عرض الفيديوهات")

    async def show_video_page(self, message, entries, page, videos_per_page, url):
        """Show a page of videos for selection"""
        start_idx = page * videos_per_page
        end_idx = min(start_idx + videos_per_page, len(entries))
        page_entries = entries[start_idx:end_idx]
        
        keyboard = []
        
        # Video selection buttons
        for entry in page_entries:
            title = entry.get('title', 'فيديو')[:40]
            duration = entry.get('duration')
            duration_text = f" ({duration//60}:{duration%60:02d})" if duration else ""
            
            button_text = f"📹 {entry['index']}. {title}{duration_text}"
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"vid_{entry['index']}_{url[-4:]}"
            )])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}_{url}"))
        if end_idx < len(entries):
            nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}_{url}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Action buttons
        keyboard.append([
            InlineKeyboardButton("✅ تحميل المحددة", callback_data=f"download_selected_{url}"),
            InlineKeyboardButton("🔄 إلغاء التحديد", callback_data=f"clear_selection_{url}")
        ])
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data=f"back_to_playlist_{url}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        info_text = (
            f"🎯 *اختر الفيديوهات للتحميل*\n\n"
            f"📄 *الصفحة {page + 1} من {(len(entries) - 1) // videos_per_page + 1}*\n"
            f"🎬 *الفيديوهات {start_idx + 1}-{end_idx} من {len(entries)}*\n\n"
            f"💡 *اضغط على الفيديوهات لتحديدها*"
        )
        
        await message.edit_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)

    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'snapchat.com' in url_lower:
            return 'snapchat'
        else:
            return 'unknown'

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-URL messages"""
        text = update.message.text
        
        # Check if user is waiting to send a support message
        if context.user_data.get('waiting_for_support_message'):
            # Clear the waiting state
            context.user_data['waiting_for_support_message'] = False
            # Process the support message
            await self.forward_support_message(update, context, text)
            return
        
        if text and any(keyword in text.lower() for keyword in ['http', 'www', '.com', '.ly']):
            # Looks like a URL, handle it
            await self.handle_url(update, context)
        else:
            # Send interactive help message
            help_keyboard = [
                [InlineKeyboardButton("📚 كيفية الاستخدام", callback_data="help")],
                [InlineKeyboardButton("🌐 المنصات المدعومة", callback_data="features")],
                [InlineKeyboardButton("💡 أمثلة للروابط", callback_data="examples")]
            ]
            reply_markup = InlineKeyboardMarkup(help_keyboard)
            
            await update.message.reply_text(
                "🤔 *يبدو أنك لم ترسل رابط فيديو!*\n\n"
                "💡 *إليك ما يمكنك فعله:*\n"
                "📱 انسخ رابط فيديو من يوتيوب أو فيسبوك أو تيك توك\n"
                "📋 الصق الرابط هنا مباشرة\n"
                "⚡ سأبدأ التحميل فوراً!\n\n"
                "👇 *أو اختر من القائمة أدناه:*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    


    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            logger.error(f"Exception while handling an update: {context.error}")
            
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An unexpected error occurred. Please try again later."
                )
        
        application.add_error_handler(error_handler)
        
        # Cleanup temp files on shutdown
        def cleanup_on_shutdown():
            cleanup_temp_files(self.temp_dir)
        
        # Start the bot
        logger.info("Starting bot...")
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            cleanup_on_shutdown()

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is required!")
        return
    
    bot = TelegramVideoBot()
    bot.run()

if __name__ == '__main__':
    main()
