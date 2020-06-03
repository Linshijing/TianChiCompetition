FROM registry.cn-shanghai.aliyuncs.com/tcc-public/python:3
#FROM registry.cn-shanghai.aliyuncs.com/tcc-public/java:jdk_13.0.2
MAINTAINER annoymous

WORKDIR /

# 根据需要打包，如果你依赖的base image自身没有带jdk，需要你手动打包进去，并且在start.sh中指定$JAVA_HOME
# ADD jdk11.tar.gz /data
# 根据需要打包
#ADD go1.14.1.linux-amd64.tar.gz /data

# 安装JDK13

ENV LANG=en_US.UTF-8
ENV JAVA_HOME=/usr/java/openjdk-13
ENV PATH=/usr/java/openjdk-13/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV JAVA_VERSION=13.0.2
# ENV JAVA_URL=https://download.java.net/java/GA/jdk13.0.2/d4173c853231432d94f001e99d882ca7/8/GPL/openjdk-13.0.2_linux-x64_bin.tar.gz
ENV JAVA_SHA256=acc7a6aabced44e62ec3b83e3b5959df2b1aa6b3d610d58ee45f0c21a7821a71
COPY openjdk.tgz /
RUN echo "$JAVA_SHA256 */openjdk.tgz" | sha256sum -c -;  mkdir -p "$JAVA_HOME";  tar --extract --file /openjdk.tgz --directory "$JAVA_HOME" --strip-components 1;  rm /openjdk.tgz;   ln -sfT "$JAVA_HOME" /usr/java/default;  ln -sfT "$JAVA_HOME" /usr/java/latest; java -Xshare:dump;   java --version;  javac --version


# 根据需要编译你自己的代码，如果是java/python代码，可以本地编译之后copy进image，否则的话，
# 需要在相关linux环境下编译之后copy进运行image，或者直接在下面RUN编译指令
COPY dispatch-demo-py /dispatch-demo-py

# 按照start.sh文件中说明，提供start.sh 脚本
COPY run_py.sh /


RUN cp /run_py.sh /run.sh && pip3 install flask jinja2 numpy pandas scipy scikit-learn==0.22.1 


EXPOSE 8080

RUN chmod u+x /run.sh

CMD ["/bin/bash","/run.sh", "jshell"]
