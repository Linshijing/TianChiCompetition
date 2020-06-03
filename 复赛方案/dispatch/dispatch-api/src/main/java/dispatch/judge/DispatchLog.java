package dispatch.judge;

import dispatch.api.dto.DispatchRequest;
import dispatch.api.dto.DispatchSolution;
import lombok.Getter;

@Getter
public class DispatchLog {
    private DispatchRequest request;
    private DispatchSolution solution;

    public DispatchLog(DispatchRequest request, DispatchSolution solution) {
        this.request = request;
        this.solution = solution;
    }
}
