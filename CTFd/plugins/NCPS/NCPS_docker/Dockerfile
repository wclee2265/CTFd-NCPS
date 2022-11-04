FROM ubuntu:20.04

ENV USER navy

RUN sed -ri 's/archive.ubuntu.com/mirror.kakao.com/g' /etc/apt/sources.list
RUN apt-get update && apt-get install -y net-tools iproute2 netcat dnsutils curl iputils-ping iptables tcpdump openssh-server sudo vim

#replace sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

#set sudo for $USER
 
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
 
#make .ssh
RUN useradd -m $USER
RUN mkdir /home/$USER/.ssh
RUN chown $USER.$USER /home/$USER/.ssh
RUN chmod 700 /home/$USER/.ssh

#set password
RUN echo 'root:root' |chpasswd
RUN echo $USER':'$USER |chpasswd

RUN service ssh start
EXPOSE 22

COPY SCADA_firmware /
RUN chmod +x /SCADA_firmware

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]