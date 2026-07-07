package com.shortify.controllers;

import com.shortify.models.Post;
import com.shortify.utils.ConfigManager;
import com.shortify.utils.PostService;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.Cursor;
import javafx.scene.control.Label;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.scene.media.MediaView;
import javafx.scene.layout.StackPane;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.shape.Rectangle;
import javafx.geometry.Pos;
import javafx.scene.control.Slider;
import javafx.util.Duration;
import org.kordamp.ikonli.javafx.FontIcon;

import java.net.URI;

public class PostsController {

    @FXML private VBox gridView;
    @FXML private FlowPane postsFlowPane;
    
    @FXML private VBox detailView;
    @FXML private Label lblDetailTitle;
    @FXML private Label lblDetailDate;
    
    @FXML private StackPane videoContainer;
    @FXML private MediaView mediaView;
    @FXML private VBox placeholderBox;
    @FXML private HBox controlsBox;
    @FXML private FontIcon playPauseIcon;
    @FXML private Slider videoSlider;
    @FXML private Label lblVideoTime;

    private MediaPlayer mediaPlayer;
    private final PostService postService = new PostService();

    @FXML
    public void initialize() {
        // detailView'i gizle, gridView'i göster ve hizalamasını ayarla
        detailView.setVisible(false);
        detailView.setManaged(false);
        detailView.setAlignment(Pos.TOP_CENTER);
        gridView.setVisible(true);
        gridView.setManaged(true);
        
        // Video konteynerini telefon (vertical) moduna uygun hale getir
        if (videoContainer != null) {
            videoContainer.setMaxWidth(400);
        }
        
        // Grid yapısını responsive hale getir (Ekran genişliğine göre kolon sayısını ve kart genişliğini ayarla)
        postsFlowPane.widthProperty().addListener((obs, oldVal, newVal) -> {
            double width = newVal.doubleValue() - postsFlowPane.getPadding().getLeft() - postsFlowPane.getPadding().getRight();
            int columns = (int) (width / 260); // 260px ideal kart genişliği (daha fazla kart sığması için küçültüldü)
            if (columns <= 0) columns = 1;
            
            double gap = postsFlowPane.getHgap();
            double cardWidth = (width - ((columns - 1) * gap)) / columns;
            cardWidth = Math.floor(cardWidth) - 1; // Yuvarlama hatalarından alt satıra düşmeyi önle
            
            for (var child : postsFlowPane.getChildren()) {
                if (child instanceof VBox) {
                    VBox card = (VBox) child;
                    card.setPrefWidth(cardWidth);
                    card.setMinWidth(cardWidth);
                    card.setMaxWidth(cardWidth);
                }
            }
        });
        
        loadPosts();
    }

    private void loadPosts() {
        postService.getPosts().thenAccept(posts -> {
            Platform.runLater(() -> {
                postsFlowPane.getChildren().clear();
                for (Post post : posts) {
                    postsFlowPane.getChildren().add(createPostCard(post));
                }
                // Kartlar eklendiğinde responsive boyutlandırmayı tetikle
                double currentWidth = postsFlowPane.getWidth();
                if (currentWidth > 0) {
                    // Trigger update manually by temporarily changing width property slightly or just wait for layout pass
                    // layout pass will happen naturally, but we can call requestLayout
                    postsFlowPane.requestLayout();
                }
            });
        }).exceptionally(ex -> {
            ex.printStackTrace();
            return null;
        });
    }

    private VBox createPostCard(Post post) {
        VBox card = new VBox(10);
        card.getStyleClass().addAll("card", "elevated-1");
        // Varsayılan genişlik atayalım (ilk açılışta saçmalamaması için)
        card.setPrefWidth(260);
        card.setMinWidth(260);
        card.setMaxWidth(260);
        card.setCursor(Cursor.HAND);
        
        // Thumbnail Placeholder and Image
        StackPane thumbnail = new StackPane();
        thumbnail.setPrefHeight(160);
        thumbnail.setStyle("-fx-background-color: #1a1a1a; -fx-background-radius: 8;");
        // Clip to radius
        Rectangle clip = new Rectangle();
        clip.widthProperty().bind(thumbnail.widthProperty());
        clip.heightProperty().bind(thumbnail.heightProperty());
        clip.setArcWidth(16);
        clip.setArcHeight(16);
        thumbnail.setClip(clip);
        
        if (post.getVideoPath() != null && !post.getVideoPath().isEmpty()) {
            String baseUrl = ConfigManager.getInstance().getApiUrl();
            String videoPath = post.getVideoPath().replace("\\", "/");
            String fileName = videoPath.substring(videoPath.lastIndexOf("/") + 1);
            String thumbUrl = baseUrl + "/stream/thumbnail/" + fileName;
            
            // Load image asynchronously in background
            ImageView imgView = new ImageView(new Image(thumbUrl, true));
            imgView.setPreserveRatio(true);
            imgView.fitHeightProperty().bind(thumbnail.heightProperty());
            imgView.fitWidthProperty().bind(thumbnail.widthProperty());
            
            FontIcon playIcon = new FontIcon("fth-play-circle");
            playIcon.setIconSize(32);
            playIcon.getStyleClass().add("accent");
            
            thumbnail.getChildren().addAll(imgView, playIcon);
        } else {
            FontIcon playIcon = new FontIcon("fth-play-circle");
            playIcon.setIconSize(48);
            playIcon.getStyleClass().add("accent");
            thumbnail.getChildren().add(playIcon);
        }
        
        Label title = new Label(post.getTitle() != null && !post.getTitle().isEmpty() ? post.getTitle() : "Başlıksız Video");
        title.getStyleClass().add("text-bold");
        title.setWrapText(true);
        title.setMinHeight(40);
        
        HBox statusBox = new HBox(10);
        statusBox.setAlignment(Pos.CENTER_LEFT);
        
        Label status = new Label(post.getStatus());
        status.getStyleClass().addAll("badge");
        if ("completed".equalsIgnoreCase(post.getStatus())) {
            status.getStyleClass().add("success");
        } else if ("failed".equalsIgnoreCase(post.getStatus())) {
            status.getStyleClass().add("danger");
        } else {
            status.getStyleClass().add("accent");
        }
        
        Label date = new Label(post.getCreatedAt());
        date.getStyleClass().addAll("text-muted", "text-small");
        
        statusBox.getChildren().addAll(status, date);
        
        card.getChildren().addAll(thumbnail, title, statusBox);
        
        // Hover effect
        card.setOnMouseEntered(e -> card.getStyleClass().add("elevated-2"));
        card.setOnMouseExited(e -> card.getStyleClass().remove("elevated-2"));
        
        // Click to play
        card.setOnMouseClicked(e -> showDetailView(post));
        
        return card;
    }

