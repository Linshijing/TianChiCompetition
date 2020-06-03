package dispatch.api.dto;

import lombok.Data;
import lombok.experimental.Accessors;

import java.util.List;

@Data
@Accessors(chain = true)
public class DispatchRequest {
    private long requestTime;
    private String areaId;
    private boolean isFirstRound;
    private boolean isLastRound;
    private List<Courier> couriers;
    private List<Order> orders;
}
