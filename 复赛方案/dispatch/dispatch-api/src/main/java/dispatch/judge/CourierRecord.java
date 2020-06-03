package dispatch.judge;

import com.google.common.collect.Lists;
import dispatch.api.dto.Courier;
import dispatch.api.dto.CourierPlan;
import dispatch.api.dto.Location;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
public class CourierRecord {
    private Courier courier;
    @Setter
    private Location location;
    private Long courierTime;
    private List<CourierPlan> courierPlans;

    public CourierRecord(Courier courier, Long courierTime) {
        this.courier = courier;
        this.location = courier.getLoc();
        this.courierTime = courierTime;
        this.courierPlans = Lists.newArrayList();
    }

    public void timeChange(Long time) {
        if (time > courierTime) {
            courierTime = time;
        }
    }

}
