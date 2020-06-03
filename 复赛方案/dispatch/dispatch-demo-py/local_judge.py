import os
import multiprocessing
import app


def run_judge(jar_path, class_path, date_path):
    cmd = "java -cp .:{} {} {}".format(jar_path, class_path, date_path)
    print(cmd)
    os.system(cmd)
    print("end judge.")


if __name__ == '__main__':
    p = multiprocessing.Process(target=app.local_start, kwargs={'port': 8080})
    p.start()
    run_judge("./dispatch-judge-jar-with-dependencies.jar", "dispatch.judge.DispatchJudge", "./open_test")
