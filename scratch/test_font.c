#include <stdio.h>
#include <math.h>

int main() {
    // 'T' character bitmap
    unsigned char t_data[8] = {0x7E, 0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00};
    int CHAR_SIZE = 64;

    for (int Y = 0; Y < CHAR_SIZE; Y += 4) { // Print every 4th line
        for (int X = 0; X < CHAR_SIZE; X += 4) { // Print every 4th char
            float py = ((Y + 0.5f) / CHAR_SIZE) * 8.0f;
            float px = ((X + 0.5f) / CHAR_SIZE) * 8.0f;

            int grid_x = (int)floorf(px);
            int grid_y = (int)floorf(py);
            if (grid_x < 0) grid_x = 0; if (grid_x > 7) grid_x = 7;
            if (grid_y < 0) grid_y = 0; if (grid_y > 7) grid_y = 7;
            int is_solid = ((t_data[grid_y] >> (7 - grid_x)) & 1);

            float min_dist = 999.0f;
            for (int gy = 0; gy < 8; gy++) {
                for (int gx = 0; gx < 8; gx++) {
                    int target_solid = ((t_data[gy] >> (7 - gx)) & 1);
                    if (target_solid != is_solid) {
                        float dx = px - (gx + 0.5f);
                        float dy = py - (gy + 0.5f);
                        float dist = sqrtf(dx * dx + dy * dy);
                        if (dist < min_dist) {
                            min_dist = dist;
                        }
                    }
                }
            }

            if (min_dist > 99.0f) min_dist = 8.0f;
            float sd = is_solid ? min_dist : -min_dist;

            float threshold = 0.0f;
            float transition = 0.65f;
            float alpha_f = (sd - (threshold - transition)) / (2.0f * transition);
            if (alpha_f < 0.0f) alpha_f = 0.0f;
            if (alpha_f > 1.0f) alpha_f = 1.0f;

            alpha_f = alpha_f * alpha_f * (3.0f - 2.0f * alpha_f);
            int alpha = (int)(255.0f * alpha_f);
            
            if (alpha == 0) {
                printf(".");
            } else if (alpha == 255) {
                printf("#");
            } else {
                printf("+"); // Semi-transparent pixels
            }
        }
        printf("\n");
    }
    return 0;
}
