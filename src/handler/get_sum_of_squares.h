#pragma once

#include "../commands.h"

// TODO: docs

typedef struct {
    uint32_t sum;
    uint16_t i;
    uint8_t n;
} get_sum_of_squares_state_t;

void handler_get_sum_of_squares(
    uint8_t p1,
    uint8_t p2,
    uint8_t lc,
    dispatcher_context_t *dispatcher_context
);