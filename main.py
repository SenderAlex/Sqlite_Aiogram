import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import TOKEN
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()


def init_db():
    conn = sqlite3.connect('student_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_data (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()


init_db()


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer('Привет!! Как тебя зовут')
    await state.set_state(Form.name)


@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Сколько тебе лет??')
    await state.set_state(Form.age)


@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('В каком классе ты учишься??')
    await state.set_state(Form.grade)


@dp.message(Form.grade)
async def get_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    student_data = await state.get_data()
    name = student_data['name']
    age = student_data['age']
    grade = student_data['grade']
    conn = sqlite3.connect('student_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO student_data (name, age, grade) VALUES (?, ?, ?)''', (name, age, grade))
    conn.commit()
    conn.close()
    await message.answer('Данные успешно сохранены!')
    await message.answer(f'Вы ввели следующие данные:\n'
                         f'Имя -- <b>{name}</b>\n'
                         f'Возраст -- <b>{age}</b>\n'
                         f'Класс -- <b>{grade}</b>', parse_mode='HTML')


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
