FROM python:3.10

WORKDIR /shop_kz

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

#ENV PYTHONPATH="/shop_kz:$PYTHONPATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]