package dispatch.api.dto;

import lombok.Data;

import java.util.List;

@Data
public class CourierPlan {
    private String courierId;
    private List<ActionNode> planRoutes;
}
