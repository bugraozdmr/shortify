package com.shortify.controllers;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;

import javafx.scene.layout.HBox;
import javafx.stage.Stage;

import java.io.IOException;

import javafx.scene.control.Label;
import com.shortify.utils.GlobalState;
import javafx.application.Platform;

public class MainController {

    @FXML private StackPane contentArea;
    @FXML private Button btnDashboard;
    @FXML private Button btnPosts;
    @FXML private Button btnSettings;
    
    @FXML private Label lblGlobalStatusIcon;
    @FXML private Label lblGlobalStatusText;
    
    @FXML
    public void initialize() {
        // Load default view
        loadView("dashboard.fxml", btnDashboard);

        // Bind global status
        GlobalState.getInstance().backendOnlineProperty().addListener((obs, oldVal, newVal) -> {
            Platform.runLater(() -> {
                if (newVal) {
                    lblGlobalStatusIcon.setStyle("-fx-font-size: 14px; -fx-text-fill: -color-success-emphasis;");
                    lblGlobalStatusText.setText("Sunucu Çevrimiçi");
                } else {
                    lblGlobalStatusIcon.setStyle("-fx-font-size: 14px; -fx-text-fill: -color-danger-emphasis;");
                    lblGlobalStatusText.setText("Bağlantı Koptu");
                }
            });
        });
    }

    @FXML
    private void showDashboard() {
        loadView("dashboard.fxml", btnDashboard);
    }

    @FXML
    private void showPosts() {
        loadView("posts.fxml", btnPosts);
    }

    @FXML
    private void showSettings() {
        loadView("settings.fxml", btnSettings);
    }

    private void loadView(String fxmlFile, Button activeButton) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/" + fxmlFile));
            Node view = loader.load();
            contentArea.getChildren().setAll(view);
            
            // Update active state of buttons
            updateActiveButton(activeButton);
        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Failed to load view: " + fxmlFile);
        }
    }

    private void updateActiveButton(Button activeBtn) {
        btnDashboard.getStyleClass().remove("active");
        btnPosts.getStyleClass().remove("active");
        btnSettings.getStyleClass().remove("active");
        
        if (activeBtn != null) {
            activeBtn.getStyleClass().add("active");
        }
    }
}
