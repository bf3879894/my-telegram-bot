import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ضع التوكن الخاص بك هنا
BOT_TOKEN = "8619380774:AAHQGaLZltjLEEJNXdLPPorD939GX1cyWX4"

MIN_WITHDRAWAL = 100.0
MINING_REWARD = 1.00
DAILY_REWARD = 5.00
REFERRAL_REWARD = 3.00

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_balances = {}
user_referrals = {}
last_mining = {}
last_daily = {}

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡ بدء التعدين السريع"), KeyboardButton(text="🎁 المكافأة اليومية")],
        [KeyboardButton(text="📊 حسـابي والسحب"), KeyboardButton(text="🔗 رابط الدعوة والربح")],
        [KeyboardButton(text="📣 القناة الرسمية")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    if user_id not in user_balances:
        user_balances[user_id] = 1.00
        user_referrals[user_id] = 0

        if command.args and command.args.isdigit():
            referrer_id = int(command.args)
            if referrer_id != user_id and referrer_id in user_balances:
                user_balances[referrer_id] += REFERRAL_REWARD
                user_referrals[referrer_id] += 1
                try:
                    await bot.send_message(
                        referrer_id,
                        f"🎉 انضم صديق جديد عبر رابطك!\n💰 تم إضافة +${REFERRAL_REWARD:.2f} لرصيدك."
                    )
                except Exception:
                    pass

    msg = (
        f"أهلاً بك 👋 {first_name} في منصة التعدين والربح!\n\n"
        f"🎁 هدية الانضمام: تم إضافة $1.00 لرصيدك تلقائياً.\n"
        f"💰 رصيدك الحالي: ${user_balances[user_id]:.2f}\n\n"
        f"اختر من القائمة بالأسفل لبدء جمع الأرباح:"
    )
    await message.answer(msg, reply_markup=main_keyboard)

@dp.message(F.text == "⚡ بدء التعدين السريع")
async def mining_handler(message: types.Message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id in last_mining:
        time_passed = (now - last_mining[user_id]).total_seconds()
        if time_passed < 3600:
            rem_min = int((3600 - time_passed) // 60)
            rem_sec = int((3600 - time_passed) % 60)
            await message.answer(
                f"⏳ جهاز التعدين يعمل الآن!\n"
                f"يرجى الانتظار {rem_min} دقيقة و {rem_sec} ثانية حتى تكتمل الدورة القادمة."
            )
            return

    last_mining[user_id] = now
    user_balances[user_id] = user_balances.get(user_id, 1.0) + MINING_REWARD
    await message.answer(
        f"✅ تمت عملية التعدين بنجاح!\n\n"
        f"💵 المكافأة المكتسبة: +${MINING_REWARD:.2f}\n"
        f"💰 رصيدك الإجمالي الآن: ${user_balances[user_id]:.2f}\n\n"
        f"💡 يمكنك العودة والتعدين مجدداً بعد ساعة!"
    )

@dp.message(F.text == "🎁 المكافأة اليومية")
async def daily_handler(message: types.Message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id in last_daily:
        time_passed = (now - last_daily[user_id]).total_seconds()
        if time_passed < 86400:
            rem_hours = int((86400 - time_passed) // 3600)
            await message.answer(
                f"⏳ لقد حصلت على مكافأتك اليومية بالفعل!\n"
                f"عد بعد {rem_hours} ساعة للحصول على المكافأة القادمة."
            )
            return

    last_daily[user_id] = now
    user_balances[user_id] = user_balances.get(user_id, 1.0) + DAILY_REWARD
    await message.answer(
        f"🎉 مبروك! حصلت على المكافأة اليومية بقيمة ${DAILY_REWARD:.2f}!\n"
        f"💰 رصيدك الحالي: ${user_balances[user_id]:.2f}"
    )

@dp.message(F.text == "🔗 رابط الدعوة والربح")
async def invite_handler(message: types.Message):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    refs_count = user_referrals.get(user_id, 0)

    await message.answer(
        f"🔥 أنشئ دخلك عبر ربط الأصدقاء!\n\n"
        f"لكل صديق يدخل عبر رابطك:\n"
        f"🎁 تحصل أنت على +${REFERRAL_REWARD:.2f} فوراً!\n\n"
        f"🔗 رابط الدعوة الخاص بك:\n{ref_link}\n\n"
        f"📊 عدد إحالاتك الحالية: {refs_count}"
    )

@dp.message(F.text == "📊 حسـابي والسحب")
async def account_handler(message: types.Message):
    user_id = message.from_user.id
    bal = user_balances.get(user_id, 1.0)
    refs = user_referrals.get(user_id, 0)

    status = (
        f"✅ يمكنك طلب السحب الآن من التطبيق المصغر!"
        if bal >= MIN_WITHDRAWAL
        else f"⚠️ يتبقى لك ${MIN_WITHDRAWAL - bal:.2f} للوصول للحد الأدنى للسحب."
    )

    await message.answer(
        f"👤 **بيانات حسابك:**\n\n"
        f"💰 الرصيد الحالي: ${bal:.2f}\n"
        f"👥 عدد الإحالات: {refs}\n"
        f"💳 الحد الأدنى للسحب: ${MIN_WITHDRAWAL:.2f}\n\n"
        f"{status}",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📣 القناة الرسمية")
async def channel_handler(message: types.Message):
    await message.answer("اشترك في القناة الرسمية لتلقي التحديثات وإثباتات السحب:\nhttps://t.me/alribh_alarabi")

async def main():
    print("ArabProfitBot Engine Started Successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
