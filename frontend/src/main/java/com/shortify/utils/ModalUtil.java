package com.shortify.utils;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Region;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.stage.StageStyle;
import javafx.stage.Window;
import org.kordamp.ikonli.javafx.FontIcon;

import java.util.concurrent.CompletableFuture;

/**
 * Uygulama genelinde kullanılabilecek şık ve modern modal pencereler.
 * Tüm modaller ana pencerenin üzerine, yarı-saydam siyah arka plan ile açılır.
 */
public class ModalUtil {

    // ═══════════════════════════════════════════════════════
    //  ONAY MODALI (Evet / Hayır)
    // ═══════════════════════════════════════════════════════
    public static CompletableFuture<Boolean> showConfirmModal(
            Window owner,
            String title,
            String message,
            String confirmText,
            String cancelText,
            String iconLiteral,
            String iconColor,
            String confirmBtnClass) {
            
        CompletableFuture<Boolean> future = new CompletableFuture<>();
        
        Stage modalStage = createModalStage(owner);
        StackPane overlay = createOverlay();
        VBox card = createCard();
        
        // İkon
        FontIcon icon = new FontIcon(iconLiteral);
        icon.setIconSize(56);
        if (iconColor != null && !iconColor.isEmpty()) {
            icon.setIconColor(Color.web(iconColor));
        }
        
        // Başlık
        Label lblTitle = new Label(title);
        lblTitle.getStyleClass().add("title-3");
        lblTitle.setStyle("-fx-font-weight: bold;");
        
        // Mesaj
        Label lblMessage = new Label(message);
        lblMessage.setWrapText(true);
        lblMessage.setTextAlignment(javafx.scene.text.TextAlignment.CENTER);
        lblMessage.getStyleClass().add("text-muted");
        lblMessage.setStyle("-fx-font-size: 13px; -fx-line-spacing: 2;");
        lblMessage.setMaxWidth(350);
        
        // Butonlar
        HBox buttonBox = new HBox(12);
        buttonBox.setAlignment(Pos.CENTER);
        buttonBox.setPadding(new Insets(8, 0, 0, 0));
        
        Button btnCancel = new Button(cancelText);
        btnCancel.getStyleClass().add("btn");
        btnCancel.getStyleClass().add("btn-outline");
        btnCancel.setPrefWidth(130);
        btnCancel.setPrefHeight(38);
        btnCancel.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
        btnCancel.setOnAction(e -> {
            future.complete(false);
            modalStage.close();
        });
        
        Button btnConfirm = new Button(confirmText);
        btnConfirm.getStyleClass().add("btn");
        if (confirmBtnClass != null && !confirmBtnClass.isEmpty()) {
            btnConfirm.getStyleClass().add(confirmBtnClass);
        }
        btnConfirm.setPrefWidth(130);
        btnConfirm.setPrefHeight(38);
        btnConfirm.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
        btnConfirm.setOnAction(e -> {
            future.complete(true);
            modalStage.close();
        });
        
        buttonBox.getChildren().addAll(btnCancel, btnConfirm);
        card.getChildren().addAll(icon, lblTitle, lblMessage, buttonBox);
        overlay.getChildren().add(card);
        
        showModal(modalStage, overlay, owner);
        
        return future;
    }

    // ═══════════════════════════════════════════════════════
    //  BİLGİLENDİRME MODALI (Başarılı / Hata / Uyarı / Bilgi)
    // ═══════════════════════════════════════════════════════
    
    /** Başarı bildirimi */
    public static void showSuccess(Window owner, String title, String message) {
        showInfoModal(owner, title, message, "fth-check-circle", "#22c55e", "accent");
    }
    
    /** Hata bildirimi */
    public static void showError(Window owner, String title, String message) {
        showInfoModal(owner, title, message, "fth-x-circle", "#ef4444", "danger");
    }
    
    /** Uyarı bildirimi */
    public static void showWarning(Window owner, String title, String message) {
        showInfoModal(owner, title, message, "fth-alert-triangle", "#f59e0b", "accent");
    }
    
