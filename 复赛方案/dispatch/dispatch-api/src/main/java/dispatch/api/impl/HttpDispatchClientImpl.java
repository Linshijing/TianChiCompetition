package dispatch.api.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;
import dispatch.api.DispatchClient;
import dispatch.api.dto.DispatchRequest;
import dispatch.api.dto.DispatchSolution;
import dispatch.api.dto.Response;
import dispatch.api.exception.DispatchException;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpStatus;
import org.apache.http.client.config.RequestConfig;

import java.io.Closeable;
import java.io.IOException;

/**
 * @author fangyu.fu
 */
@Data
@Slf4j
public class HttpDispatchClientImpl implements DispatchClient, Closeable {

    private static final String DISPATCH_PATH_V1 = "/api/v1/dispatch";
    private static final String PING_PATH_V1 = "/api/v1/ping";
    private static String DEFAULT_URL = "http://localhost:8080";
    private HttpClientManager httpClientManager;

    public HttpDispatchClientImpl(String url) {
        httpClientManager = new HttpClientManager(url, 5000, 5000,5000,0);
    }

    public HttpDispatchClientImpl() {
        httpClientManager = new HttpClientManager(DEFAULT_URL, 5000, 5000, 5000,  0);
    }

    public HttpDispatchClientImpl(String url, RequestConfig requestConfig, int retry) {
        httpClientManager = new HttpClientManager(url, requestConfig, retry);
    }

    @Override
    public Response<DispatchSolution> dispatch(DispatchRequest dispatchRequest) throws DispatchException {
        try {
            return httpClientManager.post(DISPATCH_PATH_V1, JSON.toJSONString(dispatchRequest), (body) ->
                    JSON.parseObject(body, new TypeReference<Response<DispatchSolution>>() {
                    })
            );
        } catch (Exception e) {
            log.error("", e);
            throw new DispatchException(HttpStatus.SC_INTERNAL_SERVER_ERROR, e.getMessage(), e);
        }
    }

    @Override
    public Response<String> ping() throws DispatchException {
        try {
            return httpClientManager.get(PING_PATH_V1, (body) ->
                    JSON.parseObject(body, new TypeReference<Response<String>>() {
                    })
            );
        } catch (Exception e) {
            log.error("", e);
            throw new DispatchException(HttpStatus.SC_INTERNAL_SERVER_ERROR, e.getMessage(), e);
        }
    }

    @Override
    public void close() throws IOException {
        httpClientManager.close();
    }
}
