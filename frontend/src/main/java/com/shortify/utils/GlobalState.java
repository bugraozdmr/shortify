package com.shortify.utils;

import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;
import javafx.application.Platform;

public class GlobalState {
    private static GlobalState instance;
    private final BooleanProperty backendOnline = new SimpleBooleanProperty(false);

    private GlobalState() {}

    public static GlobalState getInstance() {
        if (instance == null) {
            instance = new GlobalState();
        }
        return instance;
    }

    public BooleanProperty backendOnlineProperty() {
        return backendOnline;
    }

    public boolean isBackendOnline() {
        return backendOnline.get();
    }

    public void setBackendOnline(boolean online) {
        if (Platform.isFxApplicationThread()) {
            backendOnline.set(online);
        } else {
            Platform.runLater(() -> backendOnline.set(online));
        }
    }
}