    private void showDetailView(Post post) {
        if (post.getVideoPath() == null || post.getVideoPath().isEmpty()) {
            System.err.println("Bu gönderinin videosu henüz hazır değil veya hatalı.");
            return;
        }

        // Görünümleri değiştir
        gridView.setVisible(false);
        gridView.setManaged(false);
        detailView.setVisible(true);
        detailView.setManaged(true);
        
        lblDetailTitle.setText(post.getTitle() != null && !post.getTitle().isEmpty() ? post.getTitle() : "Başlıksız Video");
        lblDetailDate.setText(post.getCreatedAt());

        playVideo(post);
    }

    @FXML
    private void hideDetailView() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.dispose();
            mediaPlayer = null;
        }
        
        detailView.setVisible(false);
        detailView.setManaged(false);
        gridView.setVisible(true);
        gridView.setManaged(true);
        
        placeholderBox.setVisible(true);
        playPauseIcon.setIconLiteral("fth-play");
    }

    private void playVideo(Post post) {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.dispose();
        }

        String baseUrl = ConfigManager.getInstance().getApiUrl();
        String videoPath = post.getVideoPath().replace("\\", "/");
        String fileName = videoPath.substring(videoPath.lastIndexOf("/") + 1);
        String videoUrl = baseUrl + "/stream/video/" + fileName;
        
        System.out.println("Playing video from stream API: " + videoUrl);

        try {
            Media media = new Media(URI.create(videoUrl).toString());
            mediaPlayer = new MediaPlayer(media);
            mediaView.setMediaPlayer(mediaPlayer);

            mediaView.fitHeightProperty().bind(videoContainer.heightProperty());
            mediaView.fitWidthProperty().bind(videoContainer.widthProperty());

            mediaPlayer.setOnReady(() -> {
                placeholderBox.setVisible(false);
                mediaPlayer.play();
                playPauseIcon.setIconLiteral("fth-pause");
                
                // Slider max değeri ayarla
                videoSlider.setMax(100);
            });
            
            mediaPlayer.currentTimeProperty().addListener((obs, oldTime, newTime) -> {
                if (!videoSlider.isValueChanging() && mediaPlayer.getTotalDuration().toSeconds() > 0) {
                    videoSlider.setValue((newTime.toSeconds() / mediaPlayer.getTotalDuration().toSeconds()) * 100);
                }
                lblVideoTime.setText(formatTime(newTime, mediaPlayer.getTotalDuration()));
            });

            videoSlider.valueChangingProperty().addListener((obs, wasChanging, isChanging) -> {
                if (!isChanging && mediaPlayer != null) {
                    mediaPlayer.seek(mediaPlayer.getTotalDuration().multiply(videoSlider.getValue() / 100.0));
                }
            });
            
            videoSlider.setOnMouseClicked(e -> {
                if (mediaPlayer != null) {
                    mediaPlayer.seek(mediaPlayer.getTotalDuration().multiply(videoSlider.getValue() / 100.0));
                }
            });
            
            mediaPlayer.setOnEndOfMedia(() -> {
                mediaPlayer.seek(mediaPlayer.getStartTime());
                mediaPlayer.pause();
                playPauseIcon.setIconLiteral("fth-play");
            });
            
        } catch (Exception e) {
            System.err.println("Video yüklenirken hata: " + e.getMessage());
        }
    }

    @FXML
    private void togglePlayPause() {
        if (mediaPlayer != null) {
            if (mediaPlayer.getStatus() == MediaPlayer.Status.PLAYING) {
                mediaPlayer.pause();
                playPauseIcon.setIconLiteral("fth-play");
            } else {
                mediaPlayer.play();
                playPauseIcon.setIconLiteral("fth-pause");
            }
        }
    }
    
    private String formatTime(Duration current, Duration total) {
        if (current == null || total == null || total.toSeconds() == 0) return "00:00 / 00:00";
        int curSec = (int) current.toSeconds();
        int totSec = (int) total.toSeconds();
        return String.format("%02d:%02d / %02d:%02d", curSec / 60, curSec % 60, totSec / 60, totSec % 60);
    }
}
