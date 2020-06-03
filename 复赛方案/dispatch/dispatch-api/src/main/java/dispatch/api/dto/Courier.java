package dispatch.api.dto;

import lombok.Data;
import lombok.experimental.Accessors;


@Data
@Accessors(chain = true)
public class Courier {
    private String areaId;
    private String id;
    private Location loc;
    private Double speed;
    private Integer maxLoads;
}
