FROM odoo:18.0
USER root
RUN ln -sf /usr/share/zoneinfo/Europe/Brussels /etc/localtime \
&& echo "Europe/Brussels" > /etc/timezone \
&& dpkg-reconfigure tzdata
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt --break-system-packages
