package com.shortify.controllers;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextArea;
import javafx.scene.layout.VBox;
import org.json.JSONObject;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

public class DashboardController {

    @FXML private ComboBox<String> modeComboBox;
    @FXML private VBox manualInputBox;
    @FXML private TextArea customTextArea;
    @FXML private Button generateBtn;
    @FXML private Label statusLabel;

    private final HttpClient httpClient = HttpClient.newHttpClient();

    @FXML
    public void initialize() {
        // Listen to combo box changes
        modeComboBox.valueProperty().addListener((obs, oldVal, newVal) -> {
            boolean isManual = "Manuel (Özel Metin)".equals(newVal);
            manualInputBox.setVisible(isManual);
            manualInputBox.setManaged(isManual);
        });
    }

    @FXML
    private void handleGenerate() {
        String mode = modeComboBox.getValue();
        boolean isManual = "Manuel (Özel Metin)".equals(mode);

        JSONObject payload = new JSONObject();
        
        if (isManual) {
            String text = customTextArea.getText().trim();
            if (text.isEmpty()) {
                updateStatus("Hata: Özel metin boş olamaz!", "status-label", "danger");
                return;
            }
            payload.put("mode", "manual");
            payload.put("custom_text", text);
        } else {
            payload.put("mode", "auto");
        }

        generateBtn.setDisable(true);
        updateStatus("Shortify Backend'e istek gönderiliyor...", "status-label", "accent");

        String apiUrl = com.shortify.utils.ConfigManager.getInstance().getApiUrl() + "/generate/";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(apiUrl))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload.toString()))
                .build();

        CompletableFuture.supplyAsync(() -> {
            try {
                return httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }).thenAccept(response -> {
            Platform.runLater(() -> {
                generateBtn.setDisable(false);
                if (response.statusCode() == 200) {
                    updateStatus("Başarılı: Arka planda video oluşturulmaya başlandı!", "status-label", "success");
                    if (isManual) customTextArea.clear();
                } else {
                    updateStatus("Hata: HTTP " + response.statusCode(), "status-label", "danger");
                }
            });
        }).exceptionally(ex -> {
            Platform.runLater(() -> {
                generateBtn.setDisable(false);
                updateStatus("Hata: Bağlantı kurulamadı! Sunucu çalışıyor mu?", "status-label", "danger");
            });
            return null;
        });
    }

    private void updateStatus(String text, String... styleClasses) {
        statusLabel.setText(text);
        statusLabel.getStyleClass().clear();
        for (String styleClass : styleClasses) {
            statusLabel.getStyleClass().add(styleClass);
        }
    }
}
