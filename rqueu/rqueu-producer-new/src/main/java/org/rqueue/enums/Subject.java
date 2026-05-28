package org.rqueue.enums;

public enum Subject {
    STANDARD,
    VIP;

    @Override
    public String toString() {
        return name();
    }
}
