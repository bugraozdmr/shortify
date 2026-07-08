package com.shortify.utils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.Locale;

/**
 * Uygulama genelinde tarih formatlama ve dönüştürme işlemleri.
 * ISO formatındaki tarihleri okunabilir Türkçe metinlere çevirir.
 */
public class DateUtil {

    private static final Locale TR = new Locale("tr", "TR");
    
    private static final DateTimeFormatter ISO_PARSER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
    private static final DateTimeFormatter FULL_FORMAT = DateTimeFormatter.ofPattern("d MMMM yyyy, HH:mm", TR);
    private static final DateTimeFormatter SHORT_FORMAT = DateTimeFormatter.ofPattern("d MMM yyyy", TR);
    private static final DateTimeFormatter DATE_ONLY = DateTimeFormatter.ofPattern("d MMMM yyyy", TR);
    private static final DateTimeFormatter TIME_ONLY = DateTimeFormatter.ofPattern("HH:mm", TR);

    /**
     * ISO tarihini "7 Temmuz 2026, 15:05" formatına çevirir.
     */
    public static String toFull(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        return dt.format(FULL_FORMAT);
    }

    /**
     * ISO tarihini "7 Tem 2026" formatına çevirir.
     */
    public static String toShort(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        return dt.format(SHORT_FORMAT);
    }

    /**
     * ISO tarihini "7 Temmuz 2026" formatına çevirir.
     */
    public static String toDateOnly(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        return dt.format(DATE_ONLY);
    }

    /**
     * ISO tarihini "15:05" formatına çevirir.
     */
    public static String toTimeOnly(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        return dt.format(TIME_ONLY);
    }

    /**
     * ISO tarihini "2 saat önce", "3 gün önce" gibi göreli metne çevirir.
     */
    public static String toRelative(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        
        LocalDateTime now = LocalDateTime.now();
        long seconds = ChronoUnit.SECONDS.between(dt, now);
        
        if (seconds < 0) return "az sonra";
        if (seconds < 60) return "az önce";
        
        long minutes = ChronoUnit.MINUTES.between(dt, now);
        if (minutes < 60) return minutes + " dakika önce";
        
        long hours = ChronoUnit.HOURS.between(dt, now);
        if (hours < 24) return hours + " saat önce";
        
        long days = ChronoUnit.DAYS.between(dt, now);
        if (days == 1) return "dün";
        if (days < 7) return days + " gün önce";
        if (days < 30) return (days / 7) + " hafta önce";
        if (days < 365) return (days / 30) + " ay önce";
        
        return (days / 365) + " yıl önce";
    }

    /**
     * ISO tarihini akıllıca formatlar:
     * - Bugün ise: "Bugün, 15:05"
     * - Dün ise: "Dün, 15:05"
     * - Bu yıl ise: "7 Temmuz, 15:05"
     * - Eski ise: "7 Temmuz 2025"
     */
    public static String toSmart(String isoDate) {
        LocalDateTime dt = parse(isoDate);
        if (dt == null) return isoDate;
        
        LocalDateTime now = LocalDateTime.now();
        long days = ChronoUnit.DAYS.between(dt.toLocalDate(), now.toLocalDate());
        
        if (days == 0) {
            return "Bugün, " + dt.format(TIME_ONLY);
        } else if (days == 1) {
            return "Dün, " + dt.format(TIME_ONLY);
        } else if (dt.getYear() == now.getYear()) {
            return dt.format(DateTimeFormatter.ofPattern("d MMMM, HH:mm", TR));
        } else {
            return dt.format(DATE_ONLY);
        }
    }

    /**
     * ISO string'i LocalDateTime'a parse eder. Hata durumunda null döner.
     */
    public static LocalDateTime parse(String isoDate) {
        if (isoDate == null || isoDate.isEmpty()) return null;
        try {
            return LocalDateTime.parse(isoDate, ISO_PARSER);
        } catch (Exception e) {
            // Farklı formatları da dene
            try {
                return LocalDateTime.parse(isoDate.replace(" ", "T"), ISO_PARSER);
            } catch (Exception ex) {
                return null;
            }
        }
    }
}
