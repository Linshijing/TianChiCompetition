package dispatch.api.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class Response<T> {

    private int code;
    private T result;
    private String message;


    public Response(T result) {
        this.code = 200;
        this.result = result;
    }

    public Response(int code, T result, String message) {
        this.code = code;
        this.result = result;
        this.message = message;
    }

    public Response(int code, T result) {
        this.code = code;
        this.result = result;
    }

    public static Response NewErrResponse(String message) {
        return new Response(500, message);
    }

    public static Response NewErrResponse(int code, String message) {
        return new Response(500, message);
    }
}
