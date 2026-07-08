package com.shortify.controllers;

import javafx.animation.KeyFrame;
import javafx.animation.KeyValue;
import javafx.animation.Timeline;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.image.ImageView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.util.Duration;
import org.kordamp.ikonli.javafx.FontIcon;

import com.shortify.utils.GlobalState;
import javafx.application.Platform;

import java.io.IOException;

public class MainController {

    @FXML private StackPane contentArea;
    @FXML private VBox sidebar;

    @FXML private Button btnPosts;
    @FXML private Button btnSettings;
    @FXML private Button btnCollapse;
    @FXML private FontIcon collapseIcon;
    @FXML private ImageView logoImage;
    @FXML private HBox logoBox;
    @FXML private Label lblAppName;
    @FXML private Label lblMenuTitle;
    @FXML private HBox statusBar;
    
    @FXML private Label lblGlobalStatusIcon;
    @FXML private Label lblGlobalStatusText;
    
    private boolean sidebarCollapsed = false;
    private static final double EXPANDED_WIDTH = 220;
    private static final double COLLAPSED_WIDTH = 60;
    
    @FXML
    public void initialize() {
        // Sidebar genişliği ayarla
        sidebar.setPrefWidth(EXPANDED_WIDTH);
        sidebar.setMinWidth(COLLAPSED_WIDTH);
        
        // Load default view
        loadView("posts.fxml", btnPosts);

        // Bind global status
        GlobalState.getInstance().backendOnlineProperty().addListener((obs, oldVal, newVal) -> {
            Platform.runLater(() -> {
                if (newVal) {
                    lblGlobalStatusIcon.setStyle("-fx-font-size: 10px; -fx-text-fill: -color-success-emphasis;");
                    lblGlobalStatusText.setText("Sunucu Çevrimiçi");
                } else {
                    lblGlobalStatusIcon.setStyle("-fx-font-size: 10px; -fx-text-fill: -color-danger-emphasis;");
                    lblGlobalStatusText.setText("Bağlantı Koptu");
                }
            });
        });
    }

    @FXML
    private void toggleSidebar() {
        sidebarCollapsed = !sidebarCollapsed;
        
        double targetWidth = sidebarCollapsed ? COLLAPSED_WIDTH : EXPANDED_WIDTH;
        
        // Animasyonlu geçiş
        Timeline timeline = new Timeline(
            new KeyFrame(Duration.millis(200),
                new KeyValue(sidebar.prefWidthProperty(), targetWidth)
            )
        );
        timeline.play();
        
        if (sidebarCollapsed) {
            // Daralt: metinleri gizle, sadece ikonlar kalsın
            collapseIcon.setIconLiteral("fth-chevrons-right");
            lblAppName.setVisible(false);
            lblAppName.setManaged(false);
            lblMenuTitle.setVisible(false);
            lblMenuTitle.setManaged(false);
            lblGlobalStatusText.setVisible(false);
            lblGlobalStatusText.setManaged(false);
            logoImage.setFitHeight(28);
            
            // Buton metinlerini gizle
            btnPosts.setText("");
            btnSettings.setText("");
            btnCollapse.setText("");
            
            // Durum çubuğunu ve logoyu ortala
            logoBox.setAlignment(javafx.geometry.Pos.CENTER);
            logoBox.setStyle("-fx-padding: 0 0 25 0;");
            statusBar.setAlignment(javafx.geometry.Pos.CENTER);
            statusBar.setStyle("-fx-padding: 12 0 4 0;");
            
            // Sidebar padding daralt
            sidebar.setStyle("-fx-padding: 20 6 15 6;");
        } else {
            // Genişlet: metinleri göster
            collapseIcon.setIconLiteral("fth-chevrons-left");
            lblAppName.setVisible(true);
            lblAppName.setManaged(true);
            lblMenuTitle.setVisible(true);
            lblMenuTitle.setManaged(true);
            lblGlobalStatusText.setVisible(true);
            lblGlobalStatusText.setManaged(true);
            logoImage.setFitHeight(36);
            
            // Buton metinlerini geri getir
            btnPosts.setText("Gönderiler");
            btnSettings.setText("Ayarlar");
            btnCollapse.setText("Daralt");
            
            // Durum çubuğunu ve logoyu sola yasla
            logoBox.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
            logoBox.setStyle(""); // CSS'e dön
            statusBar.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
            statusBar.setStyle(""); // CSS'e dön
            
            // Sidebar padding genişlet
            sidebar.setStyle("-fx-padding: 20 8 15 8;");
        }
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
            updateActiveButton(activeButton);
        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Failed to load view: " + fxmlFile);
        }
    }

    private void updateActiveButton(Button activeBtn) {
        btnPosts.getStyleClass().remove("active");
        btnSettings.getStyleClass().remove("active");
        
        if (activeBtn != null) {
            activeBtn.getStyleClass().add("active");
        }
    }
}
