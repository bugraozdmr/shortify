package com.shortify.controllers;

import com.shortify.models.Post;
import com.shortify.utils.ConfigManager;
import com.shortify.utils.DateUtil;
import com.shortify.utils.ModalUtil;
import com.shortify.utils.PostService;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.Cursor;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.ComboBox;
import javafx.scene.control.CheckBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.control.TextArea;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.Region;
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
import java.util.List;

public class PostsController {

    // ── Grid View ──
    @FXML private VBox gridView;
    @FXML private FlowPane postsFlowPane;
    @FXML private VBox errorBox;
    @FXML private Label lblErrorMessage;
    
    @FXML private ComboBox<String> cmbStatusFilter;
    @FXML private ComboBox<String> cmbPublishFilter;
    @FXML private ComboBox<String> cmbSortFilter;
    @FXML private Button btnPrevPage;
    @FXML private Button btnNextPage;
    @FXML private Label lblPageInfo;
    
    @FXML private StackPane rootPane;
    
    // ── Detail View ──
    @FXML private ScrollPane detailScrollPane;
    @FXML private VBox detailView;
    @FXML private HBox contentArea;
    @FXML private VBox videoPanel;
    @FXML private Label lblDetailTitle;
    @FXML private Label lblDetailDate;
    
    // ── Form (her zaman görünür) ──
    @FXML private VBox editFormBox;
    @FXML private TextField txtYoutubeTitle;
    @FXML private TextArea txtYoutubeDesc;
    @FXML private TextField txtYoutubeTags;
    @FXML private CheckBox chkSchedule;
    @FXML private HBox scheduleBox;
    @FXML private DatePicker dpScheduleDate;
    @FXML private TextField txtScheduleTime;
    
    // ── Video ──
    @FXML private StackPane videoContainer;
    @FXML private MediaView mediaView;
    @FXML private VBox placeholderBox;
    @FXML private HBox controlsBox;
    @FXML private FontIcon playPauseIcon;
    @FXML private Slider videoSlider;
    @FXML private Label lblVideoTime;
    @FXML private Button btnPublish;
    @FXML private Button btnSave;
    @FXML private Button btnViewYoutube;

    private MediaPlayer mediaPlayer;
    private final PostService postService = new PostService();
    
    private Post currentPost;
    private int currentPage = 1;
    private final int itemsPerPage = 20;
    private int totalPages = 1;

