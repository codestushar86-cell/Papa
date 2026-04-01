import asyncio
import logging
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ========================= CONFIG =========================
BOT_TOKEN = "8660859572:AAEQU0LPtrNt2BEMghjzwaSAEaeHvZJPGG4"          # ← Apna Token daalo
ADMIN_ID = 8684885145                       # ← Apna Telegram ID daalo

QR_URL = "https://ibb.co/Xk3jzwd1"          # ← Apna QR Code Direct Link

UPI_ID = "kartik.tushar@fam"                    # ← Apna real UPI ID daal do
DEVELOPER_USERNAME = "@UKRAINEBOOM"         # ← Apna Telegram username (without @)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===================== BOT SETUP =====================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(skip_updates=True)

# ====================== STATES ======================
class Payment(StatesGroup):
    waiting_screenshot = State()

# ====================== KEYBOARDS (Colored Buttons) ======================
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 UPI Info", callback_data="upi_info", style="danger")],   # Green
        [InlineKeyboardButton(text="💰 Add Fund", callback_data="add_fund", style="primary")],   # Blue
        [InlineKeyboardButton(text="👨‍💻 Developer", callback_data="developer", style="danger")]  # Red
    ])
    return keyboard

def back_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_main", style="success")]       # Green
    ])
    return keyboard

# ====================== WELCOME (No QR on start) ======================
async def send_welcome(message: Message):
    welcome_text = (
        "🔥 <b>WELCOME TO UPI TO NUMBER SERVICE</b> 🔥\n\n"
        "Real-Time • Secure • Fast • Private\n\n"
        "💰 Your Balance: <b>0</b> Points\n\n"
        "Choose an option below 👇"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu()
    )

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start(message: Message):
    await send_welcome(message)

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.delete()
    await send_welcome(callback.message)
    await callback.answer()

# =================== DEVELOPER (Direct DM) ===================
@dp.callback_query(F.data == "developer")
async def developer(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👨‍💻 <b>Developer Contact</b>\n\n"
        f"Bot banaya gaya hai aapke liye ❤️\n\n"
        f"Direct Message bhejne ke liye click karein 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Message Developer", url=f"https://t.me/{DEVELOPER_USERNAME}", style="primary")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_main", style="success")]
        ])
    )
    await callback.answer()

# =================== ADD FUND (QR with Payment) ===================
@dp.callback_query(F.data == "add_fund")
async def add_fund(callback: CallbackQuery, state: FSMContext):
    add_text = (
        "💰 <b>Add Funds - UPI Payment</b>\n\n"
        f"Amount: <b>₹30</b>\n\n"
        f"📱 UPI ID: <code>{UPI_ID}</code>\n\n"
        "🔹 Is UPI ID par exactly <b>₹30</b> bhejo\n"
        "🔹 Payment karne ke baad screenshot yahan bhejo\n\n"
        "<i>Payment verify hone ke baad aapko access mil jayega</i>"
    )

    await callback.message.edit_text(
        add_text,
        reply_markup=back_keyboard()
    )

    if QR_URL.startswith("http"):
        await callback.message.answer_photo(
            photo=QR_URL,
            caption="📸 Scan this QR Code ya upar diye UPI ID par pay karo"
        )

    await state.set_state(Payment.waiting_screenshot)
    await callback.answer()

# =================== UPI INFO (Realistic) ===================
@dp.callback_query(F.data == "upi_info")
async def upi_info(callback: CallbackQuery):
    utr = f"{random.randint(1000,9999)}{random.randint(100000,999999)}"
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    upi_text = (
        "✅ <b>UPI Payment Information</b>\n\n"
        f"💸 <b>UPI ID:</b> <code>{UPI_ID}</code>\n\n"
        f"🔢 <b>Reference / UTR Number:</b> <code>{utr}</code>\n\n"
        f"⏰ <b>Time:</b> {now}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 <b>Payment Instructions:</b>\n"
        "• Is UPI ID par <b>₹30</b> bhejo\n"
        "• Payment karne ke turant baad screenshot bhej do\n\n"
        "<i>Admin turant verify kar lenge. Real-time service hai.</i>"
    )

    await callback.message.edit_text(
        upi_text,
        reply_markup=back_keyboard()
    )
    await callback.answer()

# =================== RECEIVE SCREENSHOT ===================
@dp.message(Payment.waiting_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    await message.answer(
        "✅ <b>Payment Screenshot Received ✓</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⏳ Status: <b>Pending Verification</b>\n\n"
        "Admin will verify shortly aur aapko update denge.",
        reply_markup=back_keyboard()
    )

    try:
        user = message.from_user
        caption = (
            f"🔔 <b>New Payment Screenshot</b>\n\n"
            f"👤 User ID: <code>{user.id}</code>\n"
            f"📛 Name: {user.full_name}\n"
            f"🔗 Username: @{user.username if user.username else 'N/A'}\n"
            f"⏰ Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )

        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption
        )
    except Exception as e:
        logging.error(f"Failed to send to admin: {e}")

    await state.clear()

@dp.message(Payment.waiting_screenshot)
async def receive_any(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            "❌ Please send a <b>photo/screenshot</b> of the payment.",
            reply_markup=back_keyboard()
        )

# ====================== RUN BOT ======================
async def main():
    print("🚀 Bot Started Successfully! Send /start in Telegram")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())