#pragma once

#include "protocol/Command.hpp"

class CommandParser {
public:
    static bool parse(const char *line, Command *out);

private:
    static bool parse_axis_token(const char *value, AxisId *out);
    static bool parse_float_token(const char *value, float *out);
    static bool parse_key_value_token(const char *token, const char *key, const char **value_out);
    static bool parse_jog(const char *line, Command *out);
    static bool parse_move4(const char *line, Command *out);
};
