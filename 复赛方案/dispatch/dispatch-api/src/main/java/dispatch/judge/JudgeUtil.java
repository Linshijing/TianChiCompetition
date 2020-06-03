package dispatch.judge;

import dispatch.api.dto.Location;
import org.joda.time.DateTime;

public class JudgeUtil {
    /**
     * 地球半径
     */
    private static final double RADIUS = 6367000.0;

    /**
     * 导航距离/路面距离 经验系数
     */
    private static final double COEFFICIENT = 1.4;

    /** 经验路面距离 = 球面距离 * 经验系数(1.4) */
    public static double getDistance(Location from, Location to) {
        return greatCircleDistance(from.getLongitude(), from.getLatitude(), to.getLongitude(), to.getLatitude()) * COEFFICIENT;
    }

    /** 简化版球面距离 */
    public static double greatCircleDistance(double lng1, double lat1, double lng2, double lat2) {
        // 经度差值
        double deltaLng = lng2 - lng1;
        // 纬度差值
        double deltaLat = lat2 - lat1;
        // 平均纬度
        double b = (lat1 + lat2) / 2.0;
        // 东西距离
        double x = Math.toRadians(deltaLng) * RADIUS * Math.cos(Math.toRadians(b));
        // 南北距离
        double y = RADIUS * Math.toRadians(deltaLat);
        // 用平面的矩形对角距离公式计算总距离
        return Math.sqrt(x * x + y * y);
    }
}
