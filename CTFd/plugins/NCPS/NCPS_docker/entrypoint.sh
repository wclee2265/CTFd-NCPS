#!/bin/sh

#/bin/sh -c "/usr/sbin/sshd -D && /SCADA_firmware 12345 && /bin/sh && tail -f /dev/null" 
sh -c "service ssh start"
sh -c "/SCADA_firmware 12345 & tail -f /dev/null" 