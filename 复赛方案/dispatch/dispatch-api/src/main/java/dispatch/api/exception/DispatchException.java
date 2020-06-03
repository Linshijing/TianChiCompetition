package dispatch.api.exception;

public class DispatchException extends Exception {
    public DispatchException(int code, String message) {
        super(message);
    }

    public DispatchException(int code, String message, Throwable t) {
        super(message, t);
    }
}