    @FXML
    public void initialize() {
        detailView.setVisible(false);
        detailView.setManaged(false);
        gridView.setVisible(true);
        gridView.setManaged(true);
        
        // Shorts (vertical) video — max genişlik
        if (videoContainer != null) {
            videoContainer.setMaxWidth(420);
        }
        
        // ── Responsive: contentArea genişliğine göre layout değiştir ──
        if (contentArea != null) {
            contentArea.widthProperty().addListener((obs, oldVal, newVal) -> {
                double w = newVal.doubleValue();
                if (w < 700) {
                    // Küçük ekran: video tam genişlik, form alta geçer
                    contentArea.setSpacing(20);
                    if (editFormBox != null) {
                        editFormBox.setMinWidth(0);
                        editFormBox.setPrefWidth(Region.USE_COMPUTED_SIZE);
                        editFormBox.setMaxWidth(Double.MAX_VALUE);
                        HBox.setHgrow(editFormBox, Priority.ALWAYS);
                    }
                    if (videoPanel != null) {
                        videoPanel.setMaxWidth(Double.MAX_VALUE);
                    }
                } else {
                    // Büyük ekran: yan yana
                    contentArea.setSpacing(25);
                    if (editFormBox != null) {
                        editFormBox.setMinWidth(320);
                        editFormBox.setPrefWidth(380);
                        editFormBox.setMaxWidth(400);
                        HBox.setHgrow(editFormBox, Priority.NEVER);
                    }
                    if (videoPanel != null) {
                        videoPanel.setMaxWidth(Double.MAX_VALUE);
                    }
                }
            });
        }
        
        // ── Grid responsive ──
        postsFlowPane.widthProperty().addListener((obs, oldVal, newVal) -> {
            double width = newVal.doubleValue() - postsFlowPane.getPadding().getLeft() - postsFlowPane.getPadding().getRight();
            int columns = (int) (width / 260);
            if (columns <= 0) columns = 1;
            
            double gap = postsFlowPane.getHgap();
            double cardWidth = (width - ((columns - 1) * gap)) / columns;
            cardWidth = Math.floor(cardWidth) - 1;
            
            for (var child : postsFlowPane.getChildren()) {
                if (child instanceof VBox) {
                    VBox card = (VBox) child;
                    card.setPrefWidth(cardWidth);
                    card.setMinWidth(cardWidth);
                    card.setMaxWidth(cardWidth);
                }
            }
        });
        
        if (cmbStatusFilter != null) {
            cmbStatusFilter.getItems().addAll("Tümü", "completed", "failed", "processing", "pending");
            cmbStatusFilter.getSelectionModel().selectFirst();
            
            cmbPublishFilter.getItems().addAll("Tümü", "published", "unpublished");
            cmbPublishFilter.getSelectionModel().selectFirst();
            
            cmbSortFilter.getItems().addAll("En Yeni", "En Eski");
            cmbSortFilter.getSelectionModel().selectFirst();
        }
        
        if (chkSchedule != null) {
            chkSchedule.selectedProperty().addListener((obs, oldVal, newVal) -> {
                scheduleBox.setDisable(!newVal);
            });
            txtScheduleTime.textProperty().addListener((obs, oldText, newText) -> {
                if (newText != null && !newText.matches("\\d{0,2}:?\\d{0,2}")) {
                    txtScheduleTime.setText(oldText);
                }
            });
        }
        
        if (rootPane != null) {
            rootPane.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene == null) {
                    cleanupMediaPlayer();
                }
            });
        }
        
        com.shortify.utils.GlobalState.getInstance().refreshPostsTriggerProperty().addListener((obs, oldVal, newVal) -> {
            if (gridView != null && gridView.isVisible()) {
                loadPosts(); // Arka planda listeyi günceller
            }
        });
        
        loadPosts();
    }

    @FXML
    private void applyFilters() {
        currentPage = 1;
        loadPosts();
    }
    
    @FXML
    private void prevPage() {
        if (currentPage > 1) {
            currentPage--;
            loadPosts();
        }
    }
    
    @FXML
    private void nextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            loadPosts();
        }
    }
    
    private void updatePaginationUI() {
        if (lblPageInfo != null) {
            lblPageInfo.setText("Sayfa " + currentPage + " / " + totalPages);
            btnPrevPage.setDisable(currentPage <= 1);
            btnNextPage.setDisable(currentPage >= totalPages);
        }
    }

    @FXML
    private void loadPosts() {
        errorBox.setVisible(false);
        errorBox.setManaged(false);
        
        String status = "all";
        String publish = "all";
        String sort = "desc";
        
        if (cmbStatusFilter != null && cmbStatusFilter.getValue() != null) {
            status = cmbStatusFilter.getValue();
            if ("Tümü".equals(status)) status = "all";
        }
        
        if (cmbPublishFilter != null && cmbPublishFilter.getValue() != null) {
            publish = cmbPublishFilter.getValue();
            if ("Tümü".equals(publish)) publish = "all";
        }
        
        if (cmbSortFilter != null && cmbSortFilter.getValue() != null) {
            if ("En Eski".equals(cmbSortFilter.getValue())) sort = "asc";
        }
        
        int skip = (currentPage - 1) * itemsPerPage;
        
        postService.getPosts(skip, itemsPerPage, status, publish, sort).thenAccept(result -> {
            Platform.runLater(() -> {
                postsFlowPane.getChildren().clear();
                
                int totalItems = result.getTotal();
                totalPages = (int) Math.ceil((double) totalItems / itemsPerPage);
                if (totalPages == 0) totalPages = 1;
                
                updatePaginationUI();
                
                List<Post> posts = result.getItems();
                if (posts == null || posts.isEmpty()) {
                    lblErrorMessage.setText("Bu kriterlere uygun video bulunamadı.");
                    errorBox.setVisible(true);
                    errorBox.setManaged(true);
                } else {
                    for (Post post : posts) {
                        postsFlowPane.getChildren().add(createPostCard(post));
                    }
                    double currentWidth = postsFlowPane.getWidth();
                    if (currentWidth > 0) {
                        postsFlowPane.requestLayout();
                    }
                }
            });
        }).exceptionally(ex -> {
            Platform.runLater(() -> {
                postsFlowPane.getChildren().clear();
                lblErrorMessage.setText("Sunucuya bağlanılamadı. Lütfen bağlantınızı kontrol edin.");
                errorBox.setVisible(true);
                errorBox.setManaged(true);
            });
            ex.printStackTrace();
            return null;
        });
    }

    private VBox createPostCard(Post post) {
        VBox card = new VBox(10);
        card.getStyleClass().addAll("card", "elevated-1");
        card.setPrefWidth(260);
        card.setMinWidth(260);
        card.setMaxWidth(260);
        card.setCursor(Cursor.HAND);
        
        StackPane thumbnail = new StackPane();
        thumbnail.setPrefHeight(160);
        thumbnail.setStyle("-fx-background-color: #1a1a1a; -fx-background-radius: 8;");
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
            
            ImageView imgView = new ImageView(new Image(thumbUrl, true));
            imgView.setPreserveRatio(true);
            imgView.setFitHeight(160);
            imgView.setFitWidth(260);
            
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
        
        boolean isPublishedCard = "uploaded".equals(post.getYoutubeStatus()) || "published".equals(post.getYoutubeStatus());
        if (isPublishedCard) {
            status.setText("Yayınlandı");
            status.getStyleClass().add("danger"); // Kırmızı YouTube rengi gibi
        } else if ("completed".equalsIgnoreCase(post.getStatus())) {
            status.getStyleClass().add("success");
        } else if ("failed".equalsIgnoreCase(post.getStatus())) {
            status.getStyleClass().add("danger");
        } else {
            status.getStyleClass().add("accent");
        }
        
        Label date = new Label(DateUtil.toSmart(post.getCreatedAt()));
        date.getStyleClass().addAll("text-muted", "text-small");
        
        statusBox.getChildren().addAll(status, date);
        card.getChildren().addAll(thumbnail, title, statusBox);
        
        card.setOnMouseEntered(e -> card.getStyleClass().add("elevated-2"));
        card.setOnMouseExited(e -> card.getStyleClass().remove("elevated-2"));
        card.setOnMouseClicked(e -> showDetailView(post));
        
        return card;
    }

    private void showDetailView(Post post) {
        this.currentPost = post;
        
        gridView.setVisible(false);
        gridView.setManaged(false);
        detailView.setVisible(true);
        detailView.setManaged(true);
        detailScrollPane.setVvalue(0); // Kaydırma çubuğunu en başa al
        
        // Başlık + Tarih
        lblDetailTitle.setText(post.getTitle() != null && !post.getTitle().isEmpty() ? post.getTitle() : "Başlıksız Video");
        lblDetailDate.setText(DateUtil.toFull(post.getCreatedAt()));
        
        // Form alanlarını doldur (her zaman görünür)
        txtYoutubeTitle.setText(post.getYoutubeTitle() != null ? post.getYoutubeTitle() : post.getTitle());
        txtYoutubeDesc.setText(post.getYoutubeDescription() != null ? post.getYoutubeDescription() : "");
        txtYoutubeTags.setText(post.getYoutubeTags() != null ? post.getYoutubeTags() : "");

        if (post.getScheduledAt() != null && !post.getScheduledAt().isEmpty()) {
            chkSchedule.setSelected(true);
            java.time.LocalDateTime dt = DateUtil.parse(post.getScheduledAt());
            if (dt != null) {
                dt = dt.plusHours(3);
                dpScheduleDate.setValue(dt.toLocalDate());
                txtScheduleTime.setText(String.format("%02d:%02d", dt.getHour(), dt.getMinute()));
            } else {
                dpScheduleDate.setValue(null);
                txtScheduleTime.setText("");
            }
        } else {
            chkSchedule.setSelected(false);
            dpScheduleDate.setValue(null);
            txtScheduleTime.setText("");
        }

        if (post.getVideoPath() == null || post.getVideoPath().isEmpty()) {
            placeholderBox.setVisible(true);
            if (mediaPlayer != null) {
                mediaPlayer.stop();
                mediaPlayer.dispose();
                mediaPlayer = null;
                mediaView.setMediaPlayer(null);
            }
            controlsBox.setDisable(true);
            btnPublish.setDisable(true);
        } else {
            controlsBox.setDisable(false);
            btnPublish.setDisable(false);
            playVideo(post);
        }

        boolean isPublished = "uploaded".equals(post.getYoutubeStatus()) || "published".equals(post.getYoutubeStatus());
        
        btnPublish.setVisible(!isPublished);
        btnSave.setVisible(!isPublished);
        btnSave.setManaged(!isPublished);
        
        if (btnViewYoutube != null) {
            btnViewYoutube.setVisible(isPublished);
            btnViewYoutube.setManaged(isPublished);
        }
        
        txtYoutubeTitle.setEditable(!isPublished);
        txtYoutubeDesc.setEditable(!isPublished);
        txtYoutubeTags.setEditable(!isPublished);
        
        chkSchedule.setDisable(isPublished);
        dpScheduleDate.setDisable(isPublished);
        txtScheduleTime.setDisable(isPublished);
    }

    @FXML
    private void hideDetail() {
        cleanupMediaPlayer();
        
        this.currentPost = null;
        
        detailView.setVisible(false);
        detailView.setManaged(false);
        gridView.setVisible(true);
        gridView.setManaged(true);
    }

    @FXML
    private void deletePost() {
        if (currentPost == null) return;
        
        com.shortify.utils.ModalUtil.showConfirmModal(
            detailView.getScene().getWindow(),
            "Gönderiyi Sil",
            "Bu videoyu kalıcı olarak silmek istediğinize emin misiniz? Bu işlem geri alınamaz ve sunucudaki dosya da silinecektir.",
            "Evet, Sil",
            "İptal",
            "fth-alert-triangle",
            "#ef4444",
            "danger"
        ).thenAccept(confirmed -> {
            if (confirmed) {
                postService.deletePost(currentPost.getId()).thenAccept(success -> {
                    Platform.runLater(() -> {
                        if (success) {
                            hideDetail();
                            loadPosts();
                        } else {
                            showErrorAlert("Silme işlemi başarısız oldu. Sunucu ile bağlantı kurulamadı.");
                        }
                    });
                });
            }
        });
    }

    @FXML
    private void publishPost() {
        if (currentPost == null) return;
        
        btnPublish.setDisable(true);
        String originalText = btnPublish.getText();
        btnPublish.setText("Yayınlanıyor...");
        
        postService.publishPost(currentPost.getId()).thenAccept(success -> {
            Platform.runLater(() -> {
                btnPublish.setDisable(false);
                btnPublish.setText(originalText);
                if (success) {
                    currentPost.setYoutubeStatus("uploaded");
                    loadPosts();
                    showSuccessAlert("Video başarıyla YouTube'da yayınlandı!");
                } else {
                    showErrorAlert("Yayınlama işlemi başarısız oldu. Video dosyası bulunamamış olabilir.");
                }
            });
        });
    }

    private void cleanupMediaPlayer() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
            mediaPlayer.dispose();
            mediaPlayer = null;
        }
    }

    @FXML
    private void saveEdit() {
        if (currentPost == null) return;
        
        String ytTitle = txtYoutubeTitle.getText();
        String ytDesc = txtYoutubeDesc.getText();
        String ytTags = txtYoutubeTags.getText();
        
        String scheduledAt = null;
        if (chkSchedule.isSelected() && dpScheduleDate.getValue() != null) {
            String timeStr = txtScheduleTime.getText();
            if (timeStr == null || timeStr.trim().isEmpty()) {
                timeStr = "00:00";
            }
            if (!timeStr.contains(":")) {
                timeStr = timeStr + ":00";
            }
            try {
                java.time.LocalTime time = java.time.LocalTime.parse(timeStr);
                java.time.LocalDateTime dt = java.time.LocalDateTime.of(dpScheduleDate.getValue(), time);
                scheduledAt = dt.format(java.time.format.DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            } catch (Exception e) {
                showErrorAlert("Zamanlama saati formatı hatalı. Lütfen HH:mm (örn: 18:30) şeklinde girin.");
                return;
            }
        }
        
        final String finalScheduledAt = scheduledAt;
        
        postService.updatePost(currentPost.getId(), ytTitle, ytDesc, ytTags, scheduledAt).thenAccept(success -> {
            Platform.runLater(() -> {
                if (success) {
                    currentPost.setYoutubeTitle(ytTitle);
                    currentPost.setYoutubeDescription(ytDesc);
                    currentPost.setYoutubeTags(ytTags);
                    currentPost.setScheduledAt(finalScheduledAt);
                    lblDetailTitle.setText(ytTitle != null && !ytTitle.isEmpty() ? ytTitle : "Başlıksız Video");
                    showSuccessAlert("Değişiklikler kaydedildi!");
                    loadPosts(); // Refresh list to show updated date if needed
                } else {
                    showErrorAlert("Kaydetme işlemi başarısız oldu. Lütfen arka plan sunucusunun açık olduğundan emin olun.");
                }
            });
        });
    }
    
    private void showErrorAlert(String message) {
        javafx.stage.Window owner = detailView.getScene() != null ? detailView.getScene().getWindow() : null;
        ModalUtil.showError(owner, "Hata", message);
    }
    
    private void showSuccessAlert(String message) {
        javafx.stage.Window owner = detailView.getScene() != null ? detailView.getScene().getWindow() : null;
        ModalUtil.showSuccess(owner, "Başarılı", message);
    }
    
    @FXML
    private void openYoutube() {
        if (currentPost != null && currentPost.getYoutubeUrl() != null && !currentPost.getYoutubeUrl().isEmpty()) {
            try {
                java.awt.Desktop.getDesktop().browse(new java.net.URI(currentPost.getYoutubeUrl()));
            } catch (Exception e) {
                showErrorAlert("YouTube bağlantısı açılamadı: " + e.getMessage());
            }
        } else {
            showErrorAlert("Bu video için YouTube bağlantısı bulunamadı.");
        }
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
                videoSlider.setMax(100);
            });
            
            mediaPlayer.currentTimeProperty().addListener((obs, oldTime, newTime) -> {
                if (mediaPlayer != null) {
                    if (!videoSlider.isValueChanging() && mediaPlayer.getTotalDuration().toSeconds() > 0) {
                        videoSlider.setValue((newTime.toSeconds() / mediaPlayer.getTotalDuration().toSeconds()) * 100);
                    }
                    lblVideoTime.setText(formatTime(newTime, mediaPlayer.getTotalDuration()));
                }
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
