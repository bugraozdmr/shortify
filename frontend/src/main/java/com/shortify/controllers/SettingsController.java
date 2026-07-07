package com.shortify.controllers;

import com.shortify.utils.ConfigManager;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.animation.PauseTransition;
import javafx.util.Duration;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

import com.shortify.utils.GlobalState;

public class SettingsController {

    @FXML private TextField txtApiUrl;
    @FXML private Label lblStatus;
    @FXML private Label lblConnectionStatus;

    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(java.time.Duration.ofSeconds(3))
            .build();

    @FXML
    public void initialize() {
        txtApiUrl.setText(ConfigManager.getInstance().getApiUrl());
        
        // Listen to Global State
        GlobalState.getInstance().backendOnlineProperty().addListener((obs, oldVal, newVal) -> {
            Platform.runLater(() -> {
                if (newVal) {
                    setConnectionBadge("Bağlı (Aktif)", "success");
                } else {
                    setConnectionBadge("Bağlantı Yok", "danger");
                }
            });
        });

        // Initialize with current state
        if (GlobalState.getInstance().isBackendOnline()) {
            setConnectionBadge("Bağlı (Aktif)", "success");
        } else {
            setConnectionBadge("Bağlantı Yok / Kontrol Ediliyor...", "accent");
        }

        testConnection();
    }

    @FXML
    private void saveSettings() {
        String newUrl = txtApiUrl.getText().trim();
        
        if (newUrl.isEmpty()) {
            showStatus("API URL boş bırakılamaz!", "danger");
            return;
        }
        
        ConfigManager.getInstance().setApiUrl(newUrl);
        showStatus("Ayarlar başarıyla kaydedildi!", "success");
        testConnection();
    }

    @FXML
    private void testConnection() {
        String url = txtApiUrl.getText().trim();
        if (url.isEmpty()) return;

        Platform.runLater(() -> {
            lblConnectionStatus.setText("Sınanıyor...");
            lblConnectionStatus.getStyleClass().removeAll("success", "danger");
            lblConnectionStatus.getStyleClass().add("accent");
        });

        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            Platform.runLater(() -> setConnectionBadge("Hatalı URL (http/https gerekli)", "danger"));
            return;
        }

        HttpRequest request;
        try {
            request = HttpRequest.newBuilder()
                    .uri(URI.create(url + "/health"))
                    .GET()
                    .build();
        } catch (IllegalArgumentException e) {
            Platform.runLater(() -> setConnectionBadge("Geçersiz URL Formatı", "danger"));
            return;
        }

        CompletableFuture.supplyAsync(() -> {
            try {
                return httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }).thenAccept(response -> {
            if (response.statusCode() == 200 && response.body().contains("success")) {
                GlobalState.getInstance().setBackendOnline(true);
                Platform.runLater(() -> setConnectionBadge("Bağlı (Aktif)", "success"));
            } else {
                GlobalState.getInstance().setBackendOnline(false);
                Platform.runLater(() -> setConnectionBadge("Hata (Geçersiz Yanıt)", "danger"));
            }
        }).exceptionally(ex -> {
            GlobalState.getInstance().setBackendOnline(false);
            Platform.runLater(() -> {
                setConnectionBadge("Ulaşılamıyor", "danger");
            });
            return null;
        });
    }

    private void setConnectionBadge(String text, String styleClass) {
        lblConnectionStatus.setText(text);
        lblConnectionStatus.getStyleClass().removeAll("success", "danger", "accent");
        lblConnectionStatus.getStyleClass().add(styleClass);
    }

    private void showStatus(String message, String styleClass) {
        lblStatus.setText(message);
        lblStatus.getStyleClass().removeAll("success", "danger");
        lblStatus.getStyleClass().add(styleClass);
        lblStatus.setVisible(true);

        PauseTransition pause = new PauseTransition(Duration.seconds(3));
        pause.setOnFinished(e -> lblStatus.setVisible(false));
        pause.play();
    }
}
