#include "protocol/CommandParser.hpp"

#include <stdlib.h>
#include <string.h>

bool CommandParser::parse_axis_token(const char *value, AxisId *out)
{
    if (strcmp(value, "XL") == 0) {
        *out = AxisId::XL;
        return true;
    }
    if (strcmp(value, "YL") == 0) {
        *out = AxisId::YL;
        return true;
    }
    if (strcmp(value, "XR") == 0) {
        *out = AxisId::XR;
        return true;
    }
    if (strcmp(value, "YR") == 0) {
        *out = AxisId::YR;
        return true;
    }

    return false;
}

bool CommandParser::parse_float_token(const char *value, float *out)
{
    if (value == nullptr || *value == '\0') {
        return false;
    }

    char *end = nullptr;
    const float parsed = strtof(value, &end);
    if (end == value || *end != '\0') {
        return false;
    }

    *out = parsed;
    return true;
}

bool CommandParser::parse_key_value_token(const char *token, const char *key, const char **value_out)
{
    const size_t key_length = strlen(key);
    if (strncmp(token, key, key_length) != 0 || token[key_length] != '=') {
        return false;
    }

    *value_out = token + key_length + 1;
    return **value_out != '\0';
}

bool CommandParser::parse_jog(const char *line, Command *out)
{
    if (strncmp(line, "JOG", 3) != 0) {
        return false;
    }

    const char *cursor = line + 3;
    while (*cursor == ' ') {
        ++cursor;
    }

    bool have_axis = false;
    bool have_dist = false;
    bool have_feedrate = false;

    JogCommand jog = {};

    while (*cursor != '\0') {
        while (*cursor == ' ') {
            ++cursor;
        }

        if (*cursor == '\0') {
            break;
        }

        const char *token_start = cursor;
        while (*cursor != '\0' && *cursor != ' ') {
            ++cursor;
        }

        const size_t token_length = static_cast<size_t>(cursor - token_start);
        char token[32] = {};
        if (token_length >= sizeof(token)) {
            return false;
        }
        memcpy(token, token_start, token_length);

        const char *value = nullptr;
        if (parse_key_value_token(token, "AXIS", &value)) {
            if (have_axis || !parse_axis_token(value, &jog.axis)) {
                return false;
            }
            have_axis = true;
            continue;
        }

        if (parse_key_value_token(token, "DIST", &value)) {
            if (have_dist || !parse_float_token(value, &jog.distance_mm)) {
                return false;
            }
            have_dist = true;
            continue;
        }

        if (parse_key_value_token(token, "F", &value)) {
            if (have_feedrate || !parse_float_token(value, &jog.feedrate_mm_min)) {
                return false;
            }
            have_feedrate = true;
            continue;
        }

        return false;
    }

    if (!have_axis || !have_dist || !have_feedrate) {
        return false;
    }

    out->type = CommandType::Jog;
    out->data.jog = jog;
    return true;
}

bool CommandParser::parse_move4(const char *line, Command *out)
{
    if (strncmp(line, "MOVE4", 5) != 0) {
        return false;
    }

    const char *cursor = line + 5;
    while (*cursor == ' ') {
        ++cursor;
    }

    bool have_xl = false;
    bool have_yl = false;
    bool have_xr = false;
    bool have_yr = false;
    bool have_feedrate = false;

    Move4Command move4 = {};

    while (*cursor != '\0') {
        while (*cursor == ' ') {
            ++cursor;
        }

        if (*cursor == '\0') {
            break;
        }

        const char *token_start = cursor;
        while (*cursor != '\0' && *cursor != ' ') {
            ++cursor;
        }

        const size_t token_length = static_cast<size_t>(cursor - token_start);
        char token[32] = {};
        if (token_length >= sizeof(token)) {
            return false;
        }
        memcpy(token, token_start, token_length);

        const char *value = nullptr;
        if (parse_key_value_token(token, "XL", &value)) {
            if (have_xl || !parse_float_token(value, &move4.xl_mm)) {
                return false;
            }
            have_xl = true;
            continue;
        }

        if (parse_key_value_token(token, "YL", &value)) {
            if (have_yl || !parse_float_token(value, &move4.yl_mm)) {
                return false;
            }
            have_yl = true;
            continue;
        }

        if (parse_key_value_token(token, "XR", &value)) {
            if (have_xr || !parse_float_token(value, &move4.xr_mm)) {
                return false;
            }
            have_xr = true;
            continue;
        }

        if (parse_key_value_token(token, "YR", &value)) {
            if (have_yr || !parse_float_token(value, &move4.yr_mm)) {
                return false;
            }
            have_yr = true;
            continue;
        }

        if (parse_key_value_token(token, "F", &value)) {
            if (have_feedrate || !parse_float_token(value, &move4.feedrate_mm_min)) {
                return false;
            }
            have_feedrate = true;
            continue;
        }

        return false;
    }

    if (!have_xl || !have_yl || !have_xr || !have_yr || !have_feedrate) {
        return false;
    }

    out->type = CommandType::Move4;
    out->data.move4 = move4;
    return true;
}

bool CommandParser::parse(const char *line, Command *out)
{
    if (line == nullptr || out == nullptr) {
        return false;
    }

    if (strcmp(line, "HELLO") == 0) {
        out->type = CommandType::Hello;
        return true;
    }

    if (strcmp(line, "STATUS?") == 0) {
        out->type = CommandType::Status;
        return true;
    }

    if (strcmp(line, "SET_ZERO") == 0) {
        out->type = CommandType::SetZero;
        return true;
    }

    if (parse_jog(line, out)) {
        return true;
    }

    return parse_move4(line, out);
}
