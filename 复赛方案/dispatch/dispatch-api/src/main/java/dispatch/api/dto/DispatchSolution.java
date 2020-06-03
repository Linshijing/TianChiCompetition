package dispatch.api.dto;

import lombok.Data;

import java.util.List;

@Data
public class DispatchSolution {
    private List<CourierPlan> courierPlans;
}
