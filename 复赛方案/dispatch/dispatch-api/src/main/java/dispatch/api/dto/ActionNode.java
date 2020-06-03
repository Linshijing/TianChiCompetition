package dispatch.api.dto;

import lombok.Data;

@Data
public class ActionNode {
    private String orderId;
    private int actionType;
    private long actionTime;
}
