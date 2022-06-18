FROM python:3.10.4-alpine3.15

LABEL version="v1.0-rc3"
LABEL description="一个纯粹的库存管理系统"

WORKDIR /ivm

COPY ui ./ui
COPY db ./db
COPY CONFIG.py .
COPY main.py .
COPY Caddyfile .
COPY requirements.txt .

ENV PATH /usr/local/bin:$PATH

RUN apk add --no-cache caddy gcc make g++ zlib-dev libffi-dev\
&& pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir python-multipart python-jose fastapi uvicorn[stander] peewee\
&& apk del gcc make g++ zlib-dev libffi-dev\
&& echo -e "#!/bin/sh\ncd /ivm\nnohup uvicorn main:app --host 0.0.0.0 --port 8000 >/dev/null 2>&1 &\ncaddy run" >> /bootstart.sh\
# && echo -e "#!/bin/sh\ncd /ivm\nnohup uvicorn main:app --host 0.0.0.0 --port 8000 >/dev/null 2>&1 &\nnohup caddy start >/dev/null 2>&1 & /bin/sh" >> /bootstart.sh\
&& chmod +x /bootstart.sh\
&& python3 main.py create\
&& rm -rf ~/.cache/pip\
&& rm -rf /usr/local/lib/python3.10/site-packages/pip\
&& rm -rf /usr/local/lib/python3.10/site-packages/dotenv\
&& rm -rf /usr/local/lib/python3.10/site-packages/setuptools\
&& find /usr/local/lib/python3.10/site-packages/ -name "*.dist-info" | xargs rm -rf
# clean size

ENV IVM_USERNAME=admin
ENV IVM_PASSWORD=998877

EXPOSE 80
CMD [ "/bootstart.sh" ]

