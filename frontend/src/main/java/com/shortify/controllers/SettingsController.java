package com.shortify.controllers;

import com.shortify.utils.ConfigManager;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.control.TextArea;
import javafx.scene.control.ComboBox;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Button;
import javafx.scene.layout.VBox;
import javafx.animation.PauseTransition;
import javafx.util.Duration;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;
import org.json.JSONObject;
import com.shortify.utils.GlobalState;
import com.shortify.utils.AppLogger;
import com.shortify.utils.HttpClientUtil;

public class SettingsController {

    @FXML private TextField txtApiUrl;
    @FXML private Label lblStatus;
    @FXML private Label lblConnectionStatus;
    @FXML private Button btnLogs;
    @FXML private Button btnSaveSettings;
    @FXML private VBox settingsContainer;

    @FXML private ComboBox<String> cmbAiProvider;
    @FXML private ComboBox<String> cmbAiModel;
    @FXML private TextField txtGeminiKey;
    @FXML private TextField txtOpenaiKey;
    @FXML private TextField txtDeepseekKey;
    @FXML private TextField txtOpenrouterKey;
    @FXML private TextField txtAiMaxRetries;
    @FXML private TextField txtAiRetryWait;

    @FXML private TextField txtRedditFetchMaxPages;
    @FXML private TextField txtYoutubeMaxUploadsPerDay;

    @FXML private TextField txtChannelName;
    @FXML private TextField txtSystemCleanupDays;
    @FXML private TextField txtTelegramBotToken;
    @FXML private TextField txtTelegramChatId;
    @FXML private CheckBox chkTelegramNotification;
    @FXML private TextField txtYoutubeClientId;
    @FXML private TextField txtYoutubeClientSecret;
    @FXML private TextField txtYoutubeRedirectUri;


    @FXML private CheckBox chkAutoUpload;
    @FXML private TextField txtUploadStart;
    @FXML private TextField txtUploadEnd;

    @FXML private CheckBox chkAutoGenerate;
    @FXML private TextField txtGenHours;
    @FXML private TextField txtGenMinutes;
    @FXML private TextField txtGenMaxConcurrent;

    @FXML
    public void initialize() {
        txtApiUrl.setText(ConfigManager.getInstance().getApiUrl());
        
        // Initialize ComboBoxes
        cmbAiProvider.getItems().addAll("gemini", "openai", "deepseek", "openrouter");
        
        // Setup AI Models logic
        setupAiModelsLogic();
        
        // Listen to Global State
        GlobalState.getInstance().backendOnlineProperty().addListener((obs, oldVal, newVal) -> {
            Platform.runLater(() -> {
                settingsContainer.setDisable(!newVal);
                btnLogs.setDisable(!newVal);
                btnSaveSettings.setDisable(!newVal);
                if (newVal) {
                    setConnectionBadge("Bağlı (Aktif)", "success");
                    fetchSettings();
                } else {
                    setConnectionBadge("Bağlantı Yok", "danger");
                }
            });
        });

        // Initialize with current state
        boolean isOnline = GlobalState.getInstance().isBackendOnline();
        settingsContainer.setDisable(!isOnline);
        btnLogs.setDisable(!isOnline);
        btnSaveSettings.setDisable(!isOnline);
        
        if (isOnline) {
            setConnectionBadge("Bağlı (Aktif)", "success");
            fetchSettings();
        } else {
            setConnectionBadge("Bağlantı Yok / Kontrol Ediliyor...", "accent");
            testConnection();
        }
    }

