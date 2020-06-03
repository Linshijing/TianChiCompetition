package dispatch.judge;

import dispatch.api.dto.Order;
import lombok.Data;

@Data
public class OrderRecord {
    private Order order;
    private int status;
    private boolean overTime;
    private Long deliveryTime;

    public OrderRecord(Order order) {
        this.order = order;
        this.status = 0;
    }
}
