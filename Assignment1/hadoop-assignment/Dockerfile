FROM apache/hadoop:3.4.1

USER root

# CentOS 7 est EOL : rediriger yum vers vault.centos.org
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* \
    && sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* \
    && yum clean all

# Installer Python 3 + outils
RUN yum install -y curl nc procps-ng python3 \
    && python3 --version \
    && yum clean all \
    && rm -rf /var/cache/yum

USER hadoop

ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin