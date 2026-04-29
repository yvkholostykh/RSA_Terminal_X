#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSA: интерактивный режим с эмодзи и полной поддержкой файлов.
Все файлы сохраняются в папке, где находится скрипт.
"""

import sys
import os
import random
import math

# ------------------------------------------------------------
# Определяем папку, где находится скрипт
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not BASE_DIR:
    BASE_DIR = os.getcwd()

# ------------------------------------------------------------
# Эмодзи
# ------------------------------------------------------------
ICON_STEP = "🔷"
ICON_INPUT = "📥"
ICON_CALC = "🧮"
ICON_KEY = "🔑"
ICON_NUMBER = "🔢"
ICON_LOCK = "🔒"
ICON_UNLOCK = "🔓"
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"
ICON_RESULT = "📋"
ICON_ATTACK = "⚔️"
ICON_FILE = "📄"
ICON_HOURGLASS = "⏳"
ICON_SAVE = "💾"

def print_step(msg):    print(f"{ICON_STEP} {msg}")
def print_input(msg):   print(f"{ICON_INPUT} {msg}")
def print_calc(msg):    print(f"{ICON_CALC} {msg}")
def print_const(msg):   print(f"   {msg}")
def print_result(msg):  print(f"{ICON_SUCCESS} {msg}")
def print_error(msg):   print(f"{ICON_ERROR} {msg}")
def print_key(msg):     print(f"{ICON_KEY} {msg}")
def print_attack(msg):  print(f"{ICON_ATTACK} {msg}")
def print_file(msg):    print(f"{ICON_FILE} {msg}")
def print_save(msg):    print(f"{ICON_SAVE} {msg}")

# ------------------------------------------------------------
# Теоретико-числовые функции
# ------------------------------------------------------------
def egcd(a, b):
    if a == 0: return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"НОД({a},{m})={g} ≠ 1, обратный элемент не существует")
    return x % m

def mod_pow(a, k, n):
    res = 1
    base = a % n
    exp = k
    while exp > 0:
        if exp & 1:
            res = (res * base) % n
        base = (base * base) % n
        exp >>= 1
    return res

# ------------------------------------------------------------
# Проверка простоты (Миллер-Рабин)
# ------------------------------------------------------------
SMALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def is_prime_mr(n, k=20):
    if n < 2: return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    r, d = 0, n-1
    while d % 2 == 0:
        d //= 2; r += 1
    for _ in range(k):
        a = random.randint(2, n-2)
        x = mod_pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for __ in range(r-1):
            x = mod_pow(x, 2, n)
            if x == n-1:
                break
        else:
            return False
    return True

def generate_prime_big(bits):
    if bits < 2:
        raise ValueError("Размер простого числа должен быть не менее 2 бит.")
    while True:
        num = random.getrandbits(bits)
        num |= (1 << bits-1) | 1
        if is_prime_mr(num):
            return num

# ------------------------------------------------------------
# Преобразование текст ↔ число (блоки)
# ------------------------------------------------------------
def text_to_blocks(text, max_bytes):
    data = text.encode('utf-8')
    blocks = []
    for i in range(0, len(data), max_bytes):
        chunk = data[i:i+max_bytes]
        blocks.append(int.from_bytes(chunk, byteorder='big'))
    return blocks

def blocks_to_text(blocks):
    data = b''
    for num in blocks:
        byte_len = (num.bit_length() + 7) // 8
        if byte_len == 0: continue
        data += num.to_bytes(byte_len, byteorder='big')
    return data.decode('utf-8', errors='replace')

# ------------------------------------------------------------
# Работа с файлами (сохранение в папке скрипта)
# ------------------------------------------------------------
def get_full_path(filename):
    return os.path.join(BASE_DIR, filename)

def save_keys(public, private):
    e, n = public
    d, _ = private
    path_pub = get_full_path("public_key.txt")
    path_priv = get_full_path("private_key.txt")
    try:
        with open(path_pub, "w") as f:
            f.write(f"e={e}\nn={n}\n")
        with open(path_priv, "w") as f:
            f.write(f"d={d}\nn={n}\n")
        print_save(f"Ключи сохранены:\n  {path_pub}\n  {path_priv}")
        with open(path_pub, "r") as f:
            content = f.read()
        print_const(f"Содержимое public_key.txt:\n{content.strip()}")
        return True
    except Exception as ex:
        print_error(f"Не удалось сохранить ключи: {ex}")
        print_error(f"Попробуйте сохранить вручную:\n  e={e}\n  n={n}\n  d={d}")
        return False

def load_public_key():
    path = get_full_path("public_key.txt")
    try:
        with open(path, "r") as f:
            lines = f.readlines()
            e = int(lines[0].strip().split('=')[1])
            n = int(lines[1].strip().split('=')[1])
            return (e, n)
    except:
        return None

def load_private_key():
    path = get_full_path("private_key.txt")
    try:
        with open(path, "r") as f:
            lines = f.readlines()
            d = int(lines[0].strip().split('=')[1])
            n = int(lines[1].strip().split('=')[1])
            return (d, n)
    except:
        return None

def save_message(text, filename="message.txt"):
    path = get_full_path(filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print_save(f"Сообщение сохранено: {path}")
        return True
    except Exception as ex:
        print_error(f"Не удалось сохранить сообщение: {ex}")
        return False

def load_message(filename="message.txt"):
    path = get_full_path(filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def save_encrypted(blocks, n, e, filename="encrypted.txt"):
    path = get_full_path(filename)
    try:
        with open(path, 'w') as f:
            f.write(f"# RSA encrypted file\n# n={n}\n# e={e}\n")
            for c in blocks:
                f.write(f"{c}\n")
        print_save(f"Шифртекст сохранён: {path}")
        return True
    except Exception as ex:
        print_error(f"Не удалось сохранить шифртекст: {ex}")
        return False

def load_encrypted(filename="encrypted.txt"):
    path = get_full_path(filename)
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
        blocks = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                blocks.append(int(line))
        return blocks
    except:
        return None

def save_decrypted(text, filename="decrypted.txt"):
    path = get_full_path(filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print_save(f"Расшифрованный текст сохранён: {path}")
        return True
    except Exception as ex:
        print_error(f"Не удалось сохранить расшифрованный текст: {ex}")
        return False

# ------------------------------------------------------------
# Генерация ключей с выбором размера (исправлено)
# ------------------------------------------------------------
def generate_keys_interactive():
    print_step("=== ГЕНЕРАЦИЯ КЛЮЧЕЙ RSA ===")
    print("Выберите способ:")
    print("  1 - Автоматическая генерация (случайные простые числа)")
    print("  2 - Ручной ввод простых чисел p и q")
    mode = input(f"{ICON_INPUT} Ваш выбор (1-2): ").strip()
    
    try:
        if mode == '2':
            while True:
                try:
                    p = int(input(f"{ICON_INPUT} p = "))
                    if not is_prime_mr(p):
                        print_error("p не является простым!")
                        continue
                    break
                except: print_error("Введите целое число.")
            while True:
                try:
                    q = int(input(f"{ICON_INPUT} q = "))
                    if not is_prime_mr(q):
                        print_error("q не является простым!")
                        continue
                    if q == p:
                        print_error("p и q должны быть разными!")
                        continue
                    break
                except: print_error("Введите целое число.")
            n = p * q
            phi = (p-1)*(q-1)
            print_const(f"p = {p}, q = {q}")
            print_const(f"n = {n}, φ(n) = {phi}")
        else:
            print_step("Выберите размер простых чисел в битах:")
            print("  1 → 128 бит (учебный, небезопасный)")
            print("  2 → 256 бит")
            print("  3 → 512 бит (рекомендуется для тестов)")
            print("  4 → 1024 бит")
            print("  5 → 2048 бит (рекомендуется для реального использования)")
            print("  6 → свой размер")
            size_choice = input(f"{ICON_INPUT} Ваш выбор (1-6): ").strip()
            if size_choice == '1':
                bits = 128
            elif size_choice == '2':
                bits = 256
            elif size_choice == '3':
                bits = 512
            elif size_choice == '4':
                bits = 1024
            elif size_choice == '5':
                bits = 2048
            elif size_choice == '6':
                while True:
                    try:
                        bits = int(input(f"{ICON_INPUT} Введите размер в битах (мин 32, макс 4096): "))
                        if bits < 32:
                            print_error("Размер не может быть меньше 32 бит.")
                        elif bits > 4096:
                            print_error("Размер не может быть больше 4096 бит (слишком долго).")
                        else:
                            break
                    except:
                        print_error("Введите целое число.")
            else:
                bits = 512
                print_const("Используем размер 512 бит по умолчанию.")
            
            print_step(f"Генерация {bits}-битных простых чисел... {ICON_HOURGLASS}")
            p = generate_prime_big(bits)
            q = generate_prime_big(bits)
            while abs(p - q) < 2**(bits//2):
                q = generate_prime_big(bits)
            n = p * q
            phi = (p-1)*(q-1)
            print_const(f"p = {p}")
            print_const(f"q = {q}")
            print_const(f"n = {n} (бит = {n.bit_length()})")
        
        # Выбор экспоненты e
        print_step("Выберите экспоненту e:")
        print("  1 → 65537 (рекомендуется)\n  2 → 17\n  3 → 3\n  4 → ввести свою")
        choice = input(f"{ICON_INPUT} Ваш выбор (1-4): ").strip()
        if choice == '1': e = 65537
        elif choice == '2': e = 17
        elif choice == '3': e = 3
        elif choice == '4':
            while True:
                try:
                    e = int(input(f"{ICON_INPUT} Введите e (целое >1): "))
                    if e <= 1:
                        print_error("e должно быть больше 1!")
                        continue
                    break
                except:
                    print_error("Введите целое число больше 1.")
        else: e = 65537
        
        if math.gcd(e, phi) != 1:
            print_error(f"e = {e} не взаимно просто с φ(n) = {phi}. Подбираем подходящее...")
            found = False
            for candidate in [65537, 257, 17, 3]:
                if math.gcd(candidate, phi) == 1:
                    e = candidate
                    print_const(f"Используем e = {e}")
                    found = True
                    break
            if not found:
                while True:
                    e = random.randrange(2, phi)
                    if math.gcd(e, phi) == 1:
                        break
                print_const(f"Используем случайное e = {e}")
        print_key(f"Экспонента шифрования e = {e}")
        
        print_calc("Вычисляем d = e⁻¹ mod φ(n)...")
        d = modinv(e, phi)
        print_key(f"Закрытый ключ d = {d}")
        print_const(f"Проверка: e·d = {e*d} ≡ 1 mod {phi}")
        
        public = (e, n)
        private = (d, n)
        save_keys(public, private)
        return public, private
    except Exception as ex:
        print_error(f"Ошибка при генерации ключей: {ex}")
        return None, None

# ------------------------------------------------------------
# ИНТЕРАКТИВНЫЙ РУЧНОЙ РЕЖИМ (без изменений, но использует новые функции)
# ------------------------------------------------------------
def interactive_manual_mode():
    print_step("=== РЕЖИМ РУЧНОГО ВВОДА (ПОШАГОВОЕ РЕШЕНИЕ) ===")
    try:
        print("Хотите загрузить ранее сохранённые ключи из файлов? (y/n)")
        load_choice = input().strip().lower()
        if load_choice == 'y':
            pub = load_public_key()
            priv = load_private_key()
            if pub and priv:
                e, n = pub
                d, _ = priv
                print_key(f"Загружены ключи: e={e}, n={n}, d={d}")
            else:
                print_error("Не удалось загрузить ключи. Будем вводить вручную.")
                pub = None
        else:
            pub = None
        
        if not pub:
            print_step("Шаг 1. Введите два простых числа p и q (разные).")
            while True:
                try:
                    p = int(input(f"{ICON_INPUT} p = "))
                    if not is_prime_mr(p):
                        print_error("p не является простым!")
                        continue
                    break
                except: print_error("Введите целое число.")
            while True:
                try:
                    q = int(input(f"{ICON_INPUT} q = "))
                    if not is_prime_mr(q):
                        print_error("q не является простым!")
                        continue
                    if q == p:
                        print_error("p и q должны быть разными!")
                        continue
                    break
                except: print_error("Введите целое число.")
            print_const(f"p = {p}, q = {q}")
            n = p * q
            phi = (p-1)*(q-1)
            print_calc(f"n = {n}, φ(n) = {phi}")
            
            print_step("Шаг 2. Выберите экспоненту e (взаимно простую с φ(n)).")
            print("  1 → 65537\n  2 → 17\n  3 → 3\n  4 → ввести свою")
            choice = input(f"{ICON_INPUT} Ваш выбор (1-4): ").strip()
            if choice == '1': e = 65537
            elif choice == '2': e = 17
            elif choice == '3': e = 3
            elif choice == '4':
                while True:
                    try:
                        e = int(input(f"{ICON_INPUT} Введите e (целое >1): "))
                        if e <= 1:
                            print_error("e должно быть больше 1!")
                            continue
                        break
                    except:
                        print_error("Введите целое число больше 1.")
            else: e = 65537
            
            if math.gcd(e, phi) != 1:
                print_error(f"e = {e} не взаимно просто с φ(n) = {phi}. Подбираем подходящее...")
                found = False
                for candidate in [65537, 257, 17, 3]:
                    if math.gcd(candidate, phi) == 1:
                        e = candidate
                        print_const(f"Используем e = {e}")
                        found = True
                        break
                if not found:
                    while True:
                        e = random.randrange(2, phi)
                        if math.gcd(e, phi) == 1:
                            break
                    print_const(f"Используем случайное e = {e}")
            print_key(f"e = {e}")
            
            print_step("Шаг 3. Вычисляем d = e⁻¹ mod φ(n).")
            d = modinv(e, phi)
            print_key(f"d = {d}")
            print_const(f"Проверка: e·d = {e*d} ≡ 1 mod {phi}")
            save_keys((e, n), (d, n))
        else:
            e, n = pub
            d, _ = priv
        
        print_step("Шаг 4. Введите сообщение (целое число) или загрузите из файла message.txt.")
        print("  1 - ввести число вручную")
        print("  2 - загрузить из message.txt (преобразовать текст в число)")
        msg_choice = input(f"{ICON_INPUT} Ваш выбор (1-2): ").strip()
        if msg_choice == '2':
            text = load_message("message.txt")
            if text:
                max_bytes = (n.bit_length() - 1) // 8
                if max_bytes < 1:
                    print_error("Модуль слишком мал для преобразования текста.")
                    return
                blocks = text_to_blocks(text, max_bytes)
                if len(blocks) > 1:
                    print_error("Сообщение слишком длинное для одного блока. Используйте шифрование файлов.")
                    return
                m = blocks[0]
                print_const(f"Загружено сообщение: '{text}' -> число m = {m}")
            else:
                print_error("Файл message.txt не найден.")
                return
        else:
            while True:
                try:
                    m = int(input(f"{ICON_INPUT} m = "))
                    if m >= n:
                        print_error(f"m должно быть меньше {n}")
                        continue
                    break
                except: print_error("Введите целое число.")
            save_message(str(m), "message.txt")
        
        print_const(f"Исходное сообщение: m = {m}")
        
        print_step("Шаг 5. Шифрование: c = m^e mod n.")
        print_calc(f"Вычисляем {m}^{e} mod {n} ...")
        c = mod_pow(m, e, n)
        print_const(f"{ICON_LOCK} Шифртекст: c = {c}")
        save_encrypted([c], n, e, "encrypted.txt")
        
        print_step("Шаг 6. Расшифрование: m' = c^d mod n.")
        print_calc(f"Вычисляем {c}^{d} mod {n} ...")
        m_dec = mod_pow(c, d, n)
        print_const(f"{ICON_UNLOCK} Расшифрованное сообщение: m' = {m_dec}")
        save_decrypted(str(m_dec), "decrypted.txt")
        
        if m == m_dec:
            print_result("УСПЕХ: сообщения совпадают.")
        else:
            print_error("ОШИБКА: не совпадают!")
        
        print_step("\n=== ИТОГОВЫЕ ДАННЫЕ ===")
        print_key(f"Открытый ключ: (e, n) = ({e}, {n})")
        print_key(f"Закрытый ключ: d = {d}")
        print_const(f"Исходное сообщение (число): {m}")
        print_const(f"Шифртекст (число): {c}")
        print_const(f"Расшифрованное сообщение (число): {m_dec}")
    except Exception as ex:
        print_error(f"Произошла ошибка: {ex}")
        print_error("Пожалуйста, проверьте введённые данные и попробуйте снова.")
        return

# ------------------------------------------------------------
# Остальные функции (encrypt_file_mode, decrypt_file_mode, create_test_message, view_all_files, cube_root_attack_demo, print_menu, main)
# ------------------------------------------------------------
def encrypt_file_mode(public_key):
    if not public_key:
        print_error("Открытый ключ не загружен.")
        return
    e, n = public_key
    infile = input(f"{ICON_FILE} Имя файла с открытым текстом (message.txt): ").strip()
    if not infile:
        infile = "message.txt"
    full_in = get_full_path(infile)
    if not os.path.exists(full_in):
        print_error(f"Файл {full_in} не найден.")
        return
    outfile = input(f"{ICON_FILE} Имя файла для шифртекста (encrypted.txt): ").strip()
    if not outfile:
        outfile = "encrypted.txt"
    
    try:
        with open(full_in, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        max_bytes = (n.bit_length() - 1) // 8
        if max_bytes < 1:
            print_error("Модуль n слишком мал.")
            return
        blocks = text_to_blocks(plaintext, max_bytes)
        encrypted = [mod_pow(m, e, n) for m in blocks]
        save_encrypted(encrypted, n, e, outfile)
        print_result(f"Файл {full_in} зашифрован в {get_full_path(outfile)}")
    except Exception as ex:
        print_error(f"Ошибка при шифровании: {ex}")

def decrypt_file_mode(private_key):
    if not private_key:
        print_error("Закрытый ключ не загружен.")
        return
    d, n = private_key
    infile = input(f"{ICON_FILE} Имя файла с шифртекстом (encrypted.txt): ").strip()
    if not infile:
        infile = "encrypted.txt"
    full_in = get_full_path(infile)
    if not os.path.exists(full_in):
        print_error(f"Файл {full_in} не найден.")
        return
    outfile = input(f"{ICON_FILE} Имя файла для расшифрованного текста (decrypted.txt): ").strip()
    if not outfile:
        outfile = "decrypted.txt"
    
    try:
        encrypted = load_encrypted(infile)
        if encrypted is None:
            print_error("Ошибка чтения шифртекста.")
            return
        decrypted = [mod_pow(c, d, n) for c in encrypted]
        plaintext = blocks_to_text(decrypted)
        save_decrypted(plaintext, outfile)
        print_result(f"Файл {full_in} расшифрован в {get_full_path(outfile)}")
    except Exception as ex:
        print_error(f"Ошибка при расшифровании: {ex}")

def create_test_message():
    filename = "message.txt"
    print_step(f"Редактирование {filename}")
    print("Введите текст сообщения (можно несколько строк). Пустая строка или 'END' - завершить.")
    lines = []
    while True:
        line = input()
        if line == "" or line == "END":
            break
        lines.append(line)
    if lines:
        text = "\n".join(lines)
        save_message(text, filename)
    else:
        print_error("Файл не изменён.")

def view_file(filename):
    path = get_full_path(filename)
    if not os.path.exists(path):
        print_error(f"Файл {path} не найден.")
        return
    print(f"\n--- {path} ---")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as ex:
        print_error(f"Не удалось прочитать файл: {ex}")
    print("--- конец ---")

def view_all_files():
    files = ["public_key.txt", "private_key.txt", "message.txt", "encrypted.txt", "decrypted.txt"]
    for fname in files:
        view_file(fname)

def cube_root_attack_demo():
    print_attack("=== АТАКА CUBE ROOT (малая экспонента e=3) ===")
    try:
        c = int(input(f"{ICON_INPUT} Шифртекст c (число): "))
        e = int(input(f"{ICON_INPUT} Экспонента e (обычно 3): ") or "3")
        print_calc(f"Извлекаем корень {e}-й степени из {c}...")
        low, high = 1, 2
        while high**e < c:
            high *= 2
        iterations = 0
        found = None
        while low <= high:
            iterations += 1
            mid = (low + high) // 2
            power = mid**e
            if power == c:
                found = mid
                break
            elif power < c:
                low = mid + 1
            else:
                high = mid - 1
        if found is not None:
            print_result(f"Атака успешна! Восстановлено m = {found}")
            try:
                byte_len = (found.bit_length() + 7) // 8
                text = found.to_bytes(byte_len, 'big').decode('utf-8')
                print_const(f"Как текст (UTF-8): {text}")
            except:
                pass
        else:
            print_error("Атака не удалась.")
        print_const(f"Итераций: {iterations}")
    except Exception as ex:
        print_error(f"Ошибка: {ex}")

def print_menu():
    print("\n" + "="*60)
    print("🔐 RSA КРИПТОСИСТЕМА 🔐")
    print("1. 🧑‍💻 Интерактивный ручной режим (с сохранением в файлы)")
    print("2. 🔑 Сгенерировать новую ключевую пару")
    print("3. 📂 Загрузить ключи из файлов")
    print("4. 🔒 Зашифровать файл (message.txt -> encrypted.txt)")
    print("5. 🔓 Расшифровать файл (encrypted.txt -> decrypted.txt)")
    print("6. 📝 Создать/редактировать message.txt")
    print("7. 👁️ Просмотреть все файлы")
    print("8. ⚔️ Атака Cube root")
    print("0. 🚪 Выход")

def main():
    public_key = None
    private_key = None
    
    while True:
        print_menu()
        choice = input(f"{ICON_INPUT} Ваш выбор: ").strip()
        
        if choice == '1':
            interactive_manual_mode()
            input("\n🔷 Нажмите Enter для продолжения...")
        elif choice == '2':
            public_key, private_key = generate_keys_interactive()
            input("🔷 Нажмите Enter...")
        elif choice == '3':
            public_key = load_public_key()
            private_key = load_private_key()
            if public_key and private_key:
                print_result("Ключи загружены.")
            else:
                print_error("Не удалось загрузить ключи.")
            input("🔷 Нажмите Enter...")
        elif choice == '4':
            if not public_key:
                print_error("Сначала загрузите или сгенерируйте открытый ключ.")
            else:
                encrypt_file_mode(public_key)
            input("🔷 Нажмите Enter...")
        elif choice == '5':
            if not private_key:
                print_error("Сначала загрузите или сгенерируйте закрытый ключ.")
            else:
                decrypt_file_mode(private_key)
            input("🔷 Нажмите Enter...")
        elif choice == '6':
            create_test_message()
            input("🔷 Нажмите Enter...")
        elif choice == '7':
            view_all_files()
            input("🔷 Нажмите Enter...")
        elif choice == '8':
            cube_root_attack_demo()
            input("🔷 Нажмите Enter...")
        elif choice == '0':
            print("👋 До свидания!")
            break
        else:
            print_error("Неверный выбор.")
            input("🔷 Нажмите Enter...")

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    main()