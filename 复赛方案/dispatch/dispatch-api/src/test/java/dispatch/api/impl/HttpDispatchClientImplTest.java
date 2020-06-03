package dispatch.api.impl;

import com.alibaba.fastjson.JSON;
import dispatch.api.DispatchClient;
import dispatch.api.exception.DispatchException;
import dispatch.judge.DispatchJudge;
import lombok.extern.slf4j.Slf4j;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.io.IOException;
import java.util.HashMap;

import static org.junit.Assert.assertEquals;

@Slf4j
public class HttpDispatchClientImplTest {
    private static DispatchClient dispatchClient;

    @BeforeClass
    public static void init() {
        dispatchClient = new HttpDispatchClientImpl();
    }

    @AfterClass
    public static void destroy() throws IOException {
        dispatchClient.close();
    }

    @Test
    public void testPing() throws DispatchException, InterruptedException {
        log.error(String.format("%s", JSON.toJSON(new DispatchJudge())));
        assertEquals(dispatchClient.ping().getResult(), "PONG");
        Thread.sleep(100);
    }

}
