"""
Animated Responses and Beautiful Messages Module
"""
import asyncio
import random
from typing import List, Dict

class AnimatedResponses:
    def __init__(self):
        self.loading_animations = [
            ["🔵", "⚪", "⚪", "⚪"],
            ["⚪", "🔵", "⚪", "⚪"],
            ["⚪", "⚪", "🔵", "⚪"],
            ["⚪", "⚪", "⚪", "🔵"],
            ["⚪", "⚪", "🔵", "⚪"],
            ["⚪", "🔵", "⚪", "⚪"],
        ]
        
        self.progress_bars = [
            "▰▱▱▱▱▱▱▱▱▱ 10%",
            "▰▰▱▱▱▱▱▱▱▱ 20%",
            "▰▰▰▱▱▱▱▱▱▱ 30%",
            "▰▰▰▰▱▱▱▱▱▱ 40%",
            "▰▰▰▰▰▱▱▱▱▱ 50%",
            "▰▰▰▰▰▰▱▱▱▱ 60%",
            "▰▰▰▰▰▰▰▱▱▱ 70%",
            "▰▰▰▰▰▰▰▰▱▱ 80%",
            "▰▰▰▰▰▰▰▰▰▱ 90%",
            "▰▰▰▰▰▰▰▰▰▰ 100%"
        ]

    def get_welcome_message(self, user_name: str = "صديقي") -> str:
        """Get animated welcome message"""
        messages = [
            f"🌟 أهلاً وسهلاً {user_name}! 🌟\n\n"
            "🎭 مرحباً بك في عالم التحميل السحري!\n"
            "✨ حيث الفيديوهات تطير إليك بسرعة البرق\n"
            "🚀 والجودة تلامس النجوم\n\n"
            "💫 ما رأيك ننطلق في رحلة ممتعة؟",
            
            f"🎉 يا أهلاً {user_name}! 🎉\n\n"
            "🔮 دخلت إلى مملكة التحميلات السحرية\n"
            "⚡ حيث كل رابط يتحول إلى كنز رقمي\n"
            "🏆 وكل تحميل يصبح إنجازاً مميزاً\n\n"
            "🎯 هيا نبدأ المغامرة!",
            
            f"🌈 مرحباً {user_name}! 🌈\n\n"
            "🎪 أدخلتك هنا بوابة عجائب التكنولوجيا\n"
            "🎨 حيث الإبداع يلتقي بالسرعة\n"
            "💎 والأحلام تصبح ملفات\n\n"
            "🔥 استعد لتجربة لا تُنسى!"
        ]
        return random.choice(messages)

    def get_processing_message(self) -> str:
        """Get animated processing message"""
        messages = [
            "🔮 *السحر يحدث الآن...*\n\n"
            "⚡ أكتشف أسرار الرابط\n"
            "🎭 أفك تشفيره بمهارة\n"
            "✨ أستخرج أفضل الخيارات\n"
            "🎯 أجهز المفاجآت\n\n"
            "💫 الإثارة تتصاعد...",
            
            "🚀 *المهمة السرية بدأت!*\n\n"
            "🕵️ أتسلل إلى الخادم\n"
            "🔐 أفك الأقفال الرقمية\n"
            "💎 أستخرج الجواهر الخفية\n"
            "🎪 أحضر العرض المذهل\n\n"
            "⏰ لحظات قليلة فقط...",
            
            "🎨 *ورشة الإبداع تعمل!*\n\n"
            "🔧 أحلل البيانات بدقة\n"
            "⚙️ أصمم خيارات مثالية\n"
            "🎭 أزين النتائج بجمال\n"
            "✨ أضع اللمسات السحرية\n\n"
            "🎁 الهدية تقترب..."
        ]
        return random.choice(messages)

    def get_success_message(self, file_type: str = "الملف") -> str:
        """Get animated success message"""
        messages = [
            f"🎉 *تم بنجاح باهر!* 🎉\n\n"
            f"✨ {file_type} جاهز ومتألق\n"
            "🏆 جودة مثالية كما طلبت\n"
            "⚡ سرعة خاطفة كما وعدت\n"
            "💎 نتيجة تستحق الإعجاب\n\n"
            "🎭 استمتع بإبداعك!",
            
            f"🚀 *مهمة مكتملة!* 🚀\n\n"
            f"🎯 {file_type} وصل بأمان\n"
            "💫 تم تحضيره بعناية فائقة\n"
            "🔥 النتيجة تفوق التوقعات\n"
            "⭐ إنجاز يستحق التهنئة\n\n"
            "🎊 أحسنت الاختيار!",
            
            f"💎 *كنز رقمي تم اكتشافه!* 💎\n\n"
            f"🎨 {file_type} معدّ بإتقان\n"
            "🌟 جودة تلامس الكمال\n"
            "🎪 عرض مبهر للحواس\n"
            "✨ سحر التكنولوجيا\n\n"
            "🏅 تستحق كل التقدير!"
        ]
        return random.choice(messages)

    def get_error_message(self) -> str:
        """Get friendly error message"""
        messages = [
            "😅 *عذراً، حدث شيء غير متوقع!*\n\n"
            "🔧 لا تقلق، هذا جزء من المغامرة\n"
            "💡 دعنا نجرب مرة أخرى\n"
            "🎯 المحاولة القادمة ستكون أفضل\n\n"
            "💪 لا نستسلم أبداً!",
            
            "🎭 *المسرح يواجه تحدياً صغيراً!*\n\n"
            "⚡ الخطأ مجرد استراحة قصيرة\n"
            "🔮 السحر سيعود أقوى\n"
            "🚀 التحدي يزيدنا قوة\n\n"
            "✨ هيا نعيد المحاولة!",
            
            "🎪 *توقف مؤقت في العرض!*\n\n"
            "🎨 نعيد ترتيب الديكور\n"
            "🔄 نجهز عرضاً أروع\n"
            "💎 الأفضل دائماً في الطريق\n\n"
            "🌟 ثق بنا، سننجح معاً!"
        ]
        return random.choice(messages)

    def get_achievement_message(self, achievement_name: str) -> str:
        """Get achievement unlock message"""
        return (
            f"🏆 *إنجاز جديد مفتوح!* 🏆\n\n"
            f"✨ {achievement_name} ✨\n\n"
            "🎉 تهانينا الحارة!\n"
            "⭐ +50 نقطة مكافأة\n"
            "🔥 تقدم رائع في رحلتك\n"
            "💎 مهارة متقدمة\n\n"
            "🚀 واصل التميز!"
        )

    def get_stats_intro(self) -> str:
        """Get stats introduction message"""
        return (
            "📊 *مرحباً في مركز قيادة إحصائياتك!* 📊\n\n"
            "🎯 هنا تجد ملخص رحلتك المذهلة\n"
            "📈 كل رقم يحكي قصة نجاح\n"
            "⚡ كل تحميل خطوة نحو التميز\n"
            "🏆 كل إنجاز يستحق الاحتفال\n\n"
            "💫 تفضل واستكشف عالمك الرقمي!"
        )

    # Motivational messages removed as requested by user

    async def animate_progress(self, message, steps: List[str], delay: float = 1.0):
        """Animate progress through steps"""
        for i, step in enumerate(steps):
            progress = self.progress_bars[min(i * 2, len(self.progress_bars) - 1)]
            text = f"{step}\n\n{progress}"
            await message.edit_text(text, parse_mode='Markdown')
            await asyncio.sleep(delay)

    def get_platform_greeting(self, platform: str) -> str:
        """Get platform-specific greeting"""
        greetings = {
            "youtube": "🔴 يوتيوب المفضل! مكان الإبداع اللامحدود!",
            "tiktok": "🎵 تيك توك الممتع! عالم الإبداع القصير!",
            "instagram": "📸 انستقرام الجميل! معرض الفن الرقمي!",
            "facebook": "👥 فيسبوك الاجتماعي! ملتقى الأصدقاء!",
            "twitter": "🐦 تويتر السريع! أخبار العالم في لحظة!",
            "snapchat": "👻 سناب شات المرح! لحظات عابرة تستحق الحفظ!"
        }
        return greetings.get(platform.lower(), "🌐 منصة رائعة اخترتها!")

    def get_quality_compliment(self, quality: str) -> str:
        """Get compliment based on quality choice"""
        if "1080" in quality or "HD" in quality:
            return "💎 اختيار ممتاز! عاشق الجودة العالية!"
        elif "720" in quality:
            return "⭐ خيار ذكي! التوازن المثالي!"
        elif "480" in quality:
            return "✅ اختيار عملي! السرعة والكفاءة!"
        else:
            return "🎯 قرار حكيم! تعرف ما تريد!"

    def get_random_fact(self) -> str:
        """Get random interesting fact"""
        facts = [
            "💡 هل تعلم؟ يتم رفع أكثر من 500 ساعة فيديو على يوتيوب كل دقيقة!",
            "🌍 حقيقة: تيك توك متاح في أكثر من 150 دولة حول العالم!",
            "📱 معلومة: انستقرام لديه أكثر من 2 مليار مستخدم نشط شهرياً!",
            "⚡ سرعة: البوت يمكنه معالجة عشرات الطلبات في نفس الوقت!",
            "🎨 إبداع: كل فيديو تحمله هو قطعة فن رقمية فريدة!",
            "🔬 تقنية: yt-dlp يدعم أكثر من 1000 موقع مختلف!",
            "🌟 إنجاز: شاركت في تحميل آلاف الفيديوهات للمستخدمين!",
            "🎭 متعة: كل تحميل يحمل قصة وذكرى جميلة!"
        ]
        return random.choice(facts)