# 1. Python bazaviy imidjdan boshlaymiz
FROM python:3.10-slim

# 2. Ishchi papkani /app deb nomlaymiz
WORKDIR /app

# 3. requirements.txt faylini konteynerga ko‘chiramiz
COPY requirements.txt .

# 4. Kutubxonalarni o‘rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# 5. Barcha loyihani ko‘chiramiz
COPY . .

# 6. Botni ishga tushiramiz
CMD ["python", "main.py"]
