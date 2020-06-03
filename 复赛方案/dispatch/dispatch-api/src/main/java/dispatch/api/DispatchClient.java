package dispatch.api;

import dispatch.api.dto.DispatchRequest;
import dispatch.api.dto.DispatchSolution;
import dispatch.api.dto.Response;
import dispatch.api.exception.DispatchException;

import java.io.Closeable;

/**
 * @author fangyu.fu
 */
public interface DispatchClient extends Closeable {
    Response<DispatchSolution> dispatch(DispatchRequest dispatchRequest) throws DispatchException;

    Response<String> ping() throws DispatchException;
}
