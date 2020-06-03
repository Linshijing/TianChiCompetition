package dispatch.api.dto;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class Order {
    private String areaId;
    private String id;
    private Location srcLoc;
    private Location dstLoc;
    private long createTime;
    private long promiseDeliverTime;
    private long estimatedPrepareCompletedTime;

}
