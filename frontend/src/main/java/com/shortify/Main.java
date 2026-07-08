package com.shortify;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import atlantafx.base.theme.PrimerDark;

import java.net.URL;
import java.awt.MenuItem;
import java.awt.PopupMenu;
import java.awt.SystemTray;
import java.awt.Toolkit;
import java.awt.TrayIcon;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

import javafx.application.Platform;
import javafx.scene.image.Image;
import javafx.stage.StageStyle;

import com.shortify.jobs.BackgroundJobManager;
import com.shortify.jobs.BackendHealthJob;
import com.shortify.jobs.PostsRefreshJob;
import java.util.concurrent.TimeUnit;

public class Main extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception {
        // Prevent JavaFX from exiting when the window is hidden
        Platform.setImplicitExit(false);

        // Set AtlantaFX Professional Theme
        Application.setUserAgentStylesheet(new PrimerDark().getUserAgentStylesheet());

        // Start Background Jobs
        BackgroundJobManager.getInstance().scheduleJob(new BackendHealthJob(), 0, 30, TimeUnit.SECONDS);
        BackgroundJobManager.getInstance().scheduleJob(new PostsRefreshJob(), 5, 5, TimeUnit.MINUTES);

        URL fxmlLocation = getClass().getResource("/fxml/layout.fxml");
        if (fxmlLocation == null) {
            System.err.println("Cannot find layout.fxml!");
            System.exit(1);
        }

        Parent root = FXMLLoader.load(fxmlLocation);
        Scene scene = new Scene(root, 1000, 700);

        URL cssLocation = getClass().getResource("/css/style.css");
        if (cssLocation != null) {
            scene.getStylesheets().add(cssLocation.toExternalForm());
        }

        // Set Application Icon for System Tray ONLY
        URL iconLocation = getClass().getResource("/images/icon.png");

        primaryStage.setTitle("Shortify");
        primaryStage.setScene(scene);
        primaryStage.setMinWidth(900);
        primaryStage.setMinHeight(600);
        primaryStage.show();

        // Setup System Tray
        if (iconLocation != null) {
            setupSystemTray(primaryStage, iconLocation);
        } else {
            System.err.println("Warning: icon.png not found. System tray will not be setup.");
        }
    }

    private void setupSystemTray(Stage primaryStage, URL iconLocation) {
        if (!SystemTray.isSupported()) {
            System.out.println("SystemTray is not supported");
            return;
        }

        try {
            SystemTray tray = SystemTray.getSystemTray();
            java.awt.Image image = Toolkit.getDefaultToolkit().getImage(iconLocation);
            
            TrayIcon trayIcon = new TrayIcon(image, "Shortify");
            trayIcon.setImageAutoSize(true);

            // Native Popup Menu
            PopupMenu popup = new PopupMenu();
            
            MenuItem statusItem = new MenuItem("Sunucu: ⚪ Kontrol ediliyor...");
            statusItem.setEnabled(false); // Sadece bilgi
            
            MenuItem openItem = new MenuItem("Uygulamayı Aç");
            openItem.addActionListener(e -> Platform.runLater(() -> {
                if (primaryStage.isIconified()) primaryStage.setIconified(false);
                primaryStage.show();
                primaryStage.toFront();
            }));
            
            MenuItem exitItem = new MenuItem("Çıkış Yap");
            exitItem.addActionListener(e -> {
                Platform.runLater(() -> {
                    Platform.exit();
                    System.exit(0);
                });
            });
            
            popup.add(statusItem);
            popup.addSeparator();
            popup.add(openItem);
            popup.add(exitItem);
            
            trayIcon.setPopupMenu(popup);
            tray.add(trayIcon);
            
            // Dinamik sunucu durumu güncellemesi
            com.shortify.utils.GlobalState.getInstance().backendOnlineProperty().addListener((obs, oldVal, newVal) -> {
                if (newVal) {
                    statusItem.setLabel("Sunucu: 🟢 Çevrimiçi");
                } else {
                    statusItem.setLabel("Sunucu: 🔴 Çevrimdışı");
                }
            });
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void stop() throws Exception {
        BackgroundJobManager.getInstance().shutdown();
        super.stop();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
