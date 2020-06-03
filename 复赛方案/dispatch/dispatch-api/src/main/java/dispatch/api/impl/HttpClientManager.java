package dispatch.api.impl;

import lombok.Setter;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpHost;
import org.apache.http.client.HttpClient;
import org.apache.http.client.HttpRequestRetryHandler;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.conn.routing.HttpRoute;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.DefaultHttpRequestRetryHandler;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.protocol.HttpContext;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.util.function.Function;

/**
 * @author fangyu.fu
 */
@Slf4j
public class HttpClientManager {
    private static final String LEFT_SLASH = "/";
    private PoolingHttpClientConnectionManager connectionManager;
    private HttpClientBuilder httpBuilder;
    private RequestConfig requestConfig;
    @Setter
    private int maxConnection = 10;
    @Setter
    private String hostPort = "http://localhost:8080";

    private HttpRequestRetryHandler myRetryHandler = new HttpRequestRetryHandler() {
        @Override
        public boolean retryRequest(IOException exception,
                                    int executionCount, HttpContext context) {
            return false;
        }};

    private HttpRequestRetryHandler requestRetryHandler = myRetryHandler;

    public HttpClientManager(String hostPort, RequestConfig requestConfig) {
        this(hostPort, requestConfig, 0);
    }

    public HttpClientManager(String hostPort, RequestConfig requestConfig, int retry) {
        this.hostPort = hostPort;
        this.requestConfig = requestConfig;

        if (hostPort.endsWith(LEFT_SLASH)) {
            this.hostPort = hostPort.substring(0, hostPort.length() - 1);
        }
        HttpHost target = new HttpHost(this.hostPort);
        connectionManager = new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(maxConnection);
        connectionManager.setDefaultMaxPerRoute(maxConnection);
        connectionManager.setMaxPerRoute(new HttpRoute(target), maxConnection);
        httpBuilder = HttpClients.custom();
        httpBuilder.setConnectionManager(connectionManager);
        if (retry > 0) {
            requestRetryHandler = new DefaultHttpRequestRetryHandler(retry, false);
            httpBuilder.setRetryHandler(requestRetryHandler);
        }else{
            httpBuilder.setRetryHandler(myRetryHandler);
        }
    }

    public HttpClientManager(String hostPort, int connectionTimeInMillis, int readTimeInMillis,
                             int connectionRequestTimeInMillis, int retry) {
        this(hostPort, RequestConfig.custom()
                .setSocketTimeout(readTimeInMillis)
                .setConnectTimeout(connectionTimeInMillis)
                .setConnectionRequestTimeout(connectionRequestTimeInMillis)
                .build(), retry);
    }

    public HttpClient getConnection() {
        CloseableHttpClient httpClient = httpBuilder.setRetryHandler(myRetryHandler).build();
        return httpClient;
    }

    public <T> T get(String url, Function<String, T> function) throws Exception {
        HttpClient client = getConnection();
        HttpGet get = new HttpGet(String.format("%s%s", this.hostPort, url));
        get.setConfig(requestConfig);
        return client.execute(get, (httpResponse) -> {
            String body = EntityUtils.toString(httpResponse.getEntity(), "UTF-8");
            return function.apply(body);
        });
    }

    public <T> T post(String url, String request, Function<String, T> function) throws Exception {
        HttpClient client = getConnection();
        HttpPost post = new HttpPost(String.format("%s%s", this.hostPort, url));
        post.setConfig(requestConfig);
        String json = request;
        StringEntity requestEntity = new StringEntity(json, "utf-8");
        requestEntity.setContentEncoding("UTF-8");
        post.setHeader("Content-type", "application/json");
        post.setEntity(requestEntity);
        return client.execute(post, (httpResponse) -> {
            String body = EntityUtils.toString(httpResponse.getEntity(), "UTF-8");
            return function.apply(body);
        });
    }

    public void close() {
        try {
            connectionManager.close();
        } finally {
            //ignore exception.
        }
    }
}
