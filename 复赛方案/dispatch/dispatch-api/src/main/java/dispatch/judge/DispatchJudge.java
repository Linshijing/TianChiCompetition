package dispatch.judge;

import com.alibaba.fastjson.JSON;
import dispatch.api.DispatchClient;
import dispatch.api.impl.HttpDispatchClientImpl;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.util.HashMap;

@Slf4j
public class DispatchJudge {

    public static void main(String[] args) {

        String directory = "";
        String api = "http://localhost:8080";
        if (args.length > 0) {
            directory = args[0];
            log.error(String.format("Data directory is %s", directory));
        }
        if (args.length > 1) {
            api = args[1];
            log.error(String.format("Api is %s", api));
        }
        File rootDirectory = new File(directory);
        if(!rootDirectory.isDirectory()){
            log.error("Input path must be a directory.");
            System.exit(1);
        }
        File[] dataFiles = rootDirectory.listFiles((f)->f.isDirectory() && f.getName().matches("\\d+"));
        for(File dataFile:dataFiles){
            String orderPath = String.format("%s/%s",dataFile.getAbsolutePath(),"order");
            String courierPath = String.format("%s/%s",dataFile.getAbsolutePath(), "courier");
            DispatchClient dispatchClient = new HttpDispatchClientImpl(api);
            // 从文件读取订单骑士数据
            RawData rawData = new RawData(orderPath, courierPath);

            SequentialJudge sequentialJudge = new SequentialJudge(dispatchClient, rawData);
            sequentialJudge.doDispatch();

            Score score = sequentialJudge.getScore();
            log.error(String.format("AreaId %s overtimeCount: %f", dataFile.getName(), score.getOvertimeCount()));
            log.error(String.format("AreaId %s avgDeliveryTime: %f", dataFile.getName(), score.getAvgServiceTime()));
            if (score.getIllegalMsg().isIllegal()) {
                log.error(String.format("AreaId %s error Msg %s", dataFile.getName(), score.getIllegalMsg().getMsg()));
            }
        }
        //Merge result
    }

}
