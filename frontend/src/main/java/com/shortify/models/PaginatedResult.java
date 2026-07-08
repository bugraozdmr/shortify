package com.shortify.models;

import java.util.List;

public class PaginatedResult<T> {
    private final int total;
    private final List<T> items;

    public PaginatedResult(int total, List<T> items) {
        this.total = total;
        this.items = items;
    }

    public int getTotal() {
        return total;
    }

    public List<T> getItems() {
        return items;
    }
}
