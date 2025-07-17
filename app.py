from fastapi import FastAPI, HTTPException
import httpx
import os
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import PlainTextResponse
from asyncio import create_task, gather, get_event_loop, sleep
from fastapi.staticfiles import StaticFiles


fastapi_app = FastAPI()
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
HF_TOKEN = os.getenv("HF_TOKEN")  # Токен из переменных окружения
PRIVATE_SPACE_URL = str(os.getenv("LINK"))
CORRECT_PASSWORD = os.getenv("PASS")

@fastapi_app.get('/', response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница ввода пароля"""
    login_html = """
    <!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows Vista - Вход в систему</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600&display=swap">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            background: linear-gradient(135deg, #0c5a9d, #2a8ac4, #3eb7e5);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            position: relative;
        }

        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.4) 0%, transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(173, 216, 230, 0.3) 0%, transparent 40%);
            z-index: 0;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .login-container {
            background: rgba(255, 255, 255, 0.22);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2),
                        inset 0 0 15px rgba(255, 255, 255, 0.6);
            padding: 40px;
            width: 360px;
            text-align: center;
            z-index: 10;
            position: relative;
            overflow: hidden;
            transform: translateY(0);
            transition: transform 0.3s ease;
        }

        .login-container::before {
            content: "";
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: linear-gradient(45deg,
                rgba(255, 255, 255, 0.1) 0%,
                rgba(255, 255, 255, 0) 30%,
                rgba(255, 255, 255, 0.1) 70%,
                rgba(255, 255, 255, 0) 100%);
            z-index: -1;
        }

        .user-icon {
        width: 100px;
        height: 100px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg,
            rgba(160, 230, 255, 0.9) 0%,
            rgba(100, 200, 255, 0.7) 50%,
            rgba(70, 150, 250, 0.8) 100%
            );
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow:
                0 5px 25px rgba(100, 200, 255, 0.6),
                inset 0 0 15px rgba(255, 255, 255, 0.8),
                inset 0 0 30px rgba(255, 255, 255, 0.4),
                inset 0 8px 15px rgba(0, 0, 0, 0.3); /* Тень вдавленности */
            position: relative;
            overflow: hidden;
            border: 2px solid rgba(255, 255, 255, 0.6);
        }

        .user-icon::before {
            content: "";
            position: absolute;
            top: -10%;
            left: -10%;
            width: 50%;
            height: 40%;
            background: radial-gradient(
                circle at center,
                rgba(255, 255, 255, 0.9) 0%,
                rgba(255, 255, 255, 0) 80%
            );
            border-radius: 50%;
            z-index: 2;
            transform: rotate(25deg);
            pointer-events: none;
            opacity: 0.7; /* Снижаем интенсивность */
        }

        .user-icon::after {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(
                circle at 25% 25%,
                rgba(255, 255, 255, 0.3) 0%,
                rgba(255, 255, 255, 0) 60%
            );
            z-index: 1;
            pointer-events: none;
        }

        .suiseiseki {
            width: 84px;
            height: 84px;
            border-radius: 50%;
            position: relative;
            z-index: 0;
            filter:
                brightness(1.05)
                saturate(1.2)
                drop-shadow(0 2px 3px rgba(0,0,0,0.2)); /* Тень под изображением */
            transform: translateY(1px); /* Сдвиг вниз для эффекта вдавленности */
            transition: transform 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3); /* Граница для отделения от стекла */
        }

        /* Эффект при наведении */
        .user-icon:hover .suiseiseki {
            transform: translateY(0px); /* Поднимаем при наведении */
        }

        .user-icon:hover::before {
            transform: rotate(25deg) translate(3px, 3px);
        }

        h1 {
            color: #fff;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
            font-weight: 300;
            font-size: 24px;
            letter-spacing: 0.5px;
        }

        .input-container {
            position: relative;
            margin-bottom: 25px;
        }

        input[type="password"] {
            width: 100%;
            padding: 14px 20px 14px 45px;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            font-size: 16px;
            color: #2a4e6c;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1),
                        inset 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="password"]:focus {
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 0 0 2px rgba(70, 130, 230, 0.4),
                        0 6px 15px rgba(0, 0, 0, 0.15);
        }

        .input-container::before {
            content: "🔒";
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            color: #4a6ea9;
            opacity: 0.8;
        }

        button {
            background: linear-gradient(to bottom, #4b6bc6, #3a56b0);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.4);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        button:hover {
            background: linear-gradient(to bottom, #5a7bd6, #4965c0);
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.5);
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(1px);
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        button::after {
            content: "";
            position: absolute;
            top: -50%;
            left: -60%;
            width: 20px;
            height: 200%;
            background: rgba(255, 255, 255, 0.2);
            transform: rotate(25deg);
            transition: all 0.7s;
        }

        button:hover::after {
            left: 120%;
        }

        .footer {
            margin-top: 25px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }

        .bubble {
            position: absolute;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 50%;
            z-index: 1;
            animation: float 15s infinite ease-in-out;
        }

        .bubble:nth-child(1) {
            width: 120px;
            height: 120px;
            top: 15%;
            left: 10%;
        }

        .bubble:nth-child(2) {
            width: 80px;
            height: 80px;
            top: 65%;
            left: 80%;
            animation-delay: -5s;
        }

        .bubble:nth-child(3) {
            width: 180px;
            height: 180px;
            top: 75%;
            left: 15%;
            animation-delay: -8s;
        }

        .bubble:nth-child(4) {
            width: 100px;
            height: 100px;
            top: 20%;
            left: 85%;
            animation-delay: -12s;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) translateX(0) rotate(0deg); }
            25% { transform: translateY(-50px) translateX(40px) rotate(10deg); }
            50% { transform: translateY(30px) translateX(-40px) rotate(-5deg); }
            75% { transform: translateY(-30px) translateX(-30px) rotate(5deg); }
        }

        .shine {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                to right,
                rgba(255, 255, 255, 0) 20%,
                rgba(255, 255, 255, 0.03) 50%,
                rgba(255, 255, 255, 0) 80%
            );
            transform: rotate(30deg);
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>
    <div class="bubble"></div>

    <div class="login-container">
        <div class="shine"></div>
        <div class="user-icon"><img src="static/suiseiseki.jpg" alt="Перс" class = "suiseiseki"></div>
        <h1>Доступ ограничен</h1>
        <form action="/login" method="POST">
            <div class="input-container">
                <input type="password" name="password" placeholder="Введите пароль" required>
            </div>
            <button type="submit">Войти</button>
        </form>
        <div class="footer">Windows Vista © 2007 Microsoft Corporation</div>
    </div>

    <script>
        // Простая анимация блеска при загрузке
        document.addEventListener('DOMContentLoaded', () => {
            const shine = document.querySelector('.shine');
            setTimeout(() => {
                shine.style.transition = 'transform 1.2s ease';
                shine.style.transform = 'translateX(100%)';
            }, 500);

            // Анимация появления контейнера
            const container = document.querySelector('.login-container');
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';

            setTimeout(() => {
                container.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 300);
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=login_html)

@fastapi_app.post('/login')
async def login(password: str = Form(...)):
    """Проверка пароля и установка куки"""
    if password == CORRECT_PASSWORD:
        response = RedirectResponse(url='/protected', status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_granted", value="true", httponly=True)
        return response
    return RedirectResponse(url='/?error=1', status_code=status.HTTP_303_SEE_OTHER)

@fastapi_app.get('/protected', response_class=HTMLResponse)
async def protected_page(request: Request):
    """Защищенная страница"""
    # Проверка доступа
    if request.cookies.get("access_granted") != "true":
        return RedirectResponse(url='/')
    headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }
    # Загружаем HTML из приватного Space
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                PRIVATE_SPACE_URL,
                headers=headers
            )
            response.raise_for_status()
            html_content = response.text
        except:
            """
            <!DOCTYPE html>
                <html lang="ru">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Ошибочка</title>
                </head>
                <body>
                    ошибочка
                </body>
                </html>
            """

    # Возвращаем HTML напрямую
    return HTMLResponse(content=html_content, status_code=200)