    /** Genel bilgilendirme */
    public static void showInfo(Window owner, String title, String message) {
        showInfoModal(owner, title, message, "fth-info", "#3b82f6", "accent");
    }

    private static void showInfoModal(
            Window owner,
            String title,
            String message,
            String iconLiteral,
            String iconColor,
            String btnClass) {
        
        Stage modalStage = createModalStage(owner);
        StackPane overlay = createOverlay();
        VBox card = createCard();
        
        // İkon
        FontIcon icon = new FontIcon(iconLiteral);
        icon.setIconSize(56);
        icon.setIconColor(Color.web(iconColor));
        
        // Başlık
        Label lblTitle = new Label(title);
        lblTitle.getStyleClass().add("title-3");
        lblTitle.setStyle("-fx-font-weight: bold;");
        
        // Mesaj
        Label lblMessage = new Label(message);
        lblMessage.setWrapText(true);
        lblMessage.setTextAlignment(javafx.scene.text.TextAlignment.CENTER);
        lblMessage.getStyleClass().add("text-muted");
        lblMessage.setStyle("-fx-font-size: 13px; -fx-line-spacing: 2;");
        lblMessage.setMaxWidth(350);
        
        // Tamam Butonu
        Button btnOk = new Button("Tamam");
        btnOk.getStyleClass().addAll("btn", btnClass);
        btnOk.setPrefWidth(160);
        btnOk.setPrefHeight(38);
        btnOk.setStyle("-fx-font-weight: bold; -fx-font-size: 13px;");
        btnOk.setOnAction(e -> modalStage.close());
        
        HBox buttonBox = new HBox(btnOk);
        buttonBox.setAlignment(Pos.CENTER);
        buttonBox.setPadding(new Insets(8, 0, 0, 0));
        
        card.getChildren().addAll(icon, lblTitle, lblMessage, buttonBox);
        overlay.getChildren().add(card);
        
        showModal(modalStage, overlay, owner);
    }

    // ═══════════════════════════════════════════════════════
    //  ORTAK YARDIMCILAR
    // ═══════════════════════════════════════════════════════
    
    private static Stage createModalStage(Window owner) {
        Stage stage = new Stage();
        if (owner != null) {
            stage.initOwner(owner);
        }
        stage.initModality(Modality.APPLICATION_MODAL);
        stage.initStyle(StageStyle.TRANSPARENT);
        return stage;
    }
    
    private static StackPane createOverlay() {
        StackPane overlay = new StackPane();
        overlay.setStyle("-fx-background-color: rgba(0, 0, 0, 0.70);");
        return overlay;
    }
    
    private static VBox createCard() {
        VBox card = new VBox(18);
        card.setAlignment(Pos.CENTER);
        card.setMaxWidth(420);
        card.setMaxHeight(VBox.USE_PREF_SIZE);
        card.getStyleClass().addAll("card", "elevated-4");
        card.setPadding(new Insets(35, 35, 30, 35));
        return card;
    }
    
    private static void showModal(Stage modalStage, StackPane overlay, Window owner) {
        Scene scene = new Scene(overlay);
        scene.setFill(Color.TRANSPARENT);
        if (owner != null && owner.getScene() != null) {
            scene.getStylesheets().addAll(owner.getScene().getStylesheets());
        }
        
        modalStage.setScene(scene);
        
        if (owner != null) {
            modalStage.setX(owner.getX());
            modalStage.setY(owner.getY());
            modalStage.setWidth(owner.getWidth());
            modalStage.setHeight(owner.getHeight());
            
            owner.xProperty().addListener((obs, o, n) -> modalStage.setX(n.doubleValue()));
            owner.yProperty().addListener((obs, o, n) -> modalStage.setY(n.doubleValue()));
            owner.widthProperty().addListener((obs, o, n) -> modalStage.setWidth(n.doubleValue()));
            owner.heightProperty().addListener((obs, o, n) -> modalStage.setHeight(n.doubleValue()));
        }
        
        // Overlay'e tıklanırsa kapatma (card dışı)
        overlay.setOnMouseClicked(e -> {
            if (e.getTarget() == overlay) {
                modalStage.close();
            }
        });
        
        modalStage.show();
    }
}
