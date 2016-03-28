#!/bin/bash
#===============================================================================
#
#          FILE: sys_env_install
# 
#         USAGE: ./sys_env_install
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: xiaobo_l (), xiaobol9527@gmail.com
#  ORGANIZATION: 
#       CREATED: 04/30/2014 16:24:08 
#      REVISION:  ---
#===============================================================================

set -o nounset
set -o errexit


function stop_service() {
service=$(chkconfig --list |perl -alne 'print $F[0] if $F[4] eq "3:on" && $F[0] !~ m/^(crond|network|sshd|rsyslog|postfix|irqbalance|microcode_ctl|random|smartd)$/')

for i in $service 
do
chkconfig $i off
done
if [ ${os_version} -eq 7 ]
then 
systemctl stop firewalld
systemctl disable firewalld
#systemctl stop iptables
#systemctl disable iptables
fi
}

function set_file_and_tcp_option() {

if [ ${os_version} -eq 7 ]
then
cat >>/etc/systemd/system.conf<<EOF
DefaultLimitNOFILE=102400
DefaultLimitNPROC=102400
EOF
fi

cat >>/etc/security/limits.conf<<EOF
* soft nproc 102400
* hard nproc 102400
* soft nofile 102400
* hard nofile 102400
EOF


cat >>/etc/sysctl.conf<<EOF



#-----------------------------------------------
net.ipv4.netfilter.ip_conntrack_max = 131072
net.ipv4.tcp_max_tw_buckets = 5000
net.ipv4.tcp_sack = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_rmem = 4096        87380   4194304
net.ipv4.tcp_wmem = 4096        16384   4194304

net.ipv4.tcp_max_syn_backlog = 65536
net.core.netdev_max_backlog =  32768
net.core.somaxconn = 32768

net.core.wmem_default = 8388608
net.core.rmem_default = 8388608
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 2

net.ipv4.tcp_tw_recycle = 1
#net.ipv4.tcp_tw_len = 1
net.ipv4.tcp_tw_reuse = 1

net.ipv4.tcp_mem = 94500000 915000000 927000000
net.ipv4.tcp_max_orphans = 3276800

net.ipv4.tcp_tw_recycle = 1
#net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200

#net.ipv4.tcp_keepalive_time = 300
net.ipv4.ip_local_port_range = 1024    65000

vm.swappiness = 1
EOF
}

function set_sshd() {
#set key login
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
if [ ! -d /root/.ssh ] 
then
mkdir /root/.ssh -p
fi
cat >>/root/.ssh/authorized_keys<<EOF
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAIEAw+d2Rbl082jjJO0SLMm1OVBXojPLpM2gCuDnMSCzdlruqHy+j7qWtG0OAjJCi9owARYQelpRVYSuqIQLngk3jLrq5wH8aqO3Nj7B0EttyCgzWL89D/xfsvmQxYbV5UWan+bPvM2xHbiHVH41VnVNkMTkRcFEZcA4yhuAmzU4Oik= chenjianbin
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCjYj5QvyeshJyqd603XBhu7mTfLXQZILieI7GZSWpMfawN+U0LoXkQwulM2m6qiyBtVNtr829MhfTZNo8utKS7RJ3BuUJzNWGHuaXJLyMEGxeOqFudUoCt7cDoeI4UNa3MYoRfC1yBLE2HlUl3CXVIGfrgZSq1t97QFlLkeM20aB0npWndt6eur7HJYJPfa+PL0Aupg1b9EodLOzuOt0j2A0nKLwJByBfyorCoooX7dEFy1JtTrkJ5J9YVOI53mdI89HqvOz+of8Sarm+DPWOgnvMHnkVBc3y4zpidOv/uyqDbYKmEinjEoH40Aeenw1RLlkof4BM8eeJbKq9lMxUJ linxiaobo
EOF
if [ ${os_version} -eq 7 ]
then
systemctl restart sshd
else
/etc/init.d/sshd restart
fi
}


function set_repo() {
#install rpmforege epel
yum -y install wget
mv  /etc/yum.repos.d/* /tmp

#set basic repo
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-${os_version}.repo


epel_file=epel-release-latest-${os_version}.noarch.rpm
wget http://mirrors.aliyun.com/epel/${epel_file}
rpm -ivh ${epel_file}  --force
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-${os_version}.repo


rpmforge_file=rpmforge-release-0.5.3-1.el${os_version}.rf.`uname -p`.rpm
wget http://pkgs.repoforge.org/rpmforge-release/${rpmforge_file}
rpm -ivh ${rpmforge_file}  --force
}

function base_soft_install() {
#install basic software
yum -y install \
ntp vim-enhanced sysstat gcc gcc-c++ gcc-g77 \
make automake autoconf glibc glibc-devel glib2 glib2-devel \
irqbalance microcode_ctl smartmontools 

yum -y install \
net-tools rsync subversion screen strace numactl psmisc lsof lrzsz


#install monitor
yum -y install iptraf nload iftop iotop dstat

#install python
yum -y install python-pip python-simplejson

#install perl 
yum -y install perl-DBI perl-DBD-MySQL perl-Config-Tiny perl-ExtUtils-MakeMaker perl-CPAN perl-App-cpanminus
}


function set_time() {
#set timezone
rm -f /etc/localtime
cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
set +o errexit
/usr/sbin/ntpdate ntp.api.bz
/usr/sbin/hwclock -w
echo "15 2 * * * root /usr/sbin/ntpdate ntp.api.bz > /dev/null 2>&1;/usr/sbin/hwclock -w > /dev/null 2>&1" >> /etc/crontab
set -o errexit
}

function set_ifname() {
if [ ${os_version} -eq 7 ]
then
sed -i '6 s/"$/ net.ifnames=0 biosdevname=0"/' /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg
fi
}

function set_nameserver(){
echo "nameserver 218.85.152.99">>/etc/resolv.conf
echo "nameserver 218.85.157.99">>/etc/resolv.conf
if [ ${os_version} -eq 7 ]
then
        echo "dns=none">>/etc/NetworkManager/NetworkManager.conf
        systemctl restart NetworkManager.service
fi
}

function set_others(){
#diable selinux
perl -pe 's/^SELINUX=.*/SELINUX=disabled/' -i /etc/selinux/config

if [ ${os_version} -eq 7 ]
then
        chmod +x /etc/rc.d/rc.local
fi
}

tmp_path=/tmp/sys_env_install

[ -d $tmp_path ] && rm -rf $tmp_path
mkdir -p $tmp_path
cd $tmp_path

os_version=$(uname -r |grep -oP '(?<=el)\d*')

set_nameserver
set_repo
set_sshd
base_soft_install
set_time
stop_service
set_file_and_tcp_option
set_others
#set_ifname


#system update
yum -y update

echo
echo
echo
echo
echo
echo '------------------------------------------------------'
echo 'install success!'
echo '------------------------------------------------------'