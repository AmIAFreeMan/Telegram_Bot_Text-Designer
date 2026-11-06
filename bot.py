import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен BOT_TOKEN не найден! Проверьте файл .env.")

# Define states for bot workflow
class StyleState(StatesGroup):
    waiting_for_text = State()
    waiting_for_style = State()

# Simple Unicode font conversion dictionaries
def apply_style(text: str, style: str) -> str:
    
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    
    if style == "serif_bold":
       
        styled = "𝐀𝐁𝐂𝐃𝐄𝐅𝙶𝐇𝐈𝐉𝐊𝐋𝐌𝚰𝙾𝚱𝚲𝚳𝚴𝚵𝚶𝚷𝚸𝚹𝚺𝚻𝚼𝚽𝚾𝚿𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝚕𝙢𝙣𝒐𝚙𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
        
    
    # Standard Unicode offsets for Monospace and Serif/Italic variants:
    result = []
    for char in text:
        code = ord(char)
        if style == "monospace":
            # Monospace block: U+1D670 - U+1D683 for A-Z, U+1D684 - U+1D69D for a-z
            if 65 <= code <= 90:   # A-Z
                result.append(chr(code + 0x1D670 - 65))
            elif 97 <= code <= 122: # a-z
                result.append(chr(code + 0x1D684 - 97))
            elif 48 <= code <= 57:  # 0-9
                result.append(chr(code + 0x1D7F6 - 48))
            else:
                result.append(char)
        elif style == "script":
            
            script_map = {
                'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ', 'G': '𝒢', 
                'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ', 'M': 'ℳ', 'N': '𝒩', 
                'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ', 'S': '𝒮', 'T': '𝒯', 'U': '𝒰', 
                'V': '𝒱', 'W': '𝒲', 'X': '𝒳', 'Y': '𝒴', 'Z': '𝒵',
                'a': '𝒶', 'b': '𝒷', 'c': '𝒸', 'd': '𝒹', 'e': 'ℯ', 'f': '𝒻', 'g': 'ℊ', 
                'h': '𝒽', 'i': '𝒾', 'j': '𝒿', 'k': '𝓀', 'l': '𝓁', 'm': '𝓂', 'n': '𝓃', 
                'o': 'ℴ', 'p': '𝓅', 'q': '𝓆', 'r': '𝓇', 's': '𝓈', 't': '𝓉', 'u': '𝓊', 
                'v': '𝓿', 'w': '𝓌', 'x': '𝓍', 'y': '𝓎', 'z': '𝓏'
            }
            result.append(script_map.get(char, char))
        elif style == "bold_serif":
            # Bold Serif (Times-like bold look)
            bold_map = {
                'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
                'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
                'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
                'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
                'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠',
                'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧',
                'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮',
                'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳'
            }
            result.append(bold_map.get(char, char))
        else:
            result.append(char)
            
    return "".join(result)

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(StyleState.waiting_for_text)
    await message.answer(
        "👋 Приветствую тебя! Я Бот Дизайнер текста.\n\n"
        "Напиши текст, который ты бы хотел украсить:"
    )

@dp.message(StyleState.waiting_for_text)
async def receive_text_handler(message: Message, state: FSMContext) -> None:
    # Save the user's text in FSM storage
    await state.update_data(user_text=message.text)
    await state.set_state(StyleState.waiting_for_style)
    
    # Create inline keyboard with style choices
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="𝖡𝗈𝗅𝖽 𝖲𝖾𝗋𝗂𝖿 (Times Bold)", callback_data="bold_serif")],
        [InlineKeyboardButton(text="𝒞𝓊𝓇𝓈𝒾𝓿ℯ (Script)", callback_data="script")],
        [InlineKeyboardButton(text="𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎 (Typewriter)", callback_data="monospace")]
    ])
    
    await message.answer(
        f"Отлично! Ты отправил:*\"{message.text}\"*\n\nА теперь выбери стиль:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query(StyleState.waiting_for_style, F.data.in_({"bold_serif", "script", "monospace"}))
async def apply_style_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user_text = data.get("user_text", "")
    chosen_style = callback.data
    
    styled_text = apply_style(user_text, chosen_style)
    
    await callback.message.edit_text(
        f"✨ *Вот твой новый текст:*\n\n`{styled_text}`\n\n*(Напиши новый текст, чтобы украсить его снова!)*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Reset state so they can send new text again
    await state.set_state(StyleState.waiting_for_text)
    await callback.answer()

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())