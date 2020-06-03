.PHONY: all build build-java build-py build-go build-image build-image-judge clean clean-java clean-py clean-go

NOW=$(shell date '+%Y-%m-%d_%H:%M:%S')
USER=${shell whoami}

all: build

build: build-java build-py build-go build-image build-image-judge

clean: clean-java clean-py clean-go

build-java:
	echo "start build java" && \
	mvn -f pom.xml clean package install -DskipTests && mvn -f dispatch-demo/pom.xml clean package -DskipTests

build-py:
	echo "start build python" && \
	cd dispatch-demo-py && python setup.py build

build-go:
	echo "start build go" && \
	cd dispatch-demo-go && go build

build-image:
	docker build -t registry.cn-shanghai.aliyuncs.com/tcc-public/${USER}:v${NOW} .

build-image-judge:
	docker build -t registry.cn-shanghai.aliyuncs.com/tcc-public/${USER}:v${NOW} -f DockerfileJudge

clean-java:
	mvn clean && mvn clean -f dispatch-demo/pom.xml

clean-py:
	cd dispatch-demo-py && python setup.py clean && rm -rf dispatch_demo_py.egg-info

clean-go:
	cd dispatch-demo-go && go mod tidy && rm -rf dispatch-demo-go