    private void setupAiModelsLogic() {
        cmbAiProvider.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                updateAiModels(newVal);
            }
        });
    }

    private void updateAiModels(String provider) {
        String currentModel = cmbAiModel.getValue();
        cmbAiModel.getItems().clear();
        
        if ("gemini".equals(provider)) {
            cmbAiModel.getItems().addAll(
                "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
                "gemini-2.0-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite",
                "gemini-1.5-pro", "gemini-1.5-flash", "gemma-3", "gemma-2"
            );
        } else if ("openai".equals(provider)) {
            cmbAiModel.getItems().addAll(
                "gpt-5", "gpt-5-mini", "gpt-5-nano",
                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
                "gpt-4o", "gpt-4o-mini", "o3", "o3-pro", "o4-mini"
            );
        } else if ("deepseek".equals(provider)) {
            cmbAiModel.getItems().addAll(
                "deepseek-v3", "deepseek-v3.1", "deepseek-v3-0324",
                "deepseek-v3-flash", "deepseek-v3-flash-lite",
                "deepseek-r1", "deepseek-r1-0528", "deepseek-r1-lite",
                "deepseek-coder-v2", "deepseek-math", "deepseek-vl"
            );
        } else if ("openrouter".equals(provider)) {
            cmbAiModel.getItems().addAll(
                "openai/gpt-5", "openai/gpt-5-mini", "openai/gpt-4.1",
                "google/gemini-2.5-flash", "google/gemini-2.5-pro",
                "anthropic/claude-sonnet-4", "anthropic/claude-4-opus",
                "deepseek/deepseek-v3", "deepseek/deepseek-r1",
                "meta-llama/llama-4", "mistralai/mistral-large"
            );
        }
        
        // Eğer önceki model listede varsa koru, yoksa ilkini seç
        if (currentModel != null && cmbAiModel.getItems().contains(currentModel)) {
            cmbAiModel.setValue(currentModel);
        } else if (!cmbAiModel.getItems().isEmpty()) {
            cmbAiModel.setValue(cmbAiModel.getItems().get(0));
        }
    }

    private void fetchSettings() {
        String baseUrl = ConfigManager.getInstance().getApiUrl().replaceAll("/+$", "");
        String url = baseUrl + "/settings/";
        
        HttpClientUtil.getAsync(url, null)
            .thenAccept(response -> {
                if (response.statusCode() == 200) {
                    try {
                        JSONObject json = new JSONObject(response.body());
                        Platform.runLater(() -> populateFields(json));
                    } catch (Exception e) {
                        AppLogger.error("JSON parse hatası: " + response.body(), e);
                    }
                }
            });
    }

    private void populateFields(JSONObject json) {
        String provider = json.optString("ai_provider", "gemini");
        cmbAiProvider.setValue(provider);
        updateAiModels(provider);
        cmbAiModel.setValue(json.optString("ai_model", "gemini-2.5-flash"));
        
        JSONObject keys = json.optJSONObject("api_keys");
        if (keys != null) {
            txtGeminiKey.setText(keys.optString("gemini", ""));
            txtOpenaiKey.setText(keys.optString("openai", ""));
            txtDeepseekKey.setText(keys.optString("deepseek", ""));
            txtOpenrouterKey.setText(keys.optString("openrouter", ""));
        }

        txtAiMaxRetries.setText(String.valueOf(json.optInt("ai_max_retries", 3)));
        txtAiRetryWait.setText(String.valueOf(json.optInt("ai_retry_wait_seconds", 3)));

        chkAutoUpload.setSelected(json.optBoolean("is_auto_upload", false));
        txtUploadStart.setText(json.optString("allowed_upload_start_time", "18:00"));
        txtUploadEnd.setText(json.optString("allowed_upload_end_time", "22:00"));

        txtRedditFetchMaxPages.setText(String.valueOf(json.optInt("reddit_fetch_max_pages", 5)));
        txtYoutubeMaxUploadsPerDay.setText(String.valueOf(json.optInt("youtube_max_uploads_per_day", 3)));

        chkAutoGenerate.setSelected(json.optBoolean("auto_generate_enabled", false));
        txtGenHours.setText(String.valueOf(json.optInt("auto_generate_interval_hours", 0)));
        txtGenMinutes.setText(String.valueOf(json.optInt("auto_generate_interval_minutes", 30)));
        txtGenMaxConcurrent.setText(String.valueOf(json.optInt("auto_generate_max_concurrent", 2)));

        txtChannelName.setText(json.optString("channel_name", "Anlatsana"));
        txtSystemCleanupDays.setText(String.valueOf(json.optInt("system_cleanup_older_than_days", 1)));
        txtTelegramBotToken.setText(json.optString("telegram_bot_token", ""));
        txtTelegramChatId.setText(json.optString("telegram_chat_id", ""));
        chkTelegramNotification.setSelected(json.optBoolean("telegram_notification_active", true));
        txtYoutubeClientId.setText(json.optString("youtube_client_id", ""));
        txtYoutubeClientSecret.setText(json.optString("youtube_client_secret", ""));
        txtYoutubeRedirectUri.setText(json.optString("youtube_redirect_uri", "http://localhost:8080/"));
    }

    @FXML
    private void saveSettings() {
        String newUrl = txtApiUrl.getText().trim().replaceAll("/+$", "");
        if (newUrl.isEmpty()) {
            showStatus("API URL boş bırakılamaz!", "danger");
            return;
        }
        ConfigManager.getInstance().setApiUrl(newUrl);

        if (!GlobalState.getInstance().isBackendOnline()) {
            testConnection();
            return;
        }

        try {
            JSONObject payload = new JSONObject();
            payload.put("ai_provider", cmbAiProvider.getValue());
            payload.put("ai_model", cmbAiModel.getValue());
            
            JSONObject keys = new JSONObject();
            keys.put("gemini", txtGeminiKey.getText().trim());
            keys.put("openai", txtOpenaiKey.getText().trim());
            keys.put("deepseek", txtDeepseekKey.getText().trim());
            keys.put("openrouter", txtOpenrouterKey.getText().trim());
            payload.put("api_keys", keys);

            payload.put("ai_max_retries", Integer.parseInt(txtAiMaxRetries.getText().trim()));
            payload.put("ai_retry_wait_seconds", Integer.parseInt(txtAiRetryWait.getText().trim()));

            payload.put("is_auto_upload", chkAutoUpload.isSelected());
            payload.put("allowed_upload_start_time", txtUploadStart.getText());
            payload.put("allowed_upload_end_time", txtUploadEnd.getText());

            payload.put("reddit_fetch_max_pages", Integer.parseInt(txtRedditFetchMaxPages.getText().trim()));
            payload.put("youtube_max_uploads_per_day", Integer.parseInt(txtYoutubeMaxUploadsPerDay.getText().trim()));

            payload.put("auto_generate_enabled", chkAutoGenerate.isSelected());
            payload.put("auto_generate_interval_hours", Integer.parseInt(txtGenHours.getText().trim()));
            payload.put("auto_generate_interval_minutes", Integer.parseInt(txtGenMinutes.getText().trim()));
            payload.put("auto_generate_max_concurrent", Integer.parseInt(txtGenMaxConcurrent.getText().trim()));

            payload.put("channel_name", txtChannelName.getText().trim());
            payload.put("system_cleanup_older_than_days", Integer.parseInt(txtSystemCleanupDays.getText().trim()));
            payload.put("telegram_bot_token", txtTelegramBotToken.getText().trim());
            payload.put("telegram_chat_id", txtTelegramChatId.getText().trim());
            payload.put("telegram_notification_active", chkTelegramNotification.isSelected());
            payload.put("youtube_client_id", txtYoutubeClientId.getText().trim());
            payload.put("youtube_client_secret", txtYoutubeClientSecret.getText().trim());
            payload.put("youtube_redirect_uri", txtYoutubeRedirectUri.getText().trim());
            
            String targetUrl = newUrl + "/settings/";
            String jsonPayload = payload.toString();
            
            HttpClientUtil.putAsync(targetUrl, jsonPayload, null)
                .thenAccept(response -> {
                    if (response.statusCode() == 200) {
                        Platform.runLater(() -> showStatus("Tüm ayarlar sunucuya başarıyla kaydedildi!", "success"));
                    } else {
                        Platform.runLater(() -> showStatus("Ayarlar kaydedilirken sunucu hatası oluştu.", "danger"));
                    }
                })
                .exceptionally(ex -> {
                    Platform.runLater(() -> showStatus("Bağlantı koptu veya hata oluştu.", "danger"));
                    return null;
                });
        } catch (Exception e) {
            AppLogger.error("Veriler gönderilirken beklenmeyen bir hata oluştu.", e);
            showStatus("Veriler gönderilirken bir hata oluştu.", "danger");
        }
    }

    @FXML
    private void saveApiUrlAndTest() {
        String newUrl = txtApiUrl.getText().trim().replaceAll("/+$", "");
        if (newUrl.isEmpty()) {
            showStatus("API URL boş bırakılamaz!", "danger");
            return;
        }
        ConfigManager.getInstance().setApiUrl(newUrl);
        showStatus("URL Kaydedildi. Sınanıyor...", "success");
        testConnection();
    }

    @FXML
    private void testConnection() {
        String url = txtApiUrl.getText().trim().replaceAll("/+$", "");
        if (url.isEmpty()) return;

        AppLogger.info("Sunucu bağlantısı sınanıyor: " + url);
        Platform.runLater(() -> {
            lblConnectionStatus.setText("Sınanıyor...");
            lblConnectionStatus.getStyleClass().removeAll("success", "danger");
            lblConnectionStatus.getStyleClass().add("accent");
        });

        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            Platform.runLater(() -> setConnectionBadge("Hatalı URL (http/https gerekli)", "danger"));
            return;
        }

        HttpClientUtil.getAsync(url + "/health", null)
            .thenAccept(response -> {
                if (response.statusCode() == 200 && response.body().contains("success")) {
                    ConfigManager.getInstance().setApiUrl(url); // Başarılıysa kaydet
                    GlobalState.getInstance().setBackendOnline(true);
                    Platform.runLater(() -> setConnectionBadge("Bağlı (Aktif)", "success"));
                } else {
                    GlobalState.getInstance().setBackendOnline(false);
                    Platform.runLater(() -> setConnectionBadge("Hata (Geçersiz Yanıt)", "danger"));
                }
            }).exceptionally(ex -> {
                GlobalState.getInstance().setBackendOnline(false);
                Platform.runLater(() -> setConnectionBadge("Ulaşılamıyor", "danger"));
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

    @FXML
    private void openLogs() {
        String baseUrl = txtApiUrl.getText().trim();
        if (baseUrl.isEmpty()) return;
        
        String logUrl = baseUrl + "/settings/logs";
        try {
            if (java.awt.Desktop.isDesktopSupported() && java.awt.Desktop.getDesktop().isSupported(java.awt.Desktop.Action.BROWSE)) {
                java.awt.Desktop.getDesktop().browse(new URI(logUrl));
            } else {
                String os = System.getProperty("os.name").toLowerCase();
                if (os.contains("mac")) {
                    new ProcessBuilder("open", logUrl).start();
                } else if (os.contains("nix") || os.contains("nux")) {
                    new ProcessBuilder("xdg-open", logUrl).start();
                } else if (os.contains("win")) {
                    new ProcessBuilder("rundll32", "url.dll,FileProtocolHandler", logUrl).start();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            showStatus("Log dosyası açılamadı!", "danger");
        }
    }
}
