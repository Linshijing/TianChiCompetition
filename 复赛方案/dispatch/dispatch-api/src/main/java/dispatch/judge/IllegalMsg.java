package dispatch.judge;

import lombok.Getter;

@Getter
public class IllegalMsg {
    private boolean illegal;
    private String msg = "";

    public IllegalMsg(String msg) {
        this.illegal = true;
        this.msg = msg;
    }

    public IllegalMsg() {

    }
}
