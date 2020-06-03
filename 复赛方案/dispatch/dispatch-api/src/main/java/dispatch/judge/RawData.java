package dispatch.judge;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import dispatch.api.dto.Courier;
import dispatch.api.dto.Location;
import dispatch.api.dto.Order;
import lombok.Getter;

import java.io.File;
import java.util.*;

@Getter
public class RawData {

    private String areaId;
    private List<Order> orders;
    private List<Courier> couriers;
    private Map<String, Long> courierOnlineTime;

    public RawData(String orderFilePath, String courierFilePath) {
        this.orders = Lists.newArrayList();
        this.couriers = Lists.newArrayList();
        this.courierOnlineTime = Maps.newHashMap();

        try {
            Scanner orderScanner = new Scanner(new File(orderFilePath));
            orderScanner.nextLine();
            while (orderScanner.hasNextLine()) {
                this.orders.add(orderLine2Order(getRecordFromLine(orderScanner.nextLine())));
            }
            Scanner courierScanner = new Scanner(new File(courierFilePath));
            courierScanner.nextLine();
            while (courierScanner.hasNextLine()) {
                List<String> courierLine = getRecordFromLine(courierScanner.nextLine());
                this.courierOnlineTime.put(courierLine.get(1), Long.parseLong(courierLine.get(2)));
                this.couriers.add(courierLine2Courier(courierLine));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        this.orders.sort(Comparator.comparingLong(Order::getCreateTime));
        this.couriers.sort(Comparator.comparingLong(c -> courierOnlineTime.get(c.getId())));
        this.areaId = orders.get(0).getAreaId();
    }


    private static final String COMMA_DELIMITER = "\t";

    private static List<String> getRecordFromLine(String line) {
        List<String> values = new ArrayList<>();
        try (Scanner rowScanner = new Scanner(line)) {
            rowScanner.useDelimiter(COMMA_DELIMITER);
            while (rowScanner.hasNext()) {
                values.add(rowScanner.next());
            }
        }
        return values;
    }

    private static Order orderLine2Order(List<String> orderLine) {
        return new Order().setAreaId(orderLine.get(0))
                .setId(orderLine.get(1))
                .setCreateTime(Long.parseLong(orderLine.get(2)))
                .setEstimatedPrepareCompletedTime(Long.parseLong(orderLine.get(3)))
                .setPromiseDeliverTime(Long.parseLong(orderLine.get(4)))
                .setSrcLoc(new Location(Double.parseDouble(orderLine.get(5)), Double.parseDouble(orderLine.get(6))))
                .setDstLoc(new Location(Double.parseDouble(orderLine.get(7)), Double.parseDouble(orderLine.get(8))));
    }

    private static Courier courierLine2Courier(List<String> courierLine) {
        return new Courier().setAreaId(courierLine.get(0))
                .setId(courierLine.get(1))
                .setMaxLoads(Integer.parseInt(courierLine.get(3)))
                .setSpeed(Double.parseDouble(courierLine.get(4)))
                .setLoc(new Location(Double.parseDouble(courierLine.get(5)), Double.parseDouble(courierLine.get(6))));
    }

}
