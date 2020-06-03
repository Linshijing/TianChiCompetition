package dispatch.judge;

import lombok.Data;

@Data
public class Score {
    private IllegalMsg illegalMsg = new IllegalMsg();
    private double avgServiceTime;
    private double overtimeCount;
    private long serviceTimeSum;
    private long orderSum;

    public void setIllegalMsg(IllegalMsg illegalMsg) {
        this.illegalMsg = illegalMsg;
    }

    public void setIllegalMsg(String illegalMsg) {
        this.illegalMsg = new IllegalMsg(illegalMsg);
    }

}
